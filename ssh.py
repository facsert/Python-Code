'''
Author: facsert
Date: 2023-08-23 20:34:57
LastEditTime: 2023-08-23 22:19:25
LastEditors: facsert
Description: 
'''

from time import time
from re import search
from paramiko import SSHClient, AutoAddPolicy

class Client:

    def __init__(self, host, port, username, password, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = self.connect()

    def connect(self):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(self.host, 
            self.port, 
            self.username, 
            self.password, 
            timeout=self.timeout
        )
        return client

    def exec(self, command):
        print(command)
        _, stdout, stderr = self.client.exec_command(command)
        success = True if stdout.channel.recv_exit_status() == 0 else False
        return success, f"{stdout.read().decode('utf-8')}{stderr.read().decode('utf-8')}"
    
    def shell(self, command, timeout=20):
        channel = self.client.invoke_shell()
        channel.sendall(command + ';echo "status_code: $?"\n')
        end_time = time() + timeout

        success, output = False, ''
        while True:
            if time() > end_time:
                output += f"\nTimeoutError: {command}"
                break

            data = channel.recv(4096).decode('utf-8')
            output += data
            
            try:
                status = search("status_code: \d+", data).group()
                success = True if int(status.strip().split(":")[-1]) == 0 else False
                break
            except Exception as _:
                continue
        return success, output
    
    def sftp(self):
        return self.client.open_sftps()
        


if __name__ == "__main__":
    client = Client("192.168.1.100", 22, "root", "admin")
    success, output = client.exec("sleep 3; date; echo $PWD")
    print(output)

    success, output = client.shell("ifconfig")
    print(output)
    print(f"code: {success}")     

