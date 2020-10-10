from cqc.pythonLib import CQCConnection, qubit

N = 10  # Number of paired qubits
from random import randrange

key_size = 56
A_key = []


def main():
    for i in range(N):
        A_key.append([randrange(2), randrange(2)])  # Basis, Key pair
    print("KEY: ", [a for _, a in A_key])
    # Initialize the connection
    with CQCConnection("Server") as Server:

        pair_arr = []
        q_arr = []
        # Make an EPR pair with Bob
        for i in range(N):
            pair_arr.append(Server.createEPR("Client"))
            print("{} Pairs created".format((i + 1) * 2))

        for i in range(N):
            # Create a qubit_arr to teleport
            q = qubit(Server)

            # Prepare the qubit to teleport in |+>
            # q.H()
            if A_key[i][1] == 1:
                q.X()
            # Apply the local teleportation operations
            q.cnot(pair_arr[i])
            q.H()
            q_arr.append(q)
            print("{} Qubits created".format((i + 1) * 2))

        measurements_a = []
        measurements_b = []

        for i in range(N):
            # Measure the qubits
            measurements_a.append(q_arr[i].measure())
            measurements_b.append(pair_arr[i].measure())
        to_print = "App {}: Measurement outcomes are: a={}, b={}".format(Server.name, measurements_a, measurements_b)
        print("|" + "-" * (len(to_print) + 2) + "|")
        print("| " + to_print + " |")
        print("|" + "-" * (len(to_print) + 2) + "|")

        # str_a = ''.join(str(x) for x in measurements_a)
        #
        # str_b = ''.join(str(x) for x in measurements_b)
        # Send corrections to Bob

        # int_a = 0
        # int_b = 0
        # for i in range(N):
        #     int_a = 2 * int_a + measurements_a[i]
        #     int_b = 2 * int_b + measurements_b[i]
        msg = []
        msg.extend(measurements_a)
        msg.extend(measurements_b)
        Server.sendClassical("Client", msg)
        for i in range(N):
            Server.sendQubit(pair_arr[i], "rcv")


##################################################################################################
main()
