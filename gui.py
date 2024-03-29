# BOTC Wallet
# by vortex

import uuid, sys, glob, os, qrcode, tempfile
import configparser as c
from pathlib import Path
from wallet import *

import tkinter as tk
import tkinter.messagebox as tmb
from PIL import ImageTk, Image

if sys.platform == "win32" or sys.platform == "win64":
    slash = "\\"
else:
    slash = "/"

sampleurl = "PLEASE SET YOUR HOST"

class GUI:
    def __init__(self):
        self.wallet = Wallet(sampleurl) # sample url
        self.private_file = str(Path.home()) + slash + str(uuid.uuid4()) + ".botcpkey"
        self.config_file = str(Path.home()) + slash + str(uuid.uuid4()) + ".botcconfig"
        self.exportKey()
        self.getURL()

    def getURL(self):
        config = c.ConfigParser()
        if glob.glob(str(Path.home()) + slash + "*.botcconfig") == []:
            config['uri'] = {}
            config['uri']['URL'] = sampleurl
                
            with open(self.config_file, "w") as f:
                config.write(f)
        else:
            f = glob.glob(str(Path.home()) + slash + "*.botcconfig")[0]
            if config.read(f) == [f]:
                self.wallet.url = config['uri']['URL']

    def importKey(self, file):
        with open(file, "rb") as f:
            self.wallet = CustomWallet(f.read(), sampleurl) # sample url
    
    def exportKey(self):
        # look for .botcpkey file. if exists, then skip, else dump private key
        if glob.glob(str(Path.home()) + slash + "*.botcpkey") == []:
            with open(self.private_file, "wb") as f:
                f.write(self.wallet.private_key.exportKey("DER"))
                f.close()

        else:
            self.importKey(glob.glob(str(Path.home()) + slash + "*.botcpkey")[0])

gui = GUI()

def newWallet():
    ask = tmb.askokcancel("Are you sure?", "This will remove your private key and configuration file from disk to make a new one. You will lose your coins and your settings. Do you wish to continue?")
    if ask == True:
        if glob.glob(str(Path.home()) + slash + "*.botcpkey") != []:
            os.remove(glob.glob(str(Path.home()) + slash + "*.botcpkey")[0])
            os.remove(glob.glob(str(Path.home()) + slash + "*.botcconfig")[0])
            
            gui = GUI()

### GRAPHICS ###
root = tk.Tk()
root.geometry("640x480")
root.title('BOTC Wallet')
menu = tk.Menu(root)

current_host = tk.Label(master = root, text = "Current host: {}".format(gui.wallet.url))
balance = tk.Label(master = root, text = "Balance: {} coins".format(gui.wallet.coins))

class NewHost:
    def __init__(self, master):
        w = tk.Toplevel(master)
        self.text = tk.Label(w, text = "In order to connect to the network, please change your host.")
        self.estr = tk.StringVar()
        self.entry = tk.Entry(w, textvariable = self.estr)
        self.button = tk.Button(w, text = "Connect", command = self.changeHost)

        self.text.pack()
        self.entry.pack()
        self.button.pack()

    def changeHost(self):
        if self.estr.get() == "":
            self.text.config(text = "Not a valid host!")

        config = c.ConfigParser()

        f = glob.glob(str(Path.home()) + slash + "*.botcconfig")[0]
        config['uri'] = {}
        config['uri']['URL'] = self.estr.get()

        with open(f, "w") as fp:
            config.write(fp)

        gui.wallet.url = self.estr.get()
        current_host.config(text = "Current host: {}".format(gui.wallet.url))
        print(gui.wallet.url)

def newHost():
    w = NewHost(root)

class NewTransaction:
    def __init__(self, master):
        w = tk.Toplevel(master)
        w.geometry("320x240")

        self.text = tk.Label(w, text = "Send coins to an address\n")
        self.estr = tk.StringVar()
        self.sstr = tk.DoubleVar()
        self.entrytext = tk.Label(w, text = "Recipient Address: ", justify = tk.LEFT)
        self.entry = tk.Entry(w, textvariable = self.estr, justify = tk.CENTER)
        self.button = tk.Button(w, text = "Send", command = self.send, justify = tk.CENTER)

        self.scaletext = tk.Label(w, text = "\n\nAmount sending:", justify = tk.CENTER)
        self.scale = tk.Scale(w, variable = self.sstr, orient = tk.HORIZONTAL)

        self.text.pack()
        self.entrytext.pack()
        self.entry.pack()
        self.scaletext.pack()
        self.scale.pack(anchor=tk.CENTER)
        self.button.pack()

    def send(self):
        try:
            if gui.wallet.url == sampleurl:
                self.text.config(text = "Change your host!")
        except requests.exceptions.InvalidURL:
            print("!!!CHANGE YOUR HOST!!!")

        if int(self.sstr.get()) == 0:
            self.text.config(text = "You cannot send nothing")

        try:
            if gui.wallet.sendTransaction(self.estr.get(), int(self.sstr.get())) == False:
                self.text.config(text = "Not enough coins!")
            else:
                self.text.config(text = "Transaction complete!")
                balance.config(text = "Balance: {} coins".format(gui.wallet.coins))
        except requests.exceptions.ConnectionError:
            self.text.config(text = "Host not working!")

def newTransaction():
    nt = NewTransaction(root)

class RecieveCoins:
    def __init__(self, master):
        w = tk.Toplevel(master)
        
        templocation = tempfile.NamedTemporaryFile(prefix = "botckqr", delete = False)
        qrcode.make(gui.wallet.identity).save(templocation)

        self.image = ImageTk.PhotoImage(Image.open(templocation))
        self.text = tk.Label(w, text = "Recieve coins with your address\n")
        self.button = tk.Button(w, text = "Retrieve coins", command = self.recieve)

        self.qr_button = tk.Button(w, text = "Show QR Code", command = self.showqr)
        self.addr_button = tk.Button(w, text = "Show Address", command = self.showaddress)

        self.text.pack()
        self.qr_button.pack()
        self.addr_button.pack()
        self.button.pack()

    def showqr(self):
        w = tk.Toplevel(root)
        qr = tk.Label(w, image = self.image)
        qr.pack()
    
    def showaddress(self):
        w = tk.Toplevel(root)
        l = tk.Label(w, text = "Copy me!")
        addr = tk.Text(w)
        l.pack()
        addr.insert(1.0, gui.wallet.identity)
        addr.pack()

    def recieve(self):
        try:
            if gui.wallet.url == sampleurl:
                self.text.config(text = "Change your host!")
        except requests.exceptions.InvalidURL:
            print("!!!CHANGE YOUR HOST!!!")

        try:
            gui.wallet.recieve()
            balance.config(text = "Balance: {} coins".format(gui.wallet.coins))
        except requests.exceptions.ConnectionError:
            self.text.config(text = "Host not working!")
        

def recieveCoins():
    rc = RecieveCoins(root)

if __name__ == '__main__':

    fmenu = tk.Menu(menu, tearoff=0)
    fmenu.add_command(label="Remake wallet", command=newWallet)
    fmenu.add_command(label="Use other host", command=newHost)
    fmenu.add_separator()
    fmenu.add_command(label="Exit", command=root.quit)
    menu.add_cascade(label="File", menu=fmenu)

    txnmenu = tk.Menu(menu, tearoff=0)
    txnmenu.add_command(label="New transaction", command=newTransaction)
    txnmenu.add_command(label="Recieve coins", command=recieveCoins)
    menu.add_cascade(label="Transaction", menu=txnmenu)

    print("""
    BOTC Wallet by vortex
    Written with <3
    """)
    
    root.config(menu = menu)
    current_host.pack()
    balance.pack()
    root.mainloop()
