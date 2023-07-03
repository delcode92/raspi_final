import socket

def start_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    server_address = ('localhost', 65430)
    client_socket.connect(server_address)
    print("Connected to server:", server_address)

    # Send data to the server
    message = "Hello from the client!"
    client_socket.sendall(message.encode())

    # Receive a response from the server
    response = client_socket.recv(1024).decode()
    print("Received response:", response)

    # Close the connection
    client_socket.close()

if __name__ == '__main__':
    start_client()
