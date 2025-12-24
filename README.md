# Raft Consensus Algorithm Implementation (Python)

A lightweight, educational implementation of the **Raft Distributed Consensus Algorithm** in Python. This project demonstrates how distributed nodes communicate, elect a leader, and maintain log consistency using Remote Procedure Calls (RPCs).

## 🚀 Features implemented
* **Leader Election:** Nodes utilize randomized election timeouts to elect a leader safely.
* **Heartbeats:** The Leader sends periodic heartbeats (`APPEND_ENTRIES`) to maintain authority and prevent new elections.
* **Log Replication Logic:** Basic structure for appending log entries and checking consistency (Term/Index matching).
* **RPC Simulation:** Custom `Transport` class simulating network message passing via sockets.
* **Fault Tolerance:** Nodes automatically recover and start new elections if the Leader "dies" (process is stopped).

## 📂 Project Structure

* **`node.py`**: The "Brain". Contains the `RaftNode` class with core logic (Candidate/Follower/Leader states, RequestVote, AppendEntries).
* **`transport.py`**: The "Mouth". Handles networking, socket creation, and sending JSON messages between nodes.
* **`main.py`**: The "Launcher". Initializes a node, connects the transport, and starts the election timer loop.

## 🛠️ Prerequisites
* Python 3.6+
* No external libraries required (uses standard `socket`, `threading`, `time`, `random`).

## ⚡ How to Run the Cluster

To see the consensus algorithm in action, you need to simulate a cluster by running **3 separate instances** of the application.

1.  **Open Terminal 1 (Node 1):**
    ```bash
    cd raft_core
    python main.py 1
    ```

2.  **Open Terminal 2 (Node 2):**
    ```bash
    cd raft_core
    python main.py 2
    ```

3.  **Open Terminal 3 (Node 3):**
    ```bash
    cd raft_core
    python main.py 3
    ```

### 🔍 What to expect
1.  **Initial State:** All nodes start as `Followers`.
2.  **Election:** One node will time out (random 2-4s), become a `Candidate`, and request votes.
3.  **Consensus:** Once a Candidate receives 2 votes (Majority), it becomes the **LEADER**.
4.  **Steady State:** The Leader will print `Sending heartbeat...` every 0.5s. Followers will reset their timers silently.
5.  **Failure Test:** Try closing the Leader's terminal (Ctrl+C). Watch one of the other nodes detect the silence and start a new election!

## 📝 Configuration
The node registry is currently hardcoded in `main.py` for local testing:
* **Node 1:** localhost:5001
* **Node 2:** localhost:5002
* **Node 3:** localhost:5003

## 📜 License
This project is for educational purposes. Feel free to fork and experiment!
