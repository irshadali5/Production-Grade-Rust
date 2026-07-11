import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay_10 = """<section class="chapter" id="concurrency">
    <div class="chapter-label">Chapter 10</div>
    <h1>Intensive Deep Dive: Cache Lines & `loom` Permutations</h1>

    <h2>1. The Physics of the CPU Cache (L1/L2/L3)</h2>
    <p>When discussing concurrency, junior developers focus exclusively on software primitives: threads, Mutexes, and channels. True engineering mastery requires understanding the physical silicon. A modern CPU operates at roughly 4 GHz, executing an instruction every 0.25 nanoseconds. However, fetching data from main memory (RAM) takes roughly 100 nanoseconds. If the CPU had to wait for RAM on every instruction, it would sit idle for 99% of its lifespan.</p>
    <p>To solve this, hardware engineers surround the CPU cores with ultra-fast SRAM caches (L1, L2, L3). When a core requests data, it does not fetch a single byte; it fetches an entire <strong>Cache Line</strong> (typically 64 bytes). The CPU operates under the assumption of Spatial Locality: if you access index 0 of an array, you will probably access index 1 immediately after. By loading the entire 64-byte chunk into the L1 cache, subsequent accesses take less than 1 nanosecond.</p>

    <h2>2. The MESI Protocol & False Sharing</h2>
    <p>In a multi-core processor, each core has its own private L1 cache. This introduces a fatal distributed systems problem at the silicon level: <strong>Cache Coherence</strong>. If Core A modifies a variable in its L1 cache, and Core B tries to read that same variable from its L1 cache, Core B will read stale data.</p>
    <p>CPUs solve this using hardware consensus protocols, most notably the <strong>MESI Protocol (Modified, Exclusive, Shared, Invalid)</strong>. If Core A modifies a Cache Line, it broadcasts an "Invalidate" signal across the CPU's physical ring bus. Core B is forced to mark its copy of the Cache Line as Invalid, meaning it must pause execution and fetch the fresh data from the L3 cache or RAM.</p>
    <p>This leads to the deadliest performance killer in concurrent Rust: <strong>False Sharing</strong>. Imagine a struct containing two atomic counters: <code>struct Counters { a: AtomicUsize, b: AtomicUsize }</code>. This struct is 16 bytes, easily fitting into a single 64-byte Cache Line. If Thread A (on Core A) constantly increments <code>a</code>, and Thread B (on Core B) constantly increments <code>b</code>, they are modifying different variables. However, because both variables share the <em>same Cache Line</em>, Core A and Core B will continuously bombard each other with MESI Invalidate signals. The Cache Line will violently bounce back and forth across the physical silicon ring bus, degrading performance by over 1,000%.</p>
    <p>In Rust, we mathematically prevent False Sharing using the <code>#[repr(align(64))]</code> attribute. This forces the compiler to pad the struct so that each atomic variable resides on its own physical Cache Line, completely eliminating the hardware contention.</p>

    <h2>3. The `loom` Permutation Testing Engine</h2>
    <p>Writing lock-free data structures using atomic primitives is notoriously difficult. If two threads access an atomic variable using <code>Ordering::Relaxed</code>, the CPU is legally allowed to reorder the memory instructions, leading to mathematically impossible states that only manifest under extreme load.</p>
    <p>To prove our lock-free code is safe, standard <code>cargo test</code> is useless. A race condition might only occur in 1 out of 10 million executions. We use <strong>`loom`</strong>, a permutation testing tool developed by Tokio. <code>loom</code> intercepts all atomic memory accesses and threads. It systematically executes <em>every single mathematically possible interleaving</em> of your concurrent threads. If there is a one-in-a-billion sequence of CPU instructions that leads to a data race or a memory leak, <code>loom</code> will find it, halt execution, and print the exact interleaving trace. If your code passes <code>loom</code>, it is mathematically proven to be thread-safe.</p>
</section>"""

essay_11 = """<section class="chapter" id="auth">
    <div class="chapter-label">Chapter 11</div>
    <h1>Intensive Deep Dive: Cryptographic Timing Attacks</h1>

    <h2>1. The Hardware Reality of Hashing</h2>
    <p>In the early days of the web, passwords were hashed using MD5 or SHA-256. These algorithms were designed for cryptographic speed and integrity (e.g., verifying a file download). This speed is their fatal flaw. A modern NVIDIA GPU, utilizing its thousands of specialized CUDA cores, can calculate tens of billions of SHA-256 hashes per second. If an attacker steals your database, they can crack complex passwords using brute-force dictionary attacks in mere minutes.</p>

    <h2>2. Memory Hardness and Argon2id</h2>
    <p>To defend against GPUs and custom ASICs (Application-Specific Integrated Circuits), we must abandon CPU-bound hashing and embrace <strong>Memory-Hard Functions</strong>. We utilize <strong>Argon2id</strong>. Argon2id does not rely on complex mathematics; it relies on RAM exhaustion. The algorithm is designed to fill a massive, customizable block of memory (e.g., 64 Megabytes) with pseudorandom data, and then perform highly unpredictable reads and writes across that memory space.</p>
    <p>A GPU might have 10,000 cores, but it only has 16 GB of VRAM. If a single Argon2id calculation requires 64 MB of RAM, the GPU can only run 250 hashes in parallel, utterly destroying its brute-force advantage. By increasing the memory cost parameter in our Rust implementation, we mathematically bankrupt the attacker's hardware.</p>

    <h2>3. Side-Channel Timing Attacks</h2>
    <p>Once the password is hashed, we must verify it against the user's input. A naive Rust developer might compare the hashes using the standard equality operator (<code>hash1 == hash2</code>). Under the hood, this compiles to a standard string comparison algorithm (like <code>memcmp</code>). The algorithm compares the strings byte-by-byte, from left to right. The instant it finds a non-matching byte, it returns <code>false</code> and aborts.</p>
    <p>This early-abort optimization is a catastrophic cryptographic vulnerability known as a <strong>Side-Channel Timing Attack</strong>. If the user's input matches the first character, the server takes slightly longer to reject the password (because it had to check the second character). If it matches the first two characters, it takes even longer.</p>
    <p>An attacker can send thousands of requests, measuring the server's response time down to the microsecond. By statistically analyzing the microscopic latency variations, they can literally guess the password character-by-character, essentially playing a game of "Hot or Cold" with your server.</p>

    <h2>4. Constant-Time Verification</h2>
    <p>To mathematically defeat this, we must use <strong>Constant-Time Algorithms</strong> (like those provided by the <code>subtle</code> crate). A constant-time equality check performs a bitwise XOR (<code>^</code>) across <em>every single byte</em> of both strings, accumulating the differences into a bitmask using a bitwise OR (<code>|</code>). The loop never aborts early. Regardless of whether the password is completely wrong or perfectly correct, the CPU executes the exact same number of instructions, consuming the exact same number of clock cycles.</p>
    <p>By guaranteeing that the execution time is mathematically identical in all scenarios, we eliminate the side-channel entirely, rendering the attacker's statistical models useless.</p>
</section>"""

essay_12 = """<section class="chapter" id="workers">
    <div class="chapter-label">Chapter 12</div>
    <h1>Intensive Deep Dive: Distributed Consensus & Raft</h1>

    <h2>1. The Two Generals' Problem</h2>
    <p>In Chapter 12, we previously established that background workers must read from a Garnet Stream to avoid blocking the Tokio thread. However, managing distributed workers introduces one of the most notoriously difficult problems in computer science: Distributed Consensus, beautifully illustrated by the <strong>Two Generals' Problem</strong>.</p>
    <p>Imagine two generals on opposite sides of a valley, needing to coordinate an attack. General A sends a messenger: "Attack at dawn." General B receives it and sends an acknowledgment: "I will attack at dawn." However, General B knows the messenger might have been captured on the return trip. If General A never received the acknowledgment, A will not attack, and B will be slaughtered. Therefore, General A must send a confirmation of the acknowledgment. But then A worries <em>that</em> messenger was captured. This infinite regression proves that perfect consensus over an unreliable network (TCP/IP) is mathematically impossible.</p>

    <h2>2. The Raft Consensus Algorithm</h2>
    <p>In our hyperscale architecture, if the primary Garnet cache node crashes, the cluster must promote a standby node to primary. If there is a network partition (a "split-brain"), and two nodes both think they are the primary, they will accept conflicting data, destroying the integrity of the system.</p>
    <p>Garnet and modern distributed systems solve this using the <strong>Raft Consensus Algorithm</strong>. Raft relies on the concept of a <strong>Quorum</strong> (a strict majority). If a cluster has 5 nodes, 3 nodes form a quorum. Raft enforces that a node can only be elected Leader if it receives votes from a quorum. Because it is mathematically impossible for two different nodes to simultaneously acquire a majority in a 5-node cluster, a split-brain is permanently prevented.</p>

    <h2>3. Exactly-Once Delivery (PEL)</h2>
    <p>When our Rust workers consume from the Garnet Stream, we face another distributed challenge: ensuring a job (like charging a credit card) is executed <strong>Exactly-Once</strong>. Standard queues offer "At-Most-Once" (fire and forget) or "At-Least-Once" (retry until acknowledged).</p>
    <p>To achieve the illusion of Exactly-Once, we use Garnet Consumer Groups and the <strong>Pending Entries List (PEL)</strong>. When Worker A claims a job, the job is not deleted from the stream. Instead, it is moved to Worker A's PEL. The job remains in the PEL until Worker A sends an <code>XACK</code> (Acknowledge) command.</p>
    <p>If Worker A suffers a hardware failure (Kernel Panic) mid-execution, it will never send the <code>XACK</code>. A separate Rust supervisor task periodically issues the <code>XPENDING</code> command to Garnet, scanning for jobs that have been in a PEL for longer than 60 seconds without an acknowledgment. If it finds one, it issues the <code>XCLAIM</code> command, mathematically ripping the job away from the dead Worker A and assigning it to a healthy Worker B.</p>
    <p>Crucially, to prevent the credit card from being charged twice (if Worker A wasn't dead, but just delayed by a massive Garbage Collection pause), the actual Rust execution logic must be <strong>Idempotent</strong>. We use the database's unique constraints (e.g., <code>transaction_id</code>) to guarantee that even if Worker A and Worker B execute simultaneously, only one database commit will succeed, achieving flawless Exactly-Once semantics.</p>
</section>"""

essay_13 = """<section class="chapter" id="deploy">
    <div class="chapter-label">Chapter 13</div>
    <h1>Intensive Deep Dive: ELF Binaries & `musl` Static Linking</h1>

    <h2>1. The OS Kernel as an Attack Surface</h2>
    <p>A standard deployment strategy involves packaging the Rust binary into an Alpine or Debian Docker container. However, developers often misunderstand what a container actually is. A Docker container is not a Virtual Machine. It does not have its own OS kernel. It is merely an isolated process running on the host machine's Linux kernel, restricted by <code>cgroups</code> and <code>namespaces</code>.</p>
    <p>If you deploy a Debian container, you are including a massive filesystem containing thousands of binaries: <code>bash</code>, <code>curl</code>, <code>apt</code>, <code>grep</code>, and <code>python</code>. If a hacker exploits a vulnerability in your Rust application (perhaps via a malformed image parsing crate), they can achieve Remote Code Execution (RCE). The hacker will instantly drop into a <code>bash</code> shell, use <code>curl</code> to download malware from their server, and execute it using the tools you conveniently provided in the Debian filesystem.</p>

    <h2>2. The ELF Format and Dynamic Linking (`glibc`)</h2>
    <p>To mitigate this, we deploy to a <code>scratch</code> image—a Docker image containing literally 0 bytes. No shell, no curl, nothing. However, if you compile your Rust code and place it in a scratch image, it will instantly crash upon execution.</p>
    <p>Why? Because of <strong>Dynamic Linking</strong>. By default, the Rust compiler targets <code>x86_64-unknown-linux-gnu</code>. When the compiler generates the Executable and Linkable Format (ELF) binary, it does not include the C Standard Library (like the code for the <code>malloc</code> allocator or DNS resolution). Instead, it leaves placeholders in the ELF binary, expecting the host operating system to provide the GNU C Library (<code>glibc</code>) at runtime via a shared object file (<code>.so</code>).</p>
    <p>Because the scratch image is completely empty, <code>glibc</code> does not exist. The Linux kernel attempts to execute your binary, fails to find the dynamic linker, and immediately throws a cryptic <code>standard_init_linux.go: exec user process caused "no such file or directory"</code> error.</p>

    <h2>3. True Static Linking via `musl`</h2>
    <p>To deploy to a scratch image, we must target <code>x86_64-unknown-linux-musl</code>. <code>musl</code> is a highly optimized, lightweight implementation of the C standard library designed specifically for static linking.</p>
    <p>When we target <code>musl</code>, the Rust compiler and the <code>mold</code> linker take the entire C standard library and physically copy the required machine code directly into our final Rust ELF binary. The resulting binary is completely self-contained. It relies on absolutely zero files or libraries on the host filesystem. It only communicates directly with the Linux kernel via system calls.</p>
    <p>When this statically linked binary is deployed into the empty void of a scratch image, it boots flawlessly. If a hacker achieves RCE, they are trapped in a mathematical vacuum. There is no <code>bash</code> to execute, no <code>curl</code> to download payloads, and no filesystem utilities. You have reduced the OS-level attack surface to absolute zero.</p>
</section>"""

essay_14 = """<section class="chapter" id="stack">
    <div class="chapter-label">Chapter 14</div>
    <h1>Intensive Deep Dive: V8 JIT & WASM Memory Internals</h1>

    <h2>1. The Flaw of Just-In-Time (JIT) Compilation</h2>
    <p>When building a Full Stack application using Astro and Node.js for server-side rendering, developers often rely heavily on JavaScript for computational tasks (like parsing massive JSON payloads or rendering complex Markdown). Node.js utilizes the V8 JavaScript engine, which is a Just-In-Time (JIT) compiler.</p>
    <p>JavaScript is a dynamic, untyped language. When V8 encounters a function like <code>function add(a, b) { return a + b; }</code>, it has no idea if <code>a</code> and <code>b</code> are integers, strings, or objects. The JIT compiler starts by running the code in an interpreter. As the code runs, V8 profiles the types. If it notices that <code>a</code> and <code>b</code> are always integers, it optimistically compiles the function into highly optimized machine code (TurboFan).</p>
    <p>However, if the 10,000th HTTP request passes a floating-point number instead of an integer, the optimized machine code is mathematically invalid. V8 suffers a <strong>De-optimization (Bailout)</strong>. It halts execution, discards the machine code, and falls back to the incredibly slow interpreter. In a high-throughput API, these random de-optimizations cause massive, unpredictable spikes in p99 tail latency.</p>

    <h2>2. Deterministic Performance via WebAssembly (WASM)</h2>
    <p>To guarantee flat, deterministic tail latency in our Node.js rendering layer, we offload all heavy computation to <strong>WebAssembly (WASM)</strong>. We compile our core Rust logic (like Markdown parsing or cryptographic validation) into the <code>wasm32-unknown-unknown</code> target.</p>
    <p>WASM is a statically typed, low-level bytecode. When V8 receives the WASM module, it does not need to guess types or perform speculative JIT optimization. It performs a single, highly efficient streaming compilation pass (Liftoff) and translates the WASM directly into native machine code. The resulting execution speed is mathematically constant, completely eliminating JIT de-optimizations and stabilizing our API latency.</p>

    <h2>3. Linear Memory and the FFI Boundary</h2>
    <p>However, integrating WASM introduces a massive architectural bottleneck: The Foreign Function Interface (FFI) boundary. A WASM module executes inside a sandboxed, flat <code>ArrayBuffer</code> known as <strong>Linear Memory</strong>. It has absolutely no access to the Node.js V8 heap, and Node.js cannot directly read WASM variables.</p>
    <p>If Node.js needs the WASM module to process a 10MB JSON string, the naive approach (used by most libraries) is to serialize the string, allocate 10MB of memory inside the WASM Linear Memory, copy the string byte-by-byte across the FFI boundary, process it, allocate another 10MB string, and copy it back. This massive memory copying utterly destroys the performance gains of WASM, making it slower than pure JavaScript.</p>

    <h2>4. Zero-Copy Pointer Passing</h2>
    <p>To achieve expert-level performance, we bypass copying entirely using the <code>wasm-bindgen</code> crate. When Node.js needs to pass the 10MB string, it does not pass the string. It calls a Rust WASM function that allocates 10MB of raw bytes inside the Linear Memory, and returns the <strong>raw memory pointer (<code>*mut u8</code>)</strong> back to Node.js.</p>
    <p>Node.js then creates a <code>Uint8Array</code> view that directly wraps that specific memory address within the WASM <code>ArrayBuffer</code>. Node.js writes the 10MB string directly into the WASM memory space. When Node.js calls the processing function, it simply passes the memory pointer. The Rust code instantly executes against the memory with zero serialization, zero copying, and zero overhead, achieving native C-level performance within a V8 JavaScript environment.</p>
</section>"""

content = re.sub(r'<section class="chapter" id="concurrency">.*?</section>', essay_10, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="auth">.*?</section>', essay_11, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="workers">.*?</section>', essay_12, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="deploy">.*?</section>', essay_13, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="stack">.*?</section>', essay_14, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapters 10, 11, 12, 13, and 14.")
