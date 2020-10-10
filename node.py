import sys
import threading
from random import randrange

from Crypto.Cipher import AES
from cqc.pythonLib import CQCConnection, qubit

N = 10  # Number of paired qubits
key_size = 128
arg_list = sys.argv
source = int(arg_list[1])
dest = int(arg_list[2])
sifted_key = []
obj = None


def frombits(bits):
    byteList = []
    for b in range(len(bits) // 8):
        byte = bits[b * 8:(b + 1) * 8]
        byteList.append(int(''.join([str(bit) for bit in byte]), 2))
    return bytes(byteList)


def create_key_rcv():
    print("Inside Rcv")
    with CQCConnection("Node" + str(source) + "r") as Receiver:
        while (True):
            while len(sifted_key) < key_size:
                mess = Receiver.recvClassical()
                mess = list(mess)
                src = mess[0]
                is_alert = None
                if len(mess) == 1:
                    is_alert = True
                if is_alert:
                    pair_arr = []
                    # Make an EPR pair with Alice
                    for i in range(N):
                        pair_arr.append(Receiver.recvEPR())
                    print("EPR pairs received")
                    # Get lists of measurements
                    data = Receiver.recvClassical()
                    message = list(data)
                    # print("Message ", message)
                    # Apply corrections
                    for i in range(N):
                        a = message[i]
                        b = message[N + i]
                        if b == 1:
                            pair_arr[i].X()
                        if a == 1:
                            pair_arr[i].Z()

                    # Choose random basis for each qubit at Bob's side and then
                    # measure all qubits according to those polarizations
                    B_key = [[randrange(2), None] for _ in range(N)]
                    for i in range(N):
                        if B_key[i][0]:
                            pair_arr[i].H()

                    measurements = []
                    # Measure qubit
                    for i in range(N):
                        measurements.append(pair_arr[i].measure())
                    # to_print = "App {}: Measurement outcome is: {}".format(Client.name, measurements)
                    # print_fancy(to_print)

                    Receiver.sendClassical("Node" + str(src) + "s", [a for a, _ in B_key])
                    msg = Receiver.recvClassical()
                    msg = list(msg)
                    # print("Sifted key mask: ", msg)
                    for i in range(len(msg)):
                        if msg[i] == 1:
                            sifted_key.append(measurements[i])
                    print("Sifted key: ", sifted_key)
            sifted_key_f = sifted_key[:key_size]
            msg = Receiver.recvClassical()

            global obj
            if obj is None:
                AES_key = frombits(sifted_key_f)
                print("AES key: {} size {}".format(AES_key, len(AES_key)))
                obj = AES.new(AES_key)
            plain_text = obj.decrypt(msg)
            print("Node{}: {}".format(dest, plain_text.decode("utf8")))


def create_key_snd():
    print("Inside Send")
    with CQCConnection("Node" + str(source) + "s") as Snd:
        while (True):
            text_message = input()
            if len(text_message) % 16 != 0:
                text_message += " " * (16 - len(text_message) % 16)
            while len(sifted_key) < key_size:
                q_arr = []
                request_pairs(Snd, N, dest)
                pair_arr = []
                A_key = generate_base_key_pair()
                print("KEY: ", [a for _, a in A_key])
                # Receive qubits from the server
                for i in range(N):
                    pair_arr.append(Snd.recvQubit())

                # Teleportation
                for i in range(N):
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
                for i in range(N):
                    measurements_a.append(q_arr[i].measure())
                    measurements_b.append(pair_arr[i].measure())

                # # Display measurement
                # to_print = "App {}: Measurement outcomes are: a={}, b={}".format(Snd.name, measurements_a, measurements_b)
                # print_fancy(to_print)

                # Send measurement results for teleportation
                msg = []
                msg.extend(measurements_a)
                msg.extend(measurements_b)
                Snd.sendClassical("Node" + str(dest) + "r", msg)
                msg = Snd.recvClassical()
                msg = list(msg)
                sifted_key_idx = []
                for i in range(len(msg)):
                    if A_key[i][0] == msg[i]:
                        sifted_key_idx.append(1)
                    else:
                        sifted_key_idx.append(0)
                # print("Sifted key mask: ", sifted_key_idx)
                Snd.sendClassical("Node" + str(dest) + "r", sifted_key_idx)

                for i in range(len(sifted_key_idx)):
                    if sifted_key_idx[i] == 1:
                        sifted_key.append(A_key[i][1])
                print("Sifted key: ", sifted_key)
                print("Sifted key length: ", len(sifted_key))
            sifted_key_f = sifted_key[:key_size]

            global obj
            if obj is None:
                AES_key = frombits(sifted_key_f)
                print("AES key size {}".format(len(AES_key)))
                obj = AES.new(AES_key)
            cipher_text = obj.encrypt(text_message)
            Snd.sendClassical("Node" + str(dest) + "r", cipher_text)


def request_pairs(Src, size, dest):
    message = [0, source, dest, size]
    Src.sendClassical("Server", message)
    if Src.recvClassical():
        print("Pair request is approved")
    else:
        print("Request Failed")


def generate_base_key_pair():
    key = []
    for i in range(N):
        key.append([randrange(2), randrange(2)])  # Basis, Key pair
    return key


def print_fancy(text):
    print("|" + "-" * (len(text) + 2) + "|")
    print("| " + text + " |")
    print("|" + "-" * (len(text) + 2) + "|")


def main():
    # Initialize the connection

    t1 = threading.Thread(target=create_key_rcv)
    t2 = threading.Thread(target=create_key_snd)

    t1.start()
    t2.start()


main()
