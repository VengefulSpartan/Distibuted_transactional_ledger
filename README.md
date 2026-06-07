# Distributed Transactional Ledger (Raft Consensus)

A fault-tolerant, containerized distributed consensus engine built from scratch in standard Python. This project implements the core mechanics of the **Raft Consensus Algorithm**, featuring leader election, log replication, and durable state recovery via a custom Write-Ahead Log (WAL).

## 🧠 System Architecture

This ledger operates without a central database, utilizing a cluster of independent nodes communicating over raw UDP sockets. 
* **Consensus:** Nodes dynamically elect a Leader using randomized timeout intervals to prevent split votes.
* **Fault Tolerance:** If the Leader crashes, Followers detect the missing heartbeats and automatically initiate a new election.
* **Data Durability:** Every state change (votes, log appends) is carved into a physical Write-Ahead Log (`wal.txt`). Operating system buffers are explicitly bypassed using `os.fsync()` to guarantee survival against hard power failures.
* **Containerization:** The cluster is orchestrated using Docker Compose, providing isolated environments and internal DNS resolution.

## 🚀 Tech Stack
* **Language:** Python 3.9 (No external libraries/dependencies)
* **Networking:** UDP Sockets (`socket`), Multi-threading
* **Storage:** Custom File I/O (Write-Ahead Logging)
* **Infrastructure:** Docker, Docker Compose

---

## 🛠️ Quick Start (Running the Cluster)

### Prerequisites
* Docker and Docker Compose installed on your machine.

### 1. Boot the Cluster
Clone the repository and spin up the 4-node virtual network in detached mode:
```bash
docker compose up --build -d