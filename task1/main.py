import os
import tarfile
import json
import tkinter as tk
from tkinter import scrolledtext
import platform
import subprocess
import os

class CommandProcessor:
    def __init__(self, user_name, computer_name, path):
        self.user_name = user_name
        self.computer_name = computer_name
        self.path = path

        self.filename_without_extension = os.path.splitext(os.path.basename(self.path))[0]

        # Open the tarfile
        self.tar = tarfile.open(self.path, 'r')

        # Set the root folder
        self.current_dir = self.filename_without_extension

    def cd(self, path):
        new_dir = os.path.normpath(os.path.join(self.current_dir, path))
        new_dir = new_dir.replace("\\", "/")  # Ensure consistent path format
        if any(member.name.rstrip('/') == new_dir and member.isdir() for member in self.tar.getmembers()):
            self.current_dir = new_dir
            return ""
        else:
            return "cd: no such file or directory\n"

    def ls(self):
        try:
            current_dir_prefix = self.current_dir.rstrip('/') + '/'
            files = [
                member.name[len(current_dir_prefix):].split('/')[0]
                for member in self.tar.getmembers()
                if member.name.startswith(current_dir_prefix) and member.name != current_dir_prefix
            ]
            return "\n".join(sorted(set(files))) + "\n"
        except Exception as e:
            return f"Error: {str(e)}\n"

    def cat(self, file_path):
        full_path = os.path.normpath(os.path.join(self.current_dir, file_path))
        full_path = full_path.replace("\\", "/")  # Ensure consistent path format
        try:
            member = self.tar.getmember(full_path)
            if member.isfile():
                file = self.tar.extractfile(member)
                return file.read().decode() + "\n"
            else:
                return f"cat: {file_path}: No such file\n"
        except KeyError:
            return f"cat: {file_path}: No such file\n"

    def uname(self):
        return platform.system() + "\n"


    def rmdir(self, dir_path):
        full_path = os.path.normpath(os.path.join(self.current_dir, dir_path))
        full_path = full_path.replace("\\", "/")
        self_path = self.path.replace("\\", "/")
        
        # Check if directory exists in the archive
        try:
            dir_exists = False
            for member in self.tar.getmembers():
                if member.name.startswith(full_path) and member.isdir():
                    dir_exists = True
                    break
                    
            if not dir_exists:
                return f"rmdir: {dir_path}: No such directory\n"
                
            # Close the tar archive
            self.tar.close()
            
            # Use 7z to delete the directory from the archive  
            command = f'7z d "{self_path}" "{full_path}"'
            result = os.system(command)
            
            # Reopen the tar archive
            self.tar = tarfile.open(self.path, 'r')
            
            if result == 0:
                return f"Directory {dir_path} removed successfully\n"
            else:
                return f"Error removing directory {dir_path}\n"
                
        except Exception as e:
            return f"Error: {str(e)}\n"

    def exit(self):
        self.tar.close()
        return ""

    def get_prompt(self):
        relative_dir = os.path.relpath(self.current_dir, self.filename_without_extension)
        relative_dir = relative_dir.replace("\\", "/")
        return f"{self.user_name}@{self.computer_name}:/{relative_dir if relative_dir != '.' else ''}$ "

class TerminalApp:
    def __init__(self, config_path):
        # Load configuration
        with open(config_path) as config_file:
            config = json.load(config_file)

        user_name = config['user_name']
        computer_name = config['computer_name']
        path = config['path']
        self.script_path = config.get('script', '')

        self.command_processor = CommandProcessor(user_name, computer_name, path)

        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title(f"{self.command_processor.user_name}@{self.command_processor.computer_name}")

        self.console = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Courier", 12), bg="purple", fg="chartreuse1")
        self.console.pack(fill=tk.BOTH, expand=True)

        self.console.bind("<Return>", self.execute_command)

        # Display initial prompt
        self.display_prompt()

        # Execute commands from script
        self.execute_script()

        self.display_prompt()

        self.root.mainloop()

    def execute_command(self, event=None):
        # Get the last line of the console
        last_line = self.console.get("end-2c linestart", "end-1c").strip()
        # Extract the command part after the last prompt
        command = last_line.split('$', 1)[-1].strip()
        self.console.insert(tk.END, "\n")

        self.run_command(command)
        self.display_prompt()

    def display_prompt(self):
        prompt = self.command_processor.get_prompt()
        self.console.insert(tk.END, prompt)
        self.console.see(tk.END)

    def execute_script(self):
        if self.script_path and os.path.isfile(self.script_path):
            with open(self.script_path, 'r') as script_file:
                first_command = True
                for line in script_file:
                    command = line.strip()
                    if command:
                        if not first_command:
                            self.display_prompt()
                        self.console.insert(tk.END, f"{command}\n")
                        self.run_command(command)
                        first_command = False

    def run_command(self, command):
        if command.startswith("cd "):
            path = command[3:].strip()
            output = self.command_processor.cd(path)
        elif command == "ls":
            output = self.command_processor.ls()
        elif command.startswith("cat "):
            file_path = command[4:].strip()
            output = self.command_processor.cat(file_path)
        elif command == "uname":
            output = self.command_processor.uname()
        elif command.startswith("rmdir "):
            dir_path = command[6:].strip()
            output = self.command_processor.rmdir(dir_path)
        elif command == "exit":
            output = self.command_processor.exit()
            self.console.insert(tk.END, output)
            self.root.quit()
            return
        else:
            output = f"Unknown command: {command}\n"

        self.console.insert(tk.END, output)
        self.console.see(tk.END)

if __name__ == "__main__":
    TerminalApp("D:\\Projects\\config_managment\\task1\\config.json")