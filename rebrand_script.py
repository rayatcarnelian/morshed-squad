
import os
import re

def rebrand_content(content):
    # 1. Replace package names in imports
    # Handle "from crewai" -> "from morshed_squad"
    content = re.sub(r'from crewai(\s|\.)', r'from morshed_squad\1', content)
    content = re.sub(r'import crewai\b', r'import morshed_squad', content)
    
    # Handle "from crewai_files" -> "from morshed_squad_files"
    content = re.sub(r'from crewai_files(\s|\.)', r'from morshed_squad_files\1', content)
    content = re.sub(r'import crewai_files\b', r'import morshed_squad_files', content)
    
    # 2. Replace 'crewai_tools'
    content = content.replace('crewai_tools', 'morshed_squad_tools')
    content = content.replace('crewai-tools', 'morshed_squad_tools')
    content = content.replace('crewai-files', 'morshed_squad_files') 

    # 3. Replace 'crewai.' usage (e.g. crewai.Agent)
    # Be careful not to replace crewai.com
    # Match 'crewai.' where not preceded by dot or slash (url)
    content = re.sub(r'(?<![\./])\bcrewai\.', 'morshed_squad.', content)
    
    # 4. Replace string references "crewai" -> "morshed_squad" (common in setup.py or configs)
    # Matches "crewai" or 'crewai'
    content = re.sub(r'[\"\']crewai[\"\']', '"morshed_squad"', content)
    content = re.sub(r'[\"\']crewai-files[\"\']', '"morshed_squad_files"', content)
    
    # 5. Branding text "CrewAI" -> "Morshed Squad"
    content = content.replace('CrewAI', 'Morshed Squad')
    
    return content

def main():
    root_dirs = [
        'lib'
    ]
    
    extensions = ['.py', '.toml', '.md', '.rst']
    
    root_path = os.getcwd() # Should be e:/Morshed Squad/crewAI-main
    
    for relative_root in root_dirs:
        full_root = os.path.join(root_path, relative_root)
        if not os.path.exists(full_root):
            print(f"Skipping {full_root} (not found)")
            continue
            
        print(f"Processing {full_root}...")
        for subdir, dirs, files in os.walk(full_root):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(subdir, file)
                    # Skip the script itself if in target
                    if 'rebrand_script.py' in filepath: 
                        continue
                        
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        new_content = rebrand_content(content)
                        
                        if new_content != content:
                            print(f"Updating {filepath}")
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()
