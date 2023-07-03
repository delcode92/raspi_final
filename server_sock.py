import socket

def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('localhost', 65430)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print("Server is listening on {}:{}".format(server_address[0], server_address[1]))

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print("Connected to client:", client_address)

        # Receive data from the client
        data = client_socket.recv(1024).decode()
        print("Received data:", data)

        # Send a response back to the client
        response = "Hello from the server!"
        client_socket.sendall(response.encode())

        # Close the client connection
        client_socket.close()

if __name__ == '__main__':
    start_server()
