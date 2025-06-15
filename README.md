# Reticulum with ZK

The cryptography-based networking stack for building unstoppable networks with LoRa, Packet Radio, WiFi and everything in between with Zero Knowledge Support.

# Notable Characteristics

While Reticulum solves the same problem that any network stack does, namely to get data reliably from one point to another over a number of intermediaries, it does so in a way that is very different from other networking technologies.

- Reticulum does not use source addresses. No packets transmitted include information about the address, place, machine or person they originated from.
- There is no central control over the address space in Reticulum. Anyone can allocate as many addresses as they need, when they need them.
- Reticulum ensures end-to-end connectivity. Newly generated addresses become globally reachable in a matter of seconds to a few minutes.
- Addresses are self-sovereign and portable. Once an address has been created, it can be moved physically to another place in the network, and continue to be reachable.
- All communication is secured with strong, modern encryption by default.
- All encryption keys are ephemeral, and communication offers forward secrecy by default.
- It is not possible to establish unencrypted links in Reticulum networks.
- It is not possible to send unencrypted packets to any destinations in the network.
- Destinations receiving unencrypted packets will drop them as invalid.

## Supported on

- Android, ARM64 , Debian, Bookworm, MacOS, OpenWRT, Raspberry, Pi , RISC-V, Ubuntu Lunar, Windows . .

# Prerequisite

[Setup Reticulum](https://reticulum.network/manual/gettingstartedfast.html) and have it running on your preffered device.

## Reticulum allows you to [create your own applications](https://reticulum.network/manual/examples.html#), can get started with:

### Basic example is Minimal.py

`running, https://github.com/markqvist/Reticulum/blob/master/Examples/Minimal.py`

In **Reticulum**, the **Peer ID** ( shown in your log):

```
Minimal example <PEER-ID> running...
```

is a **shortened public identity hash** that uniquely identifies your node (or specifically, the destination endpoint in that script).

- It’s a **cryptographic hash** of the **destination identity** (public key) generated for the script using Reticulum.
- Every `Destination` in Reticulum has a long-term **asymmetric identity**, which is derived from a keypair and used for:
  - Addressing
  - Authentication
  - Encryption
- This peer ID is a short **fingerprint** of that identity and used for discovery, routing, and debugging.

- Snippet

```python
destination = Destination(reticulum_instance, "minimal.example", Destination.IN, "example", None)
print("Minimal example", destination.hex_hash(), "running...")
```

Here:

- `"minimal.example"` is the **destination name**
- `hex_hash()` returns a **16-byte hex** string of the destination’s hash (your peer ID)

### you can try all:

- Minimal
- Announce
- Broadcast
- Echo
- Link
- Identification
- Requests & Responses
- Channel
- Buffer
- Filetransfer
- Custom Interfaces

# Cryptography Primitives Supported

- Ed25519 for signatures
- X22519 for ECDH key exchanges
- HKDF for key derivation
- AES-256 in CBC mode
- HMAC-SHA256 for message authentication
- SHA-256
- SHA-512

[more detail](https://reticulum.network/crypto.html) ...

# ZK in Reticulum

## Link.py : Exisiting

![image](https://github.com/ArpitxGit/Reticulum-With-ZK/blob/ZK/Assets/Link.png)

1. T1 (Server):

- waited for a connection and received "Hey Y0" over a secure link.

2. T2 (Client):

- Requested path discovery.
- Linked with server.
- Sent "Hey Yo".

This means: Reticulum is announcing, discovering, and linking as expected.

Both nodes can exchange application-level data.

## zkLink.py : Hacked

### Concept:

- Client holds a shared_secret.
- Server issues a nonce challenge (random string).
- Client replies with SHA256(shared_secret + nonce).
- Server verifies it by recomputing the same.

**mock version using SHA256-based challenge-response logic**

![image](https://github.com/ArpitxGit/Reticulum-With-ZK/blob/ZK/Assets/zkLink.png)

- Server sends nonce challenge →
- Client replies with correct SHA256 proof →
- Server accepts proof and unlocks messaging →
- Messages sent/received as expected.

The logs show:

- ✅ Proof verification success on server side
- Client sends messages → Server receives it
- Server sends back confirmation reply → Client receives it
- Then link eventually closes cleanly.

# Future Programmable Work

## zkLinkTODO.py

Part | Code Section | What to Implement

ZK Proof | client_loop() (before prompt) | Replace zkproof:valid with an actual ZK proof string

ZK Verify | server_receive_initial_proof() | Verify the ZK proof based on your scheme

Secure Flow | client_connected() → server_packet_received() | Only allow general messaging after ZK pass

# Mobile Economy 5G GSMA

![image](https://github.com/ArpitxGit/Reticulum-With-ZK/blob/ZK/Assets/Mobile-Economy-2025-GSMA.png)

# Subscriber & Tech Trends

![image](https://github.com/ArpitxGit/Reticulum-With-ZK/blob/ZK/Assets/Sub&Tech-Trends.png)

# ZK in Telco

![image](https://github.com/ArpitxGit/Reticulum-With-ZK/blob/ZK/Assets/zkInTelco.png)

# Network Slicing

- [Network Slicing : SoK](https://dungexn.notion.site/Network-Slicing-SoK-2130fed242918041b46cddf6aac01e67?source=copy_link)
- [Network Slicing : Tech Stack](https://dungexn.notion.site/Network-Slicing-Tech-Stack-2130fed2429180e686ccc3765e07ed87?source=copy_link)
- [Nokio vs Ericsson](https://dungexn.notion.site/NOKIO-vs-Ericsson-2130fed2429180278fabdc091ef67878?source=copy_link)
- [Global Tech Stack Comparison](https://dungexn.notion.site/Network-Slicing-Tech-Comparison-2130fed2429180469a5ec81a6d11b7ba?source=copy_link)
