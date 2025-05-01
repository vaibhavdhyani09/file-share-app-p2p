import threading
import customtkinter as ctk
import socket
import os

ctk.set_appearance_mode("system")     # dark/light mode
ctk.set_default_color_theme("blue")   # kya pta

serverhost = '0.0.0.0'
port = 12345
buffer = 4096
SEPARATOR = "<SEPARATOR>"       # separator for name and size

app = ctk.CTk()
app.title("Reciever")
app.geometry("600x500")

statuslabel = ctk.CTkLabel(app, text="Waiting for file...", font=("Arial", 16))
statuslabel.pack(pady=20)

filenamelabel = ctk.CTkLabel(app, text="", wraplength=400)
filenamelabel.pack(pady=5)

progress = ctk.CTkProgressBar(app, width=400)
progress.set(0)
progress.pack(pady=20)

save = "received_files"
os.makedirs(save, exist_ok=True)

def start_server():
    s = socket.socket()
    s.bind((serverhost, port))
    s.listen(1)

    while True:
        client_socket, address = s.accept()
        statuslabel.configure(text=f"Connected to: {address}")

        try:
            received = client_socket.recv(buffer).decode()
            filename, filesize = received.split(SEPARATOR)
            filename = os.path.basename(filename)
            filenamelabel.configure(text=f"Receiving: {filename}")
            filepath = os.path.join(save, filename)
            filesize = int(filesize)

            received_size = 0
            progress.set(0)

            with open(filepath, "wb") as f:
                while received_size < filesize:
                    bytes_read = client_socket.recv(buffer)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    received_size += len(bytes_read)
                    progress.set(received_size / filesize)
                    app.update_idletasks()

            statuslabel.configure(text="✅ File received successfully!")
        except Exception as e:
            statuslabel.configure(text=f"❌ Error: {e}")

        client_socket.close()

# Start server in background
threading.Thread(target=start_server, daemon=True).start()

app.mainloop()