# Production-Grade Rust: Hyperscale Architecture

## What is this?

**Production-Grade Rust** is an intensive, deep-dive technical book and architectural reference guide designed to bridge the gap between "learning Rust" and "deploying Rust at global scale". It goes far beyond standard syntax tutorials, exploring the absolute physical limits of hardware, the intricacies of the Linux kernel, and the mathematical physics behind distributed systems.

This repository contains the complete content of the book, structured as a modern web application. The book is comprised of 37 chapters (00 to 36), ending with four comprehensive Capstone Projects that tie the advanced theories into deployable, production-ready code architectures.

## Why was this created?

Most Rust tutorials end with building a simple HTTP server or a CLI tool. They teach you how to make the compiler happy, but they don't teach you how to survive a 10-million-packet-per-second volumetric DDoS attack, or how to avoid Thread Starvation in the Tokio async runtime, or why your Kubernetes `cgroups` are randomly OOM-killing your perfectly healthy application due to the Linux Page Cache.

This project was built because **architectural intuition cannot be learned from syntax guides.** It must be learned by exploring the brutal realities of production:

- Why GraphQL N+1 queries mathematically destroy database connection pools.
- Why UUIDv7 is physically required to prevent B-Tree fragmentation in Postgres.
- Why the V8 Javascript engine's memory model fundamentally clashes with WebAssembly Linear Memory.
- How to achieve Zero-Copy Kernel Bypassing using `io_uring` and `eBPF`.

We wanted to create a resource that treats software engineering not just as code, but as **Mathematical Physics applied to Silicon**.

## Architecture & Core Concepts

This book dissects the entire modern hyperscale stack, treating Rust as the ultimate systems language to interface with:

1. **Network Physics & Load Balancing**: TCP/UDP protocols, Epoll/io_uring, BGP Anycast, and the Thundering Herd problem.
2. **Distributed Data & Consensus**: Raft distributed consensus, Redis LUA atomic pipelining, Bloom Filters, and HNSW Vector Graph navigation.
3. **The Kernel Boundary (eBPF & WASM)**: Hooking into the XDP network layer with eBPF, and executing untrusted code securely using WASI capability-based sandboxing.
4. **Silicon Isolation (MicroVMs)**: Booting Firecracker MicroVMs in 125ms and understanding KVM Extended Page Tables (EPT).
5. **Observability & Determinism**: Profiling CPU hardware using `perf` Flamegraphs, and mathematically enforcing CI/CD Directed Acyclic Graphs (DAGs).

## Book Layout & Format

The content is structured to progressively build your architectural intuition from foundational infrastructure up to advanced AI integration and low-level kernel hacking.

Every single chapter strictly adheres to the following intensive format:

1. **Core Concept Exploration**: A deep dive into the theoretical and physical mechanics of a technology.
2. **Mermaid Architecture Diagrams**: Beautiful, visual representations of data flow, memory layouts, and system topologies.
3. **Rust Implementation**: Concrete, production-ready Rust code snippets demonstrating how to interface with the technology.
4. **Production Post-Mortem**: A real-world disaster scenario (e.g., Discord's 2023 outage, the NodeJS Left-Pad catastrophe) explaining how theoretical flaws manifest as million-dollar production failures.
5. **Advanced Mathematical Physics**: An exploration of the low-level silicon or mathematical realities behind the concept (e.g., AVX-512 SIMD vectorization, Big O of AST Traversal).
6. **The Architect's Challenge**: A complex, real-world puzzle designed to test your understanding of edge cases.
7. **Architectural Tradeoffs & Edge Cases**: A dedicated section injecting intensive analysis of system constraints, risks, and production best practices without pulling punches.

### Chapter Progression

- **Chapters 00 - 10**: The Foundations of Hyperscale (Async runtimes, CI/CD, Containerization, Database Physics).
- **Chapters 11 - 20**: Distributed Systems & Resilience (Raft, Circuit Breakers, Rate Limiting, Singleflight).
- **Chapters 21 - 32**: The Extreme Limits (eBPF, Firecracker, `io_uring`, HNSW Vectors, Hardware Profiling).
- **Chapters 33 - 36**: The Capstone Projects (Building a highly concurrent API Gateway, a distributed KV store, a Vector DB, and a Serverless WebAssembly Edge runtime).

## Getting Started

The book is served via a frontend web application located in the `webapp` directory.

To run the web app locally:

```bash
cd webapp
bun install
bun run dev
```

> **"Software engineering at scale is not about writing code; it is about mathematically managing the physical constraints of the universe."**
