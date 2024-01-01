import socket
import os
import psutil


def close_clickermann():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'].lower() == 'clickermann.exe':
            print(process)
            os.system(f"taskkill /F /PID {process.info['pid']}")
            print("Clickermann terminated.")


def print_process():
    for process in psutil.process_iter(['pid', 'name']):
        print(process)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print("Server listening on port 12345...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(1024).decode('utf-8')

        if data == 'kill':
            close_clickermann()

        client_socket.close()


if __name__ == "__main__":
    # start_server()
    # print_process()
    close_clickermann()
