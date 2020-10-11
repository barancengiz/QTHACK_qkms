# import all the required modules
import socket
import threading
from random import randrange
from tkinter import *

# import all functions /
# everthing from chat.py file
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from cqc.pythonLib import CQCConnection, qubit

FORMAT = "utf-8"

# Create a new client socket
# and connect to the server
client = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)


# GUI class for the chat
class GUI:
    def generate_hash(self, sifted_key_f):
        h = SHA256.new()
        h.update(sifted_key_f)
        hash = h.digest()
        return hash

    def frombits(self, bits):
        byteList = []
        for b in range(len(bits) // 8):
            byte = bits[b * 8:(b + 1) * 8]
            byteList.append(int(''.join([str(bit) for bit in byte]), 2))
        return bytes(byteList)

    def request_pairs(self, Src, size, dest):
        message = [0, int(self.source), dest, size]
        Src.sendClassical("Server", message)
        if Src.recvClassical():
            print("Pair request is approved")
        else:
            print("Request Failed")

    def generate_base_key_pair(self):
        key = []
        for i in range(self.N):
            key.append([randrange(2), randrange(2)])  # Basis, Key pair
        return key

    def print_fancy(self, text):
        print("|" + "-" * (len(text) + 2) + "|")
        print("| " + text + " |")
        print("|" + "-" * (len(text) + 2) + "|")

    # constructor method
    def __init__(self):

        self.N = 10  # Number of paired qubits
        self.key_size = 128
        self.sifted_key = []
        self.obj = None
        self.key_match = False
        self.translation_table = str.maketrans("ıöüçşğ", "ioucsg")
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        # tyoing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # create a Label
        self.labelName2 = Label(self.login,
                                text="Dest: ",
                                font="Helvetica 12")

        self.labelName2.place(relheight=0.2,
                              relx=0.1,
                              rely=0.4)

        self.entryName2 = Entry(self.login,
                                font="Helvetica 14")

        self.entryName2.place(relwidth=0.4,
                              relheight=0.12,
                              relx=0.35,
                              rely=0.4)

        # set the focus of the curser
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName2.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name):
        self.source = self.entryName.get()
        self.dest = self.entryName2.get()
        self.login.destroy()
        self.layout("Talking W/ Node" + name)

        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

    # function to receive messages
    def receive(self):
        with CQCConnection("Node" + self.source + "r") as Receiver:
            while True:
                try:
                    while len(self.sifted_key) < self.key_size:
                        mess = Receiver.recvClassical()
                        if len(self.sifted_key) >= self.key_size:
                            plain_text = self.obj.decrypt(mess)
                            self.print_mess(plain_text, node=self.dest)
                            break
                        mess = list(mess)
                        src = mess[0]
                        is_alert = None
                        if len(mess) == 1:
                            is_alert = True
                        if is_alert:
                            pair_arr = []
                            # Make an EPR pair with Alice
                            for i in range(self.N):
                                pair_arr.append(Receiver.recvEPR())
                            print("EPR pairs received")
                            # Get lists of measurements
                            data = Receiver.recvClassical()
                            message = list(data)
                            # print("Message ", message)
                            # Apply corrections
                            for i in range(self.N):
                                a = message[i]
                                b = message[self.N + i]
                                if b == 1:
                                    pair_arr[i].X()
                                if a == 1:
                                    pair_arr[i].Z()

                            # Choose random basis for each qubit at Bob's side and then
                            # measure all qubits according to those polarizations
                            B_key = [[randrange(2), None] for _ in range(self.N)]
                            for i in range(self.N):
                                if B_key[i][0]:
                                    pair_arr[i].H()

                            measurements = []
                            # Measure qubit
                            for i in range(self.N):
                                measurements.append(pair_arr[i].measure())
                            # to_print = "App {}: Measurement outcome is: {}".format(Client.name, measurements)
                            # print_fancy(to_print)

                            Receiver.sendClassical("Node" + str(src) + "s", [a for a, _ in B_key])
                            msg = Receiver.recvClassical()
                            msg = list(msg)
                            # print("Sifted key mask: ", msg)
                            for i in range(len(msg)):
                                if msg[i] == 1:
                                    self.sifted_key.append(measurements[i])
                            print("Sifted key: ", self.sifted_key)
                    sifted_key_f = self.sifted_key[:self.key_size]
                    if not self.key_match:
                        hash_mess = self.generate_hash(self.frombits(sifted_key_f))
                        other_hash = Receiver.recvClassical()
                        if hash_mess != other_hash:
                            print("Error: Key mismatch. Deleting key")
                            Receiver.sendClassical("Node" + str(src) + "s", 0)
                            self.sifted_key = []
                            sifted_key_f = []
                            continue
                        else:
                            Receiver.sendClassical("Node" + str(src) + "s", 1)
                            self.key_match = True
                    msg = Receiver.recvClassical()

                    if self.obj is None:
                        AES_key = self.frombits(sifted_key_f)
                        print("AES key: {} size {}".format(AES_key, len(AES_key)))
                        self.obj = AES.new(AES_key)
                    plain_text = self.obj.decrypt(msg)
                    self.print_mess(plain_text, node=self.dest)
                except Exception as ex:
                    # an error will be printed on the command line or console if there's an error
                    print("An error occured!\n", ex)
                    client.close()
                    break

    def print_mess(self, plain_text, node):
        if isinstance(plain_text, bytes):
            plain_text = plain_text.decode("utf8", errors="ignore")
        if node is self.source:
            node = "Ben: "
        else:
            node = "Node {}: ".format(node)

        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, node +
                             plain_text + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    # function to send messages
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        with CQCConnection("Node" + self.source + "s") as Snd:
            try:
                text_message = self.msg
                text_message = text_message.translate(self.translation_table)
                if len(text_message) % 16 != 0:
                    text_message += " " * (16 - len(text_message) % 16)
                while len(self.sifted_key) < self.key_size:
                    q_arr = []
                    self.request_pairs(Snd, self.N, int(self.dest))
                    pair_arr = []
                    A_key = self.generate_base_key_pair()
                    print("KEY: ", [a for _, a in A_key])
                    # Receive qubits from the server
                    for i in range(self.N):
                        pair_arr.append(Snd.recvQubit())

                    # Teleportation
                    for i in range(self.N):
                        # Create a qubit to teleport
                        q = qubit(Snd)

                        if A_key[i][1] == 1:
                            q.X()
                        if A_key[i][0] == 1:
                            q.H()
                        # Teleportation operations
                        q.cnot(pair_arr[i])
                        q.H()
                        q_arr.append(q)

                    measurements_a = []
                    measurements_b = []

                    # Measure qubits
                    for i in range(self.N):
                        measurements_a.append(q_arr[i].measure())
                        measurements_b.append(pair_arr[i].measure())

                    # # Display measurement
                    # to_print = "App {}: Measurement outcomes are: a={}, b={}".format(Snd.name, measurements_a, measurements_b)
                    # print_fancy(to_print)

                    # Send measurement results for teleportation
                    msg = []
                    msg.extend(measurements_a)
                    msg.extend(measurements_b)
                    Snd.sendClassical("Node" + self.dest + "r", msg)
                    msg = Snd.recvClassical()
                    msg = list(msg)
                    sifted_key_idx = []
                    for i in range(len(msg)):
                        if A_key[i][0] == msg[i]:
                            sifted_key_idx.append(1)
                        else:
                            sifted_key_idx.append(0)
                    # print("Sifted key mask: ", sifted_key_idx)
                    Snd.sendClassical("Node" + self.dest + "r", sifted_key_idx)

                    for i in range(len(sifted_key_idx)):
                        if sifted_key_idx[i] == 1:
                            self.sifted_key.append(A_key[i][1])
                    print("Sifted key: ", self.sifted_key)
                    print("Sifted key length: ", len(self.sifted_key))
                sifted_key_f = self.sifted_key[:self.key_size]

                if not self.key_match:
                    hash_mess = self.generate_hash(self.frombits(sifted_key_f))
                    Snd.sendClassical("Node" + self.dest + "r", hash_mess)
                    key_correct = Snd.recvClassical()
                    if not key_correct:
                        print("Error: Key mismatch. Deleting key")
                        self.sifted_key = []
                        sifted_key_f = []
                        return
                    else:
                        self.key_match = True

                if self.obj is None:
                    AES_key = self.frombits(sifted_key_f)
                    print("AES key size {}".format(len(AES_key)))
                    self.obj = AES.new(AES_key)
                cipher_text = self.obj.encrypt(text_message)
                Snd.sendClassical("Node" + self.dest + "r", cipher_text)
                self.print_mess(text_message, node=self.source)

            except Exception as err:
                print(err)
                pass


# create a GUI class object
g = GUI()
