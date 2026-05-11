import os
import zipfile
import sys

def package_skill(skill_path):
    skill_name = os.path.basename(os.path.normpath(skill_path))
    output_filename = f"{skill_name}.skill.zip"
    
    ignore_dirs = {'.git', '__pycache__', '.pytest_cache'}
    ignore_files = {'.DS_Store', output_filename}
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # Mutate dirs in-place to avoid walking ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file in ignore_files or file.endswith('.bak'):
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, skill_path)
                zipf.write(abs_path, rel_path)
    
    print(f"Skill packaged successfully: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path>")
        sys.exit(1)
    package_skill(sys.argv[1])
