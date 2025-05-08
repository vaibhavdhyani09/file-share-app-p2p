import socket
import threading
import os
import customtkinter as ctk
from zeroconf import Zeroconf, ServiceInfo
from tkinter import messagebox

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Receiver")
app.geometry("600x500")

port = 12345
buffer = 4096
SEPARATOR = "<SEPARATOR>"
save = "received_files"
os.makedirs(save, exist_ok=True)

statuslabel = ctk.CTkLabel(app, text="Waiting for file...", font=("Arial", 16))
statuslabel.pack(pady=20)

filenamelabel = ctk.CTkLabel(app, text="", wraplength=400)
filenamelabel.pack(pady=5)

progress = ctk.CTkProgressBar(app, width=400)
progress.set(0)
progress.pack(pady=20)

def register_mdns():
    zeroconf = Zeroconf()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    service_info = ServiceInfo(
        "_filetransfer._tcp.local.",
        "FileReceiver._filetransfer._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={},
        server=f"{hostname}.local.",
    )
    zeroconf.register_service(service_info)

def start_server():
    s = socket.socket()
    s.bind(('', port))
    s.listen(1)

    while True:
        client_socket, addr = s.accept()
        statuslabel.configure(text=f"Connected to {addr}")

        try:
            received = client_socket.recv(buffer).decode()
            filename, filesize = received.split(SEPARATOR)
            filename = os.path.basename(filename)
            filenamelabel.configure(text=f"Receiving: {filename}")
            filepath = os.path.join(save, filename)
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filename)
                count = 1
                new_filename = f"{base}_copy{count}{ext}"
                while os.path.exists(os.path.join(save, new_filename)):
                    count += 1
                    new_filename = f"{base}_copy{count}{ext}"
                filepath = os.path.join(save, new_filename)
                # print(f"⚠ File already exists. Saving as: {new_filename}")
                messagebox.showinfo("Copy exists!", f"File exists. Saved as: {new_filename}")

            filesize = int(filesize)

            received_size = 0
            progress.set(0)

            with open(filepath, "wb") as f:
                while received_size < filesize:
                    chunk = client_socket.recv(buffer)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)
                    progress.set(received_size / filesize)
                    app.update_idletasks()

            statuslabel.configure(text="File received successfully!")
        except Exception as e:
            statuslabel.configure(text=f"Error: {e}")
        client_socket.close()

threading.Thread(target=register_mdns, daemon=True).start()
threading.Thread(target=start_server, daemon=True).start()
app.mainloop()

