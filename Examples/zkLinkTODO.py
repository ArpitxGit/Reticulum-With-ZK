###########################################################################################################
#### TODOs for zkLINk ####
# Part	      |    Code Section	                                 | What to Implement
# ZK Proof	  | client_loop() (before prompt)	                   | Replace zkproof:valid with an actual ZK proof string
# ZK Verify	  | server_receive_initial_proof()                   | Verify the ZK proof based on your scheme
# Secure Flow |	client_connected() → server_packet_received()	   | Only allow general messaging after ZK pass
###########################################################################################################



import os
import sys
import time
import argparse
import RNS

APP_NAME = "example_utilities"

##########################################################
#### Server Part #########################################
##########################################################

latest_client_link = None

def server(configpath):
    reticulum = RNS.Reticulum(configpath)
    server_identity = RNS.Identity()
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "linkexample"
    )
    server_destination.set_link_established_callback(client_connected)
    server_loop(server_destination)

def server_loop(destination):
    RNS.log("Link example "+RNS.prettyhexrep(destination.hash)+" running, waiting for a connection.")
    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")
    while True:
        entered = input()
        destination.announce()
        RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))

def client_connected(link):
    global latest_client_link
    RNS.log("Client connected")
    link.set_link_closed_callback(client_disconnected)

    # TODO [SERVER]: Wait for proof in first packet and verify it before allowing any more interaction
    # Set packet callback to receive the first ZK proof packet from the client
    link.set_packet_callback(server_receive_initial_proof)
    latest_client_link = link

def client_disconnected(link):
    RNS.log("Client disconnected")

# This function handles the first proof packet from the client
def server_receive_initial_proof(message, packet):
    global latest_client_link
    text = message.decode("utf-8")
    RNS.log("Received initial data on the link: "+text)

    # TODO [SERVER]: Add actual ZK proof verification logic here
    # Example (placeholder):
    if text == "zkproof:valid":
        RNS.log("ZK proof verified successfully.")
        reply = "ZK verified ✅. You may send data."
        latest_client_link.set_packet_callback(server_packet_received)  # enable full comms
    else:
        RNS.log("ZK proof verification failed.")
        reply = "ZK failed ❌. Closing link."
        latest_client_link.teardown()

    RNS.Packet(latest_client_link, reply.encode("utf-8")).send()

def server_packet_received(message, packet):
    text = message.decode("utf-8")
    RNS.log("Received data on the link: "+text)
    reply_text = "I received \""+text+"\" over the link"
    RNS.Packet(latest_client_link, reply_text.encode("utf-8")).send()

##########################################################
#### Client Part #########################################
##########################################################

server_link = None

def client(destination_hexhash, configpath):
    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
        if len(destination_hexhash) != dest_len:
            raise ValueError("Destination length is invalid...")
        destination_hash = bytes.fromhex(destination_hexhash)
    except:
        RNS.log("Invalid destination entered. Check your input!\n")
        sys.exit(0)

    reticulum = RNS.Reticulum(configpath)

    if not RNS.Transport.has_path(destination_hash):
        RNS.log("Destination is not yet known. Requesting path and waiting for announce to arrive...")
        RNS.Transport.request_path(destination_hash)
        while not RNS.Transport.has_path(destination_hash):
            time.sleep(0.1)

    server_identity = RNS.Identity.recall(destination_hash)

    RNS.log("Establishing link with server...")

    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "linkexample"
    )

    link = RNS.Link(server_destination)
    link.set_packet_callback(client_packet_received)
    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    # TODO [CLIENT]: Send initial proof after link established
    global server_link
    server_link = link

    client_loop()

def client_loop():
    global server_link
    while not server_link:
        time.sleep(0.1)

    # TODO [CLIENT]: Send ZK proof before user input is allowed
    try:
        # Simulated ZK proof step
        # TODO: Replace with actual ZK generation (e.g., hash(secret + nonce))
        zk_proof = "zkproof:valid"
        RNS.Packet(server_link, zk_proof.encode("utf-8")).send()
    except Exception as e:
        RNS.log("Failed to send ZK proof: "+str(e))
        server_link.teardown()
        sys.exit(0)

    should_quit = False
    while not should_quit:
        try:
            print("> ", end=" ")
            text = input()

            if text in ["quit", "q", "exit"]:
                should_quit = True
                server_link.teardown()

            if text != "":
                data = text.encode("utf-8")
                if len(data) <= RNS.Link.MDU:
                    RNS.Packet(server_link, data).send()
                else:
                    RNS.log("Data exceeds MDU.", RNS.LOG_ERROR)

        except Exception as e:
            RNS.log("Error while sending data over the link: "+str(e))
            should_quit = True
            server_link.teardown()

def link_established(link):
    global server_link
    server_link = link
    RNS.log("Link established with server")

def link_closed(link):
    if link.teardown_reason == RNS.Link.TIMEOUT:
        RNS.log("The link timed out, exiting now")
    elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
        RNS.log("The link was closed by the server, exiting now")
    else:
        RNS.log("Link closed, exiting now")
    time.sleep(1.5)
    sys.exit(0)

def client_packet_received(message, packet):
    text = message.decode("utf-8")
    RNS.log("Received data on the link: "+text)
    print("> ", end=" ")
    sys.stdout.flush()

# ... [Unchanged main entrypoint] ...
##########################################################
#### Program Startup #####################################
##########################################################

# This part of the program runs at startup,
# and parses input of from the user, and then
# starts up the desired program mode.
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple link example")

        parser.add_argument(
            "-s",
            "--server",
            action="store_true",
            help="wait for incoming link requests from clients"
        )

        parser.add_argument(
            "--config",
            action="store",
            default=None,
            help="path to alternative Reticulum config directory",
            type=str
        )

        parser.add_argument(
            "destination",
            nargs="?",
            default=None,
            help="hexadecimal hash of the server destination",
            type=str
        )

        args = parser.parse_args()

        if args.config:
            configarg = args.config
        else:
            configarg = None

        if args.server:
            server(configarg)
        else:
            if (args.destination == None):
                print("")
                parser.print_help()
                print("")
            else:
                client(args.destination, configarg)

    except KeyboardInterrupt:
        print("")
        sys.exit(0)