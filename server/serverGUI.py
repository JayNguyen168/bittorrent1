# import platform
import threading
import PySimpleGUI as sg

from server import ServerLogic

class ServerGUI:
    def __init__(self, host, port):
        self.server = ServerLogic(
            host,
            port,
            log_callback=self.log_message,
            log_request_callback=self.log_request,
        )

        # Layout
        layout = [
            [sg.Text('Logs', font=('Courier New', 26, 'bold'), text_color='purple', background_color='black')],
            [sg.Multiline("", size=(70, 15), key='-LOG-', autoscroll=True, disabled=True, reroute_cprint=True, font=('Courier New', 14), background_color='black', text_color='white')],
            [sg.Text('Requests', font=('Courier New', 26, 'bold'), text_color='purple', background_color='black')],
            [sg.Multiline(size=(70, 15), key='-REQUEST_LOG-', disabled=True, autoscroll=True, font=('Courier New', 14), background_color='black', text_color='white')],
            [sg.InputText(key='-COMMAND-', size=(50, 1), font=('Courier New', 14), background_color='black', text_color='white'), sg.Button('Send Command', key='-SEND_COMMAND-', font=('Courier New', 12), button_color=('black', 'orange'))],
            [sg.Button('Start Server', key='-START_SERVER-', font=('Courier New', 12), button_color=('black', 'green')),
             sg.Button('Stop Server', key='-STOP_SERVER-', font=('Courier New', 12), button_color=('black', 'red'))]
        ]
        self.window = sg.Window('P2P Server GUI', layout, finalize=True)
        
    def start_server(self):
        self.log_message("Starting server...")
        self.server.start()

    def stop_server(self):
        self.log_message("Server stopped.\n")
        self.server.shutdown()

    def send_command(self, command):
        threading.Thread(target=self.server.process_server_command, args=(command,)).start()

    def on_close(self):
        self.server.shutdown()
        self.window.close()

    def log_message(self, message):
        self.window["-LOG-"].update(disabled=False)
        self.window["-LOG-"].print(message, end="\n")
        self.window["-LOG-"].update(disabled=True)

    def log_request(self, message):
        self.window["-REQUEST_LOG-"].update(disabled=False)
        self.window["-REQUEST_LOG-"].print(message, end="\n")
        self.window["-REQUEST_LOG-"].update(disabled=True)

if __name__ == '__main__':
    gui = ServerGUI("0.0.0.0", 8888)

    while True:
        event, values = gui.window.read()

        if event == sg.WINDOW_CLOSED:
            gui.on_close()
            break
        elif event == '-START_SERVER-':
            gui.start_server()
        elif event == '-STOP_SERVER-':
            gui.stop_server()
        elif event == '-SEND_COMMAND-':
            gui.send_command(values["-COMMAND-"])

