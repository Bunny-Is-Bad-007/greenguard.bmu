# created by Mushfiq
import os
import time

repo_path = '.'
comment = '# created by Mushfiq\n'

for subdir, _, files in os.walk(repo_path):
    for file in files:
        file_path = os.path.join(subdir, file)
        if file_path.endswith(".py") or file_path.endswith(".ts") or file_path.endswith(".css"):
            with open(file_path, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(comment + content)
            
            # Update the file modification time
            os.utime(file_path, (time.time(), time.time()))

print("All files updated successfully.")
