import os
import subprocess

# Read the .env file
with open('.env') as f:
    lines = f.read().splitlines()

# Prepare commands
commands = []

for line in lines:
    # Skip empty lines and comments
    if not line.strip() or line.startswith('#'):
        continue
    try:
        key, value = line.split('=', 1)
        # Add each key-value pair as a separate command
        commands.append(f'heroku config:set {key}="{value}" --app dtrack')
    except ValueError:
        print(f"Skipping invalid line: {line}")

# Execute each command separately to avoid issues with command length
for cmd in commands:
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)
