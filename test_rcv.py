from cqc.pythonLib import CQCConnection

N = 10  # Number of paired qubits
key_size = 56
A_key = []


def main():
    # Initialize the connection
    with CQCConnection("RCV") as Rcv:

        pair_arr = []
        # Receive qubits from the server
        for i in range(N):
            pair_arr.append(Rcv.recvQubit())

        for i in range(N):
            A_key.append(pair_arr[i].measure())

        to_print="Key: {}".format(A_key)

        print("|" + "-" * (len(to_print) + 2) + "|")
        print("| " + to_print + " |")
        print("|" + "-" * (len(to_print) + 2) + "|")


main()
