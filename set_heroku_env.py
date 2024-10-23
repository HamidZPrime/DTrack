import os

# Read the .env file
with open('.env') as f:
    lines = f.read().splitlines()

# Prepare the heroku command
cmd = 'heroku config:set '

for line in lines:
    # Skip empty lines and comments
    if not line.strip() or line.startswith('#'):
        continue
    key, value = line.split('=', 1)
    # Add each key-value pair to the command
    cmd += f'{key}="{value}" '

# Add the app name
cmd += '--app dtrack'

# Execute the command
os.system(cmd)

