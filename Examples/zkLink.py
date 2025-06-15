##########################################################
# on the way to use no/zero knowledge system in Link and make it zk Link #
# example: simple SHA256-based challenge-response #
# mock zero-knowledge authentication demo using Reticulum #
##########################################################

import os
import sys
import time
import argparse
import random
import string
import hashlib
import RNS

APP_NAME = "example_utilities"

# Shared secret for mock zero-knowledge proof (must be known by both client and server)
SHARED_SECRET = "ThrasherThrashingThrashers"

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
        "zklinkexample"
    )

    server_destination.set_link_established_callback(client_connected)
    server_loop(server_destination)

def server_loop(destination):
    RNS.log(
        "zkLink example "+
        RNS.prettyhexrep(destination.hash)+
        " running, waiting for a connection."
    )
    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")

    while True:
        entered = input()
        destination.announce()
        RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))

def client_connected(link):
    global latest_client_link
    RNS.log("Client connected")
    link.set_link_closed_callback(client_disconnected)

    # Step 1: Server sends nonce challenge for mock ZK proof
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    link.nonce_challenge = nonce  # save challenge on link object
    RNS.Packet(link, f"challenge:{nonce}".encode("utf-8")).send()

    # Set callback to verify client's proof response
    link.set_packet_callback(server_verify_proof)

    latest_client_link = link

def server_verify_proof(message, packet):
    global latest_client_link
    proof = message.decode("utf-8")

    expected_hash = hashlib.sha256(
        (SHARED_SECRET + latest_client_link.nonce_challenge).encode()
    ).hexdigest()

    if proof == expected_hash:
        RNS.log("✅ Client proof verified.")
        RNS.Packet(latest_client_link, "ZK OK".encode("utf-8")).send()

        # Unlock full messaging after successful proof
        latest_client_link.set_packet_callback(server_packet_received)
    else:
        RNS.log("❌ Client proof failed.")
        RNS.Packet(latest_client_link, "ZK FAIL".encode("utf-8")).send()
        latest_client_link.teardown()

def client_disconnected(link):
    RNS.log("Client disconnected")

def server_packet_received(message, packet):
    global latest_client_link
    text = message.decode("utf-8")
    RNS.log("Received data on the link: "+text)

    reply_text = "I received \""+text+"\" over the link"
    reply_data = reply_text.encode("utf-8")
    RNS.Packet(latest_client_link, reply_data).send()

##########################################################
#### Client Part #########################################
##########################################################

server_link = None

def client(destination_hexhash, configpath):
    global server_link

    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
        if len(destination_hexhash) != dest_len:
            raise ValueError(
                f"Destination length invalid, must be {dest_len} hex chars ({dest_len//2} bytes)."
            )
        destination_hash = bytes.fromhex(destination_hexhash)
    except:
        RNS.log("Invalid destination entered. Check your input!\n")
        sys.exit(0)

    reticulum = RNS.Reticulum(configpath)

    if not RNS.Transport.has_path(destination_hash):
        RNS.log("Destination not known yet. Requesting path and waiting for announce...")
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
        "zklinkexample"
    )

    link = RNS.Link(server_destination)
    link.set_packet_callback(client_packet_received)
    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    client_loop()

def client_loop():
    global server_link

    # Wait for the link to become active
    while not server_link:
        time.sleep(0.1)

    # Wait for challenge from server
    challenge = None
    while not challenge:
        if hasattr(server_link, "zk_challenge"):
            challenge = server_link.zk_challenge
        time.sleep(0.1)

    # Generate proof for challenge
    proof = hashlib.sha256((SHARED_SECRET + challenge).encode("utf-8")).hexdigest()
    RNS.Packet(server_link, proof.encode("utf-8")).send()

    should_quit = False
    while not should_quit:
        try:
            print("> ", end=" ")
            text = input()

            if text.lower() in ("quit", "q", "exit"):
                should_quit = True
                server_link.teardown()

            if text != "":
                data = text.encode("utf-8")
                if len(data) <= RNS.Link.MDU:
                    RNS.Packet(server_link, data).send()
                else:
                    RNS.log(
                        f"Cannot send this packet, size {len(data)} exceeds MDU {RNS.Link.MDU}",
                        RNS.LOG_ERROR
                    )

        except Exception as e:
            RNS.log("Error while sending data over the link: "+str(e))
            should_quit = True
            server_link.teardown()

def link_established(link):
    global server_link
    server_link = link
    RNS.log('Link established with server, waiting for ZK challenge...')

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
    global server_link
    text = message.decode("utf-8")

    if text.startswith("challenge:"):
        server_link.zk_challenge = text.split("challenge:")[1]
        RNS.log("Received ZK challenge: "+server_link.zk_challenge)
    elif text == "ZK OK":
        RNS.log("Server verified proof. You can now send messages.")
        print("> ", end=" ")
        sys.stdout.flush()
    elif text == "ZK FAIL":
        RNS.log("Server rejected proof. Disconnecting.")
        server_link.teardown()
    else:
        RNS.log("Received data on the link: "+text)
        print("> ", end=" ")
        sys.stdout.flush()

##########################################################
#### Program Startup #####################################
##########################################################

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple zkLink example")

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

        configarg = args.config if args.config else None

        if args.server:
            server(configarg)
        else:
            if args.destination is None:
                print("")
                parser.print_help()
                print("")
            else:
                client(args.destination, configarg)

    except KeyboardInterrupt:
        print("")
        sys.exit(0)
