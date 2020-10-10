from random import randrange

from cqc.pythonLib import CQCConnection, qubit

N = 10  # Number of paired qubits
key_size = 56
src = 1
dest = 2
sifted_key = []


def create_key_snd(Snd):
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
        Snd.sendClassical("Node" + str(dest), msg)
        msg = Snd.recvClassical()
        msg = list(msg)
        sifted_key_idx = []
        for i in range(len(msg)):
            if A_key[i][0] == msg[i]:
                sifted_key_idx.append(1)
            else:
                sifted_key_idx.append(0)
        # print("Sifted key mask: ", sifted_key_idx)
        Snd.sendClassical("Node" + str(dest), sifted_key_idx)

        for i in range(len(sifted_key_idx)):
            if sifted_key_idx[i] == 1:
                sifted_key.append(A_key[i][1])
        print("Sifted key: ", sifted_key)
        print("Sifted key length: ", len(sifted_key))
    sifted_key_f = sifted_key[:key_size]
    return sifted_key_f


def request_pairs(Src, size, dest):
    message = [0, src, dest, size]
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
    with CQCConnection("Node1") as Node1:
        key = create_key_snd(Node1)
        print_fancy(str(key))


main()
