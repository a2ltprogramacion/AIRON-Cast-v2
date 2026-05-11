#!/usr/bin/env python3
# agents/agent_forge/scripts/check_vram.py
# La Forja — VRAM availability check for index rebuild
# Version: 1.0 — BL.030

import sys
import subprocess
import json
import urllib.request
import urllib.error


def check_vram_available(min_vram_mb=1500):
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.free,memory.used",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return {"ok": False, "total_mb": 0, "free_mb": 0, "used_mb": 0,
                    "min_required_mb": min_vram_mb,
                    "error": f"nvidia-smi error: {result.stderr.strip()}"}

        parts = result.stdout.strip().split(",")
        total, free, used = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
        ok = free >= min_vram_mb
        return {"ok": ok, "total_mb": total, "free_mb": free, "used_mb": used,
                "min_required_mb": min_vram_mb,
                "error": None if ok else
                         f"Insufficient VRAM: {free}MB free, {min_vram_mb}MB required. "
                         f"Unload LM Studio model before rebuild."}

    except FileNotFoundError:
        return {"ok": True, "total_mb": 0, "free_mb": 0, "used_mb": 0,
                "min_required_mb": min_vram_mb,
                "error": "nvidia-smi not found — embeddings will run on CPU (slower)"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "nvidia-smi timed out",
                "total_mb": 0, "free_mb": 0, "used_mb": 0, "min_required_mb": min_vram_mb}
    except Exception as e:
        return {"ok": False, "error": str(e),
                "total_mb": 0, "free_mb": 0, "used_mb": 0, "min_required_mb": min_vram_mb}


def check_lm_studio_unloaded(base_url="http://localhost:1234"):
    try:
        req = urllib.request.Request(f"{base_url}/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data   = json.loads(resp.read().decode())
            models = data.get("data", [])
            loaded = len(models) > 0
            return {"ok": not loaded, "lm_studio_up": True,
                    "models_loaded": [m["id"] for m in models],
                    "error": (f"LM Studio has {len(models)} model(s) loaded. "
                              f"Unload before rebuild.") if loaded else None}
    except urllib.error.URLError:
        return {"ok": True, "lm_studio_up": False, "models_loaded": [], "error": None}
    except Exception as e:
        return {"ok": False, "lm_studio_up": False, "models_loaded": [], "error": str(e)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_vram_mb", type=int, default=1500)
    parser.add_argument("--base_url",    default="http://localhost:1234")
    args = parser.parse_args()

    print("\n[ VRAM Check for Index Rebuild ]\n")

    vram = check_vram_available(args.min_vram_mb)
    print(f"  [{'OK  ' if vram['ok'] else 'WARN'}] "
          f"VRAM: {vram['free_mb']}MB free / {vram['total_mb']}MB total "
          f"(required: {vram['min_required_mb']}MB)")
    if vram["error"] and not vram["ok"]:
        print(f"         {vram['error']}")

    lms = check_lm_studio_unloaded(args.base_url)
    print(f"  [{'OK  ' if lms['ok'] else 'WARN'}] "
          f"LM Studio: {'not running' if not lms['lm_studio_up'] else 'running'} — "
          f"models: {lms['models_loaded'] or 'none'}")
    if lms["error"]:
        print(f"         {lms['error']}")

    overall = vram["ok"] and lms["ok"]
    print(f"\n  Rebuild safe to proceed: {'YES' if overall else 'NO'}\n")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
