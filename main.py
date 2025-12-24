import sys
import time
import threading

# Import your classes
# Assuming your node code is in 'node.py' and transport in 'transport.py'
from node import raftNode
from transport import Transport


def start_node(node_id):
    # -------------------------------------------------
    # 1. CONFIGURATION ("The Phonebook")
    # -------------------------------------------------
    # Map Node IDs to Ports
    registry = {
        1: 5001,
        2: 5002,
        3: 5003
    }

    if node_id not in registry:
        print(f"Error: Node ID {node_id} not found in registry.")
        return

    my_port = registry[node_id]
    my_address = ('localhost', my_port)

    # Calculate Peers (Everyone who is NOT me)
    peers = []
    for n_id, p_port in registry.items():
        if n_id != node_id:
            peers.append(('localhost', p_port))

    print(f"[*] Node {node_id} starting on {my_address}")
    print(f"[*] Peers: {peers}")

    # -------------------------------------------------
    # 2. INITIALIZATION
    # -------------------------------------------------
    # Create the Brain
    node = raftNode(node_id)

    # Create the Network
    transport = Transport(my_address, node)

    # Wire them together
    node.set_transport(transport)
    node.peers = peers

    # -------------------------------------------------
    # 3. START ENGINE
    # -------------------------------------------------
    # Start the Election Timer in a background thread
    # (So it doesn't block the main program)
    t = threading.Thread(target=node.run_election_timer, daemon=True)
    t.start()

    # Keep the main thread alive to listen for Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <node_id>")
        print("Example: python main.py 1")
    else:
        id = int(sys.argv[1])
        start_node(id)