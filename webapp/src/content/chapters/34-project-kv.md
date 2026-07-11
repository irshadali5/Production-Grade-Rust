---
title: "Project 2: Building a Distributed KV Store (Raft)"
description: "Intensive deep dive for chapter 34"
order: 34
---

## 1. The Architecture of Distributed State

For our second project, we will drop down into the storage layer. We will build a distributed, highly available Key-Value Database in Rust.

If you deploy a standard Hashmap in a Rust API, the data is completely lost when the server restarts or crashes. To make it persistent, we must write the data to a physical disk. However, if that physical disk is destroyed in a fire, the data is still lost. True production systems must distribute state across multiple physical servers simultaneously. We will implement the **Raft Consensus Algorithm** to ensure all servers agree on the data, even during massive network partitions.

```mermaid
sequenceDiagram
    participant Client
    participant Leader as Leader Node (Rust)
    participant Follower1 as Follower Node A
    participant Follower2 as Follower Node B
    
    Client->>Leader: SET(key="user_1", val="foo")
    
    Note over Leader: 1. Write to local Write-Ahead Log (WAL)
    
    Leader->>Follower1: AppendEntries(Term 4, Log: [SET user_1])
    Leader->>Follower2: AppendEntries(Term 4, Log: [SET user_1])
    
    Follower1-->>Leader: Ack (Log Appended)
    
    Note over Leader: 2. Majority Achieved! (2 out of 3)
    Note over Leader: 3. Commit to memory HashMap
    
    Leader-->>Client: 200 OK
    Leader->>Follower2: Commit Notice
```

## 2. The Write-Ahead Log (WAL) Engine

The absolute most critical component of any database is the Write-Ahead Log (WAL). Before the Rust Leader node updates its in-memory Hashmap, it must append the command to a physical file on the NVMe disk. If the server loses power exactly 1 microsecond after replying to the client, the data is safe on disk.

```rust
// src/db/wal.rs
use tokio::fs::{File, OpenOptions};
use tokio::io::{AsyncWriteExt, BufWriter};

pub struct WriteAheadLog {
    file: BufWriter<File>,
}

impl WriteAheadLog {
    pub async fn new(path: &str) -> Self {
        // We open the file in Append-Only mode. We never overwrite data.
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .await
            .unwrap();
            
        WriteAheadLog {
            file: BufWriter::new(file),
        }
    }

    pub async fn append_entry(&mut self, term: u64, command: &str) {
        // 1. Serialize the Raft Entry
        let payload = format!("{}|{}\n", term, command);
        
        // 2. Write to the OS Memory Buffer (Fast, but not safe)
        self.file.write_all(payload.as_bytes()).await.unwrap();
        
        // 3. The fsync system call: This blocks until the physical SSD controller 
        // mathematically guarantees the electrons are stored in the NAND flash gates.
        self.file.flush().await.unwrap();
        self.file.get_mut().sync_data().await.unwrap();
    }
}
```

## 3. The Raft State Machine in Rust

Handling the Raft state transitions (Follower -> Candidate -> Leader) requires absolute precision. We use Rust's powerful `enum` system to map the exact theoretical states of the Raft whitepaper.

```rust
// src/db/raft.rs
use std::collections::HashMap;

// The strict mathematical states of a Raft node
enum RaftState {
    Follower,
    Candidate,
    Leader,
}

pub struct RaftNode {
    state: RaftState,
    current_term: u64,
    voted_for: Option<String>,
    // The actual database engine (The State Machine)
    state_machine: HashMap<String, String>,
}

impl RaftNode {
    pub fn handle_heartbeat_timeout(&mut self) {
        // If the Leader crashes and stops sending heartbeats, 
        // this Follower promotes itself to a Candidate and triggers an election.
        if let RaftState::Follower = self.state {
            self.state = RaftState::Candidate;
            self.current_term += 1;
            self.voted_for = Some("self".to_string());
            
            println!("Leader timeout! Starting election for Term {}", self.current_term);
            // ... broadcast RequestVote RPCs to other nodes ...
        }
    }
}
```

By combining a physical Write-Ahead Log (`fsync`) with the distributed mathematics of the Raft protocol, we have built a data storage engine capable of surviving catastrophic hardware failures with zero data loss.
