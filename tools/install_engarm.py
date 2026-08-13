#!/usr/bin/env python3
"""
Install Engram — OpenCode ⊕ AIRON-Cast Fusion
Instala Engram (Go binary) via gentle-ai o descarga directa.
"""
import subprocess
import sys
import os
import platform
import urllib.request
from pathlib import Path

def install_engarm_via_gentle_ai():
    """Intenta instalar via gentle-ai (recomendado)."""
    print("Intentando instalar Engram via gentle-ai...")
    try:
        # Verificar si gentle-ai está disponible
        result = subprocess.run(["gentle-ai", "--version"], capture_output=True)
        if result.returncode == 0:
            subprocess.run(["gentle-ai", "install", "--component", "engram", "--agent", "opencode"], check=True)
            print("✓ Engram instalado via gentle-ai")
            return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return False

def install_engarm_direct():
    """Descarga binario Engram directo desde GitHub releases."""
    print("Descargando Engram binario...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Mapear arquitectura
    if arch in ("x86_64", "amd64"):
        arch = "amd64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        print(f"Arquitectura no soportada: {arch}")
        return False
    
    # URL pattern: https://github.com/Gentleman-Programming/engram/releases/download/v{X.Y.Z}/engram_{OS}_{ARCH}
    # Usar latest release
    try:
        # Obtener latest release
        import json
        with urllib.request.urlopen("https://api.github.com/repos/Gentleman-Programming/engram/releases/latest") as resp:
            release = json.load(resp)
        
        version = release["tag_name"]
        print(f"Última versión: {version}")
        
        # Buscar asset para nuestra plataforma
        asset_name = f"engram_{system}_{arch}"
        if system == "windows":
            asset_name += ".exe"
        
        asset_url = None
        for asset in release["assets"]:
            if asset["name"] == asset_name:
                asset_url = asset["browser_download_url"]
                break
        
        if not asset_url:
            print(f"No se encontró asset para {asset_name}")
            return False
        
        # Descargar
        dest = Path.home() / ".local" / "bin" / ("engram.exe" if system == "windows" else "engram")
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Descargando desde {asset_url}...")
        urllib.request.urlretrieve(asset_url, dest)
        
        # Hacer ejecutable en Unix
        if system != "windows":
            dest.chmod(0o755)
        
        # Añadir al PATH si no está
        bin_dir = dest.parent
        path_env = os.environ.get("PATH", "")
        if str(bin_dir) not in path_env:
            print(f"⚠ Añade {bin_dir} a tu PATH:")
            if system == "windows":
                print(f"  setx PATH \"%PATH%;{bin_dir}\"")
            else:
                print(f"  export PATH=\"$PATH:{bin_dir}\"")
        
        print(f"✓ Engram instalado en {dest}")
        return True
        
    except Exception as e:
        print(f"Error descargando Engram: {e}")
        return False

def verify_installation():
    """Verifica que Engram funciona."""
    try:
        result = subprocess.run(["engram", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Engram verificado: {result.stdout.strip()}")
            return True
    except:
        pass
    print("✗ Engram no funciona correctamente")
    return False

def main():
    print("=" * 60)
    print("  Instalador Engram — OpenCode + AIRON-Cast Fusion")
    print("=" * 60)
    print()
    
    # 1. Intentar via gentle-ai
    if install_engarm_via_gentle_ai():
        if verify_installation():
            return 0
    
    # 2. Fallback: descarga directa
    if install_engarm_direct():
        if verify_installation():
            return 0
    
    print()
    print("Instalación fallida. Opciones manuales:")
    print("  1. Instala Go y compila: go install github.com/Gentleman-Programming/engram@latest")
    print("  2. Descarga release: https://github.com/Gentleman-Programming/engram/releases")
    print("  3. Usa gentle-ai: pip install gentle-ai && gentle-ai install --component engram")
    return 1

if __name__ == "__main__":
    sys.exit(main())