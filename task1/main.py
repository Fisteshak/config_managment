import os
import tarfile
import json
import tkinter as tk
from tkinter import scrolledtext
import platform

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

user_name = config['user_name']
computer_name = config['computer_name']
path = config['path']

filename_without_extension = os.path.splitext(os.path.basename(path))[0]

# Extract filesystem
base_dir = os.path.dirname(os.path.abspath(__file__))
with tarfile.open(path, 'r') as tar:
    tar.extractall(path=base_dir)

# Set the root folder
extracted_dir = os.path.join(base_dir, filename_without_extension)
current_dir = extracted_dir

# Initialize Tkinter
root = tk.Tk()
root.title(f"{user_name}@{computer_name}")

console = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 12), bg="purple", fg="chartreuse1")
console.pack(fill=tk.BOTH, expand=True)
relative_dir = ''

def execute_command(event):
    global current_dir, path
    # Get the last line of the console
    last_line = console.get("end-2c linestart", "end-1c").strip()
    # Extract the command part after the last prompt
    command = last_line.split('$', 1)[-1].strip()
    console.insert(tk.END, "\n")

    if command.startswith("cd "):
        path = command[3:].strip()
        new_dir = os.path.abspath(os.path.join(current_dir, path))
        if new_dir.startswith(extracted_dir) and os.path.isdir(new_dir):
            current_dir = new_dir
        else:
            console.insert(tk.END, f"cd: no such file or directory\n")
    elif command == "ls":
        try:
            files = os.listdir(current_dir)
            console.insert(tk.END, "\n".join(files) + "\n")
        except Exception as e:
            console.insert(tk.END, f"Error: {str(e)}\n")

    elif command.startswith("cat "):
        file_path = os.path.join(current_dir, command[4:].strip())
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                console.insert(tk.END, file.read() + "\n")
        else:
            console.insert(tk.END, f"cat: {file_path}: No such file\n")
    elif command == "uname":
        console.insert(tk.END, platform.system() + "\n")
    elif command.startswith("rmdir "):
        dir_path = os.path.join(current_dir, command[6:].strip())
        if os.path.isdir(dir_path):
            try:
                os.rmdir(dir_path)
                #console.insert(tk.END, f"rmdir: {dir_path} removed\n")
            except Exception as e:
                console.insert(tk.END, f"rmdir: {str(e)}\n")
        else:
            console.insert(tk.END, f"rmdir: {dir_path}: No such directory\n")
    elif command == "exit":
        add_to_tar(path, extracted_dir)
        root.quit()

    display_prompt()

def add_to_tar(tar_path, dir_to_add):
    #
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(dir_to_add, arcname=os.path.basename(dir_to_add))


def display_prompt():
    relative_dir = os.path.relpath(current_dir, extracted_dir)
    relative_dir = relative_dir.replace("\\", "/")
    console.insert(tk.END, f"{user_name}@{computer_name}:/{relative_dir if relative_dir != '.' else ''}$ ")
    console.see(tk.END)

console.bind("<Return>", execute_command)
display_prompt()

root.mainloop()