import socket


def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    client_socket.send(command.encode('utf-8'))

    client_socket.close()


if __name__ == "__main__":
    command = input("Enter command ('kill' to terminate clickermann): ")
    send_command(command)
