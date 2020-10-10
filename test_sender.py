from random import randrange

from cqc.pythonLib import CQCConnection, qubit

N = 10  # Number of paired qubits
key_size = 56
q_arr = []
src = 1
dest = 2


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
    with CQCConnection("Node1") as Snd:
        request_pairs(Snd, N, 2)
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
        Snd.sendClassical("Node"+str(dest), msg)


main()
