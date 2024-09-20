import os
import tarfile
import json


# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

user_name = config['user_name']
computer_name = config['computer_name']
path = config['path']

filename_without_extension = os.path.splitext(os.path.basename(path))[0]

# Extract filesystem in the same directory as main.py
base_dir = os.path.dirname(os.path.abspath(__file__))
with tarfile.open(path, 'r') as tar:
    tar.extractall(path=base_dir)

print(base_dir, path)