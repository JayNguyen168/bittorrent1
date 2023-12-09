import os
import shlex
import PySimpleGUI as sg
import threading

from client import FileClient

class FileClientGUI:
    def __init__(self):     # Done
        self.client = FileClient(log_callback=self.log)

        self.layout = [
            [sg.Text("File client GUI", font=("Helvetica", 16)), sg.Text("My Repository", key="-REPO_TEXT-", font=("Helvetica", 16), pad=(440, 0), visible=False)],
            [sg.Multiline("", key="-OUTPUT-", font=("Helvetica", 14), size=(50, 20), autoscroll=True, reroute_cprint=True, disabled=True), sg.Multiline("", key="-REPO-", font=("Helvetica", 14), size=(50, 20), disabled=True, visible=False)],
            [sg.Text("Host name:", key="-HN_TEXT-", font=("Helvetica", 12)), sg.InputText(key="-HOSTNAME-", size=(40, 1)), sg.Button("Connect", key="-CONNECT_BUTTON-")],
            [sg.Text("Command:", key="-COMMAND_TEXT-", font=("Helvetica", 12), visible=False), sg.InputText(key="-COMMAND-", size=(40, 1), visible=False), sg.Button("Send Command", key="-COMMAND_BUTTON-", visible=False)],
            [sg.Text("Upload File:", key="-UPLOAD_TEXT-", font=("Helvetica", 12), visible=False), sg.InputText(key="-FILE_PATH-", size=(40, 1), visible=False),
             sg.FileBrowse(key="-BROWSE-", visible=False)],
            [sg.Text("File Name:", key="-FN_TEXT-", font=("Helvetica", 12), visible=False), sg.InputText(key="-FILE_NAME-", size=(40, 1), visible=False),
             sg.Button("Publish", key="-PUBLISH-", visible=False)],
            [ sg.Button("Quit")]
        ]

        self.window = sg.Window("File Client GUI", self.layout, finalize=True)

        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED or event == "Quit":    
                self.quit_client()
                break
            
            elif event == "-CONNECT_BUTTON-":      
                hostname = values["-HOSTNAME-"]
                self.connect(hostname)
                    
            elif event == "-PUBLISH-":         
                self.publish(values["-FILE_PATH-"], values["-FILE_NAME-"])
                
            elif event == "-COMMAND_BUTTON-":
                command_parts = shlex.split(values["-COMMAND-"])
                if command_parts[0] == "publish":
                    self.publish(command_parts[1], command_parts[2])
                elif command_parts[0] == "fetch":
                    self.fetch(command_parts[1])

    def connect(self, hostname):        # Done
        if hostname:
            try:
                client_address = self.client.connect_to_server(hostname)
                self.log(f"Client address: {client_address}")
                if client_address:
                    self.log(f"Hostname {hostname} set successfully.")
                    threading.Thread(target=self.client.start, args=(client_address,)).start()
                    self.window["-REPO_TEXT-"].update(visible=True)
                    self.window["-REPO-"].update(visible=True)
                    self.window["-HN_TEXT-"].update(visible=False)
                    self.window["-HOSTNAME-"].update(visible=False)
                    self.window["-CONNECT_BUTTON-"].update(visible=False)
                    self.window["-COMMAND_TEXT-"].update(visible=True)
                    self.window["-COMMAND-"].update(visible=True)
                    self.window["-COMMAND_BUTTON-"].update(visible=True)
                    self.window["-UPLOAD_TEXT-"].update(visible=True)
                    self.window["-FILE_PATH-"].update(visible=True)
                    self.window["-BROWSE-"].update(visible=True)
                    self.window["-FN_TEXT-"].update(visible=True)
                    self.window["-FILE_NAME-"].update(visible=True)
                    self.window["-PUBLISH-"].update(visible=True)
                    
                    # Create a repository folder if it doesn't exist
                    self.client.repository_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repository")
                    if not os.path.exists(self.client.repository_folder):
                        os.makedirs(self.client.repository_folder)
                        self.log(f'Repository folder created: {self.client.repository_folder}')
                    else:
                        self.client.connect_publish(self.client.client_socket)
                        result = ""
                        for file_name in os.listdir(self.client.repository_folder):
                            result += f"{file_name}\n"
                        result = result.rstrip("\n")
                    self.window["-REPO-"].update(disabled=False)
                    self.window["-REPO-"].print(result)
                    self.window["-REPO-"].update(disabled=True)
                    
            except Exception as e:
                self.log(f"Error setting hostname: {e}")
        else:
            self.log("Hostname cannot be empty.")

    def publish(self, file_path, file_name):     # Done
        if not file_name or not file_path:
            self.log("Error publishing file: Please fill in the blank!")
            return
        
        if file_name and "." not in file_name:
            file_extension = os.path.splitext(file_path)[1]
            file_name += file_extension
            
        try:
            publish_status = self.client.publish(self.client.client_socket, file_path, file_name)
            if publish_status:
                self.window["-FILE_PATH-"].update("")
                self.window["-FILE_NAME-"].update("")
                self.window["-COMMAND-"].update("")
                self.window["-REPO-"].update(disabled=False)
                self.window["-REPO-"].print(file_name.rstrip("\n"))
                self.window["-REPO-"].update(disabled=True)
        except Exception as e:
            self.log(f"Error publishing file: {e}")

    def fetch(self, file_name):
        if not file_name:
            self.log("Error fetching file: File name cannot be blank!")
            return
        try:
            fetch_status = self.client.fetch(self.client.client_socket, file_name)
            if fetch_status:
                self.window["-COMMAND-"].update("")
                self.window["-REPO-"].update(disabled=False)
                self.window["-REPO-"].print(file_name.rstrip("\n"))
                self.window["-REPO-"].update(disabled=True)
        except Exception as e:
            self.log(f"Error fetching file: {e}")

    def quit_client(self):      # Done
        self.client.quit(self.client.client_socket)
        self.window.close()

    def log(self, message):     # Done
        self.window["-OUTPUT-"].update(disabled=False)
        self.window["-OUTPUT-"].print(message, end="\n")
        self.window["-OUTPUT-"].update(disabled=True)
        

if __name__ == "__main__":
    gui = FileClientGUI()
