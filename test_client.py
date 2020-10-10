from cqc.pythonLib import CQCConnection

N = 10  # Number of paired qubits
key_size = 56
A_key = []


def main():
    # Initialize the connection
    with CQCConnection("Client") as Client:

        pair_arr = []
        # Make an EPR pair with Alice
        for i in range(N):
            pair_arr.append(Client.recvEPR())
            # Receive info about corrections

        # Get lists of measurements
        data = Client.recvClassical()
        message = list(data)
        print("Message ", message)
        # Apply corrections
        for i in range(N):
            a = message[i]
            b = message[N+i]
            if b == 1:
                pair_arr[i].X()
            if a == 1:
                pair_arr[i].Z()

        measurements = []
        # Measure qubit
        for i in range(N):
            measurements.append(pair_arr[i].measure())
        to_print = "App {}: Measurement outcome is: {}".format(Client.name, measurements)
        print("|" + "-" * (len(to_print) + 2) + "|")
        print("| " + to_print + " |")
        print("|" + "-" * (len(to_print) + 2) + "|")


main()
