import os
import tarfile
import json
import tkinter as tk
from tkinter import scrolledtext
import platform

class CommandProcessor:
    def __init__(self, user_name, computer_name, path):
        self.user_name = user_name
        self.computer_name = computer_name
        self.path = path

        self.filename_without_extension = os.path.splitext(os.path.basename(self.path))[0]

        # Extract filesystem
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        with tarfile.open(self.path, 'r') as tar:
            tar.extractall(path=self.base_dir)

        # Set the root folder
        self.extracted_dir = os.path.join(self.base_dir, self.filename_without_extension)
        self.current_dir = self.extracted_dir

    def cd(self, path):
        new_dir = os.path.abspath(os.path.join(self.current_dir, path))
        if new_dir.startswith(self.extracted_dir) and os.path.isdir(new_dir):
            self.current_dir = new_dir
            return ""
        else:
            return "cd: no such file or directory\n"

    def ls(self):
        try:
            files = os.listdir(self.current_dir)
            return "\n".join(files) + "\n"
        except Exception as e:
            return f"Error: {str(e)}\n"

    def cat(self, file_path):
        full_path = os.path.join(self.current_dir, file_path)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as file:
                return file.read() + "\n"
        else:
            return f"cat: {file_path}: No such file\n"

    def uname(self):
        return platform.system() + "\n"

    def rmdir(self, dir_path):
        full_path = os.path.join(self.current_dir, dir_path)
        if os.path.isdir(full_path):
            try:
                os.rmdir(full_path)
                return ""
            except Exception as e:
                return f"rmdir: {str(e)}\n"
        else:
            return f"rmdir: {dir_path}: No such directory\n"

    def exit(self):
        self.add_to_tar(self.path, self.extracted_dir)
        return ""

    def add_to_tar(self, tar_path, dir_to_add):
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(dir_to_add, arcname=os.path.basename(dir_to_add))

    def get_prompt(self):
        relative_dir = os.path.relpath(self.current_dir, self.extracted_dir)
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
    TerminalApp('config.json')