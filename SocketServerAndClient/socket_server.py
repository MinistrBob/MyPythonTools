import socket
import os
import psutil
from server_settings import app_settings as appset


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
    server_socket.bind((appset.bind_ip, appset.bind_port))
    server_socket.listen(1)

    print(f"Server listening on [{appset.bind_ip}] port {appset.bind_port}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            data = client_socket.recv(1024).decode('utf-8')

            if data == 'kill':
                close_clickermann()

            client_socket.close()
    except KeyboardInterrupt:
        # Handle Ctrl+C
        print("\nServer interrupted. Closing...")
        server_socket.close()
        sys.exit()


if __name__ == "__main__":
    # print_process()
    # close_clickermann()
    
    # Register a signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    start_server()

