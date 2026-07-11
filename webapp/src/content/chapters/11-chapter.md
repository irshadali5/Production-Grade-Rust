---
title: "Intensive Deep Dive: Cryptographic Timing Attacks & Argon2id"
description: "Intensive deep dive for chapter 11"
order: 11
---


## 1. The Hardware Reality of Cryptographic Hashing



In legacy systems, passwords were hashed using MD5, SHA-1, or SHA-256. These algorithms were designed by the NSA to maximize throughput for data integrity checks. This speed is their fatal flaw when used for authentication. A modern NVIDIA H100 GPU contains over 14,000 CUDA cores. A cluster of these GPUs can calculate hundreds of billions of SHA-256 hashes per second.


If an attacker exfiltrates your database through an SQL injection, they do not need to "decrypt" the passwords. They will simply run a brute-force dictionary attack against the hashes. Because SHA-256 is purely CPU-bound, the attacker's specialized GPU ASICs will crack 99% of your users' passwords in a matter of hours.

## 2. Memory-Hard Functions: The Argon2id Algorithm



To mathematically bankrupt attackers, we must abandon CPU-bound hashing and embrace **Memory-Hard Functions**. We utilize **Argon2id**, the winner of the Password Hashing Competition. Argon2id defeats GPUs not by being mathematically complex, but by monopolizing physical RAM bandwidth.


The algorithm initializes a massive, customizable block of memory (e.g., a 64 Megabyte matrix). It iteratively fills this memory with pseudorandom data, and then executes highly unpredictable memory reads and writes across the entire block. Because GPUs have thousands of cores but severely limited VRAM (e.g., 80 GB), an attacker can only execute a few hundred concurrent Argon2id hashes before physically running out of memory. By tuning the memory cost parameter in Rust, we completely neutralize multi-million dollar GPU cracking rigs.


Crucially, Argon2id is a hybrid algorithm. The `d` variant provides data-independent memory access (defending against side-channel cache attacks), while the `i` variant provides data-dependent access (defending against ASICs). `Argon2id` combines both for ultimate security.

## 3. The Physics of Side-Channel Timing Attacks



Once a password is hashed, it must be verified against the stored hash in the database. A junior developer will use a standard string comparison: `if input_hash == db_hash`. This compiles down to the `memcmp` CPU instruction.


`memcmp` is optimized for speed. It compares the arrays byte-by-byte from left to right. The absolute microsecond it detects a mismatch (e.g., the first character is wrong), it instantly aborts the loop and returns `false`. This early-abort optimization introduces a catastrophic cryptographic vulnerability: a **Side-Channel Timing Attack**.


If the attacker guesses the first character correctly, the CPU must process the second character, which takes slightly longer. An attacker can send 10,000 HTTP requests, measuring the server's response time down to the nanosecond. By performing statistical regression on the network jitter, the attacker can literally guess the password character-by-character based entirely on microscopic fluctuations in CPU latency.

## 4. Constant-Time Bitwise Verification



We eliminate this mathematically using **Constant-Time Algorithms** provided by the `subtle` crate. A constant-time check does not use `if` statements or early returns. It iterates through *every single byte* of the hash array, performing a bitwise XOR (`^`) between the input byte and the database byte.


It accumulates the results using a bitwise OR (`|`) into a single integer flag. Only at the very end of the loop is the flag evaluated. Whether the attacker guessed 0 characters correctly or 31 characters correctly, the CPU executes the exact same number of instructions, traversing the exact same memory pathways, consuming the exact same number of clock cycles.


By forcing the execution time to be mathematically identical across all inputs, we physically sever the side-channel, rendering statistical latency analysis utterly useless.
