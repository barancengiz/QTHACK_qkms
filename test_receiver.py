from random import randrange

from cqc.pythonLib import CQCConnection

N = 10  # Number of paired qubits
key_size = 56
sifted_key = []


def print_fancy(text):
    print("|" + "-" * (len(text) + 2) + "|")
    print("| " + text + " |")
    print("|" + "-" * (len(text) + 2) + "|")


def main():
    # Initialize the connection
    with CQCConnection("Node2") as Client:
        while len(sifted_key) < key_size:
            mess = Client.recvClassical()
            mess = list(mess)
            src = mess[0]
            is_alert = None
            if len(mess) == 1:
                is_alert = True
            if is_alert:
                pair_arr = []
                # Make an EPR pair with Alice
                for i in range(N):
                    pair_arr.append(Client.recvEPR())
                print("EPR pairs received")
                # Get lists of measurements
                data = Client.recvClassical()
                message = list(data)
                print("Message ", message)
                # Apply corrections
                for i in range(N):
                    a = message[i]
                    b = message[N + i]
                    if b == 1:
                        pair_arr[i].X()
                    if a == 1:
                        pair_arr[i].Z()

                # Choose random basis for each qubit at Bob's side and then measure all qubits according to those polarizations
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

                Client.sendClassical("Node" + str(src), [a for a, _ in B_key])
                msg = Client.recvClassical()
                msg = list(msg)
                # print("Sifted key mask: ", msg)
                for i in range(len(msg)):
                    if msg[i] == 1:
                        sifted_key.append(measurements[i])
                print("Sifted key: ", sifted_key)
            sifted_key_f = sifted_key[:key_size]
            print_fancy(str(sifted_key_f))


main()
