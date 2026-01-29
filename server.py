import socket
import threading

# --- CONFIGURATION ---
HOST = '0.0.0.0'
TCP_PORT = 8888  # Chat Port
UDP_PORT = 9999  # Voice Port

# Lists to keep track of connected users
clients_tcp = []
clients_udp = []
lock = threading.Lock()

def broadcast_chat(message, sender_socket):
    """Relays a chat message to all other connected TCP clients."""
    with lock:
        for client in clients_tcp:
            if client != sender_socket:
                try: client.send(message)
                except: 
                    client.close()
                    if client in clients_tcp: clients_tcp.remove(client)

def broadcast_audio(data, sender_addr):
    """Relays voice data to all other connected UDP clients."""
    with lock:
        for client_addr in clients_udp:
            if client_addr != sender_addr:
                try: udp_socket.sendto(data, client_addr)
                except: pass

def handle_tcp_client(client_socket):
    """Listens for messages from a specific user."""
    while True:
        try:
            message = client_socket.recv(1024)
            if not message: break
            broadcast_chat(message, client_socket)
        except: break
    
    with lock:
        if client_socket in clients_tcp: clients_tcp.remove(client_socket)
    client_socket.close()

def start_server():
    global udp_socket
    print(f"--- DROIDSHIELD GLOBAL SERVER LIVE ---")
    print(f"[*] Listening for Chat on TCP Port {TCP_PORT}")
    print(f"[*] Listening for Voice on UDP Port {UDP_PORT}")
    
    # 1. Setup TCP (Chat)
    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp.bind((HOST, TCP_PORT))
    server_tcp.listen()

    # 2. Setup UDP (Voice)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    # 3. Background Thread for Voice
    def udp_handler():
        while True:
            try:
                data, addr = udp_socket.recvfrom(4096)
                with lock:
                    if addr not in clients_udp:
                        clients_udp.append(addr)
                        print(f"[+] Voice Client Joined: {addr}")
                broadcast_audio(data, addr)
            except: pass
            
    threading.Thread(target=udp_handler, daemon=True).start()

    # 4. Main Loop for Chat
    while True:
        client, addr = server_tcp.accept()
        with lock:
            clients_tcp.append(client)
        print(f"[+] Chat Client Joined: {addr}")
        threading.Thread(target=handle_tcp_client, args=(client,)).start()

if __name__ == "__main__":
    start_server()