import socket
import threading
import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


selectedfile = None
app = ctk.CTk()
app.geometry("600x600")
app.title("Sender")

port = 12345
buffer = 4096
SEPARATOR = "<SEPARATOR>"

receiver_ip = None

class FileReceiverListener(ServiceListener):
    def remove_service(self, zc, type, name): pass
    def update_service(self, zc, type, name): pass

    def add_service(self, zc, type, name):
        global receiver_ip
        info = zc.get_service_info(type, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            receiver_ip = ip
            ipentry.delete(0, "end")
            ipentry.insert(0, ip)
            statuslabel.configure(text=f"Found receiver: {ip}")

def discover_receiver():
    zeroconf = Zeroconf()
    listener = FileReceiverListener()
    ServiceBrowser(zeroconf, "_filetransfer._tcp.local.", listener)

def selectfile():
    global selectedfile
    path = filedialog.askopenfilename()
    if path:
        selectedfile = path
        filelabel.configure(text=f"File : {os.path.basename(path)}")

def send():
    if not selectedfile:
        messagebox.showerror("Error", "Pick a file first.")
        return
    ip = ipentry.get()
    if not ip:
        messagebox.showerror("Error", "No receiver found or IP empty.")
        return
    try:
        s = socket.socket()
        s.connect((ip, port))
        filesize = os.path.getsize(selectedfile)
        s.send(f"{selectedfile}{SEPARATOR}{filesize}".encode())

        progress.set(0)
        sent = 0
        with open(selectedfile, "rb") as f:
            while True:
                chunk = f.read(buffer)
                if not chunk:
                    break
                s.sendall(chunk)
                sent += len(chunk)
                progress.set(sent / filesize)
                app.update_idletasks()
        s.close()
        messagebox.showinfo("Success", "File sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")

header = ctk.CTkLabel(app, text="HELLO!", font=("Bell MT", 30), text_color="gray")
header.pack(pady=20)

filelabel = ctk.CTkLabel(app, text="No file selected", wraplength=400)
filelabel.pack(pady=15)

choose_button = ctk.CTkButton(app, text="Choose File", command=selectfile, text_color="black", hover_color="white", fg_color="#2aa8e0")
choose_button.pack(pady=10)

ipentry = ctk.CTkEntry(app, placeholder_text="Receiver IP (auto-filled)")
ipentry.pack(pady=10)

send_button = ctk.CTkButton(app, text="Send File", command=send, text_color="black", hover_color="white", fg_color="#2aa8e0")
send_button.pack(pady=15)

progress = ctk.CTkProgressBar(app, width=300)
progress.set(0)
progress.pack(pady=10)

statuslabel = ctk.CTkLabel(app, text="Looking for receiver...", text_color="gray")
statuslabel.pack(pady=5)

threading.Thread(target=discover_receiver, daemon=True).start()
app.mainloop()



