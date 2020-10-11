from cqc.pythonLib import CQCConnection


def node_map(number):
    if number == 0:
        return "Server"
    else:
        return "Node" + str(number)


def main():
    # Initialize the connection
    N = 0  # Number of qubit pairs
    source = 0
    with CQCConnection("Server") as Server:
        while True:
            # Get required pair size
            request = Server.recvClassical()
            request_type = request[0]
            source = node_map(request[1])+"s"
            destination = node_map(request[2])+"r"
            N = request[3]
            if N < 1:
                print("Error: Invalid number of pairs {}".format(N))
                exit(0)
            # Request Approved
            # print("Request Approved")
            Server.sendClassical(source, 1)
            # print("Response sent to source")
            Server.sendClassical(destination, request[1])
            # print("Response sent to destination")

            # Type0: Make pair
            if request_type == 0:

                pair_arr = []
                # Create EPR pairs, 2*size qubits
                # Split pairs and send to source node
                for i in range(N):
                    pair_arr.append(Server.createEPR(destination))
                    print("{} Pairs created".format((i + 1) * 2))

                # Send remaining qubits to destination node
                for i in range(N):
                    Server.sendQubit(pair_arr[i], source)


##################################################################################################
main()
