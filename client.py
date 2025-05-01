from tkinter import filedialog, messagebox
import customtkinter as ctk
import socket
import os

ctk.set_appearance_mode("system")     # dark/light mode
ctk.set_default_color_theme("blue")   # kya pta

serverport = 12345  # works on this port
# udpport = 9999
buffer = 4096  # tcp packet size
SEPARATOR = "<SEPARATOR>"       # separator for name and size

app = ctk.CTk()    # creating a window
app.geometry("600x500")    # window dimensions
app.title("Sender")       # title

def selectfile():
    global selectedfile
    path = filedialog.askopenfilename()
    if path:
        selectedfile = path
        filelabel.configure(text=f"File : {os.path.basename(path)}")

def send():
    if not selectedfile:
        messagebox.showinfo("ERROR ! Pick a file !")
        return
    ip = ipentry.get()
    if not ip:
        messagebox.showerror("Error", "Enter receiver's IP address.")
        return

    try:
        s = socket.socket()   # create socket
        s.connect((ip, serverport))    # connect to server/ reciever

        filesize = os.path.getsize(selectedfile)     # get filesize using os mod fxn
        s.send(f"{selectedfile}{SEPARATOR}{filesize}".encode())   # send file name and file size to server

        progress.set(0)               # set progress bar to 0
        with open(selectedfile, "rb") as f:    # open the file and read as binary
            sent = 0
            while True:
                read = f.read(buffer)                  # read binary of buffer size at once
                if not read:                        # nothing left to read
                    break
                s.sendall(read)                     # send all that it reads in chunks through TCP
                sent += len(read)                   # update sent
                progress.set(sent / filesize)       # set progress
                app.update_idletasks()              # update GUI
        s.close()
        messagebox.showinfo("Success", "File sent successfully!")

    except Exception as err :
        messagebox.showerror("Error", f"Transfer failed:\n{err}")


header = ctk.CTkLabel(app, text="HELLO!",font=("Bell MT", 30), text_color="gray")
header.pack(pady=20)

filelabel = ctk.CTkLabel(app, text="No file selected", wraplength=400)
filelabel.pack(pady=15)

choose_button = ctk.CTkButton(app, text="Choose File", text_color="black", command=selectfile, hover_color="white", fg_color="#2aa8e0")
choose_button.pack(pady=10)

iplabel = ctk.CTkLabel(app, text="Receiver's IP Address:")
iplabel.pack(pady=5)

ipentry = ctk.CTkEntry(app, placeholder_text="e.g., 192.168.1.42")
ipentry.pack(pady=10)

send_button = ctk.CTkButton(app, text="Send File", command=send,  text_color="black", hover_color="white", fg_color="#2aa8e0")
send_button.pack(pady=15)

progress = ctk.CTkProgressBar(app, width=300)
progress.set(0)
progress.pack(pady=10)

footer = ctk.CTkLabel(app, text="Make sure receiver is running!", font=("Arial", 10), text_color="gray")
footer.pack(pady=5)

app.mainloop()    # runs it all