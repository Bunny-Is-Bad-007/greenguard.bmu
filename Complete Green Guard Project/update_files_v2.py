# created by Mushfiq
# created by Mushfiq
import os
import time
import subprocess

repo_path = '.'
comment = '# created by Mushfiq\n'

# Initialize Git repository if not already initialized
if not os.path.exists(os.path.join(repo_path, '.git')):
    subprocess.run(['git', 'init'], cwd=repo_path)

# Check if remote origin already exists
try:
    subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/Bunny-Is-Bad-007/Haxked3.0.git'], cwd=repo_path, check=True)
except subprocess.CalledProcessError:
    pass  # Remote already exists

for subdir, _, files in os.walk(repo_path):
    for file in files:
        file_path = os.path.join(subdir, file)
        if file_path.endswith(".py") or file_path.endswith(".ts") or file_path.endswith(".css"):
            with open(file_path, 'r+', encoding='utf-8') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(comment + content)
            
            # Update the file modification time
            os.utime(file_path, (time.time(), time.time()))

# Stage all changes
subprocess.run(['git', 'add', '.'], cwd=repo_path)

# Commit changes
subprocess.run(['git', 'commit', '-m', 'Add local folder content'], cwd=repo_path)

# Pull from GitHub to integrate changes
subprocess.run(['git', 'pull', 'origin', 'main'], cwd=repo_path)

# Push to GitHub
subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=repo_path)

print("All files updated and pushed to GitHub successfully.")
