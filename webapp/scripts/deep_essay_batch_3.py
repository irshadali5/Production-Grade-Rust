import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay_20 = """<section class="chapter" id="gateway">
    <div class="chapter-label">Chapter 20</div>
    <h1>Intensive Deep Dive: Token Buckets & Leaky Bucket Physics</h1>

    <h2>1. The Economics of LLM APIs</h2>
    <p>When interacting with external LLM APIs (like OpenAI or Anthropic), you are charged per token. A single malicious user scraping your API can bankrupt your company in minutes. A hyperscale architecture must implement a ruthless API Gateway that enforces cryptographically secure rate limiting before the request even reaches the Axum router.</p>

    <h2>2. The Token Bucket Algorithm</h2>
    <p>The naive approach to rate limiting is the "Fixed Window" counter. If a user is allowed 100 requests per minute, you increment a counter. However, this allows massive bursts: a user can send 100 requests at 12:00:59, and another 100 requests at 12:01:01, effectively achieving 200 requests in 2 seconds, destroying your backend.</p>
    <p>We solve this using the <strong>Token Bucket Algorithm</strong>. Imagine a literal bucket that holds a maximum of 100 tokens. A background mathematical function adds 1 token to the bucket every 0.6 seconds. When a request arrives, we check if the bucket has a token. If it does, we remove the token and process the request. If the bucket is empty, we reject the request. This perfectly smooths out traffic, mathematically preventing destructive bursts.</p>

    <h2>3. The Leaky Bucket Variation</h2>
    <p>If we want to protect downstream services (like a fragile legacy database), we use the <strong>Leaky Bucket Algorithm</strong>. Incoming requests pour into the top of the bucket at any rate. However, the bucket has a small hole in the bottom, and requests drip out at a perfectly constant, mathematical rate (e.g., exactly 10 requests per second). If the bucket fills up, incoming requests spill over and are rejected. This guarantees that your downstream service receives a perfectly flat line of traffic, rendering it immune to load spikes.</p>

    <h2>4. Redis Pipelining & LUA Scripts</h2>
    <p>To implement this in a distributed cluster, we must store the buckets in Garnet (our Redis alternative). If a Rust worker executes <code>GET</code>, checks the tokens, and executes <code>SET</code>, there is a massive Race Condition. If 1,000 requests arrive at the exact same millisecond, all 1,000 workers will read <code>tokens=100</code>, and all will decrement it, completely bypassing the limit.</p>
    <p>We eliminate this using <strong>Atomic LUA Scripts</strong>. We send the Token Bucket logic to Garnet as a LUA script. Garnet executes the LUA script in a single, atomic, single-threaded transaction directly in its memory space. By leveraging Redis pipelining, we guarantee absolute thread safety across 10,000 distributed Rust workers with zero lock contention.</p>
</section>"""

essay_21 = """<section class="chapter" id="rag">
    <div class="chapter-label">Chapter 21</div>
    <h1>Intensive Deep Dive: HNSW Graphs & Cosine Similarity</h1>

    <h2>1. The Limitation of Lexical Search</h2>
    <p>Standard databases use B-Tree indexes for lexical search (matching exact strings). If a user searches for "automobile," a B-Tree will never return a document containing the word "car" because the strings are different. To build intelligent AI applications (RAG), we must search based on <strong>semantic meaning</strong>.</p>
    
    <h2>2. High-Dimensional Vector Embeddings</h2>
    <p>We achieve this by passing text through an Embedding Model (like <code>text-embedding-3-small</code>). The model uses a neural network to convert the text into a massive array of floating-point numbers—a 1,536-dimensional Vector. This Vector represents the exact semantic location of the concept in a 1,536-dimensional mathematical space. In this space, the vector for "automobile" is physically located very close to the vector for "car," but very far away from the vector for "apple."</p>

    <h2>3. Cosine Similarity & The Curse of Dimensionality</h2>
    <p>To find the most relevant documents, we calculate the angle between the user's search query vector and every document vector in the database using <strong>Cosine Similarity</strong>. A Cosine Similarity of 1.0 means the vectors point in the exact same direction (perfect semantic match). A similarity of 0 means they are orthogonal (unrelated).</p>
    <p>However, calculating the Cosine Similarity against 1 billion documents takes a massive amount of CPU time. This is known as the Curse of Dimensionality. We cannot scan the entire database for every search.</p>

    <h2>4. Hierarchical Navigable Small World (HNSW) Graphs</h2>
    <p>We solve this using the <code>pgvector</code> extension in Postgres, specifically utilizing the <strong>HNSW (Hierarchical Navigable Small World)</strong> index. HNSW is a probabilistic, graph-based algorithm. It builds multiple layers of graphs. The top layer has very few nodes (vectors) with long connections. The bottom layer has all the nodes.</p>
    <p>When a search occurs, the algorithm starts at the top layer, taking massive leaps across the 1,536-dimensional space to quickly find the general neighborhood of the semantic concept. It then descends into the lower layers, taking smaller and smaller steps to find the exact nearest neighbors. HNSW trades a tiny fraction of accuracy for a logarithmic speedup, allowing us to perform semantic vector searches across billions of documents in single-digit milliseconds.</p>
</section>"""

essay_22 = """<section class="chapter" id="async">
    <div class="chapter-label">Chapter 22</div>
    <h1>Intensive Deep Dive: The Physics of the `Future` Trait</h1>

    <h2>1. The Illusion of Asynchronous Code</h2>
    <p>Junior developers believe that the <code>async</code> keyword magically makes code run in parallel. This is a severe misunderstanding. When you write an <code>async fn</code>, the Rust compiler performs an aggressive AST transformation. It completely rewrites your function into a massive, hidden <strong>State Machine</strong> enum.</p>
    <p>Every time you write the <code>.await</code> keyword, you define a boundary for the state machine. The function does not "block"; it simply yields execution and returns a <code>Poll::Pending</code> state. The variables that were alive before the <code>.await</code> are mathematically packed into the state machine enum so they can be restored later. This is why you cannot hold a <code>std::sync::MutexGuard</code> across an <code>.await</code> point—the thread might be yielded, the lock remains held, and your server deadlocks instantly.</p>

    <h2>2. The Waker and Epoll</h2>
    <p>If a Future returns <code>Poll::Pending</code>, how does Tokio know when to poll it again? It would be a catastrophic waste of CPU to continuously poll it in a loop (busy-waiting). The magic lies in the <code>Context</code> argument passed to the <code>poll</code> method, which contains a <strong>Waker</strong>.</p>
    <p>When your Rust code initiates a network request, it registers the TCP socket with the OS kernel's <code>epoll</code> (or <code>io_uring</code>) system. It then stores the <code>Waker</code> deep inside the TCP stream struct. The Future returns <code>Poll::Pending</code> and the thread is completely freed to do other work.</p>

    <h2>3. The Hardware Interrupt</h2>
    <p>Millseconds later, a physical packet of light travels through a fiber-optic cable, hits the server's Network Interface Card (NIC), and generates a hardware interrupt. The OS kernel processes the packet, places the data in a buffer, and fires the <code>epoll</code> event.</p>
    <p>Tokio detects the <code>epoll</code> event, looks up the TCP socket, and invokes <code>Waker::wake()</code>. This specific method pushes the sleeping Task back onto Tokio's Run Queue. The executor eventually pops the task and calls <code>poll()</code> again. The state machine resumes exactly where it left off, successfully reads the buffer, and returns <code>Poll::Ready</code>.</p>
    <p>By understanding this intricate dance between compiler-generated state machines, Wakers, and hardware interrupts, we can architect systems that process 10 million concurrent connections using only 8 MB of RAM.</p>
</section>"""

essay_23 = """<section class="chapter" id="security">
    <div class="chapter-label">Chapter 23</div>
    <h1>Intensive Deep Dive: Elliptic Curves & Perfect Forward Secrecy</h1>

    <h2>1. The Mathematics of Diffie-Hellman</h2>
    <p>In a hyperscale system, relying purely on TLS 1.2 is insufficient for internal microservice communication. A compromised load balancer can decrypt all traffic via SSL stripping. We must implement Zero-Trust networking using End-to-End Encryption (E2EE) at the application layer.</p>
    <p>To establish a secure channel over a compromised network, we use the <strong>Elliptic Curve Diffie-Hellman (ECDH)</strong> protocol. Both Rust microservices generate a private key and mathematically derive a public key by multiplying a base point on an Elliptic Curve (e.g., Curve25519). They exchange their public keys in plain text over the compromised network.</p>
    <p>Microservice A multiplies its private key with Microservice B's public key. Microservice B does the reverse. Through the mathematical properties of Elliptic Curves, both calculations result in the exact same Shared Secret. The attacker, who intercepted the public keys, cannot calculate the Shared Secret because calculating the Discrete Logarithm of an Elliptic Curve is mathematically impossible for modern supercomputers.</p>

    <h2>2. Perfect Forward Secrecy (PFS)</h2>
    <p>If we use a static private key, an attacker could record 5 years of encrypted traffic. If they eventually steal the private key in year 6, they can retroactively decrypt all 5 years of data. This is catastrophic.</p>
    <p>We eliminate this using <strong>Perfect Forward Secrecy (PFS)</strong>. Our Rust microservices do not use static keys for encryption. They generate completely new, ephemeral Elliptic Curve keypairs for <em>every single network session</em>. Once the session concludes, the ephemeral private keys are cryptographically zeroized from RAM. Even if the attacker physically compromises the server and extracts the hard drive, they cannot decrypt past traffic, because the keys physically no longer exist in the universe.</p>
</section>"""

essay_24 = """<section class="chapter" id="wasm">
    <div class="chapter-label">Chapter 24</div>
    <h1>Intensive Deep Dive: WASI & Capability-Based Sandboxing</h1>

    <h2>1. The Danger of Native Plugins</h2>
    <p>If you build a platform that allows users to upload custom logic (e.g., custom HTTP routing scripts), executing that logic natively is a massive security vulnerability. If you execute a user's Python script, they can use <code>os.system('rm -rf /')</code> to destroy the host server, or they can open a socket and exfiltrate your database credentials.</p>

    <h2>2. WebAssembly System Interface (WASI)</h2>
    <p>We solve this by requiring users to upload WebAssembly (WASM) modules. We execute these modules inside our Rust server using the <code>wasmtime</code> runtime. However, pure WASM cannot perform any I/O. It cannot read files or open network sockets. It is a pure mathematical sandbox.</p>
    <p>To allow useful work, we implement the <strong>WebAssembly System Interface (WASI)</strong>. WASI defines a standardized set of system calls (like <code>fd_read</code> or <code>random_get</code>) that the WASM module can call. However, these calls do not hit the OS kernel; they are intercepted by the <code>wasmtime</code> runtime running in our Rust host.</p>

    <h2>3. Capability-Based Security</h2>
    <p>This allows us to implement <strong>Capability-Based Security</strong>. By default, the WASM plugin has zero capabilities. If the plugin attempts to open <code>/etc/passwd</code>, the <code>wasmtime</code> interceptor instantly denies the request. The Rust host must explicitly grant the WASM module a specific "Capability" (e.g., a file descriptor pointing only to the <code>/tmp/plugin_data</code> directory).</p>
    <p>The plugin believes it is talking to the OS, but it is actually trapped in a mathematically isolated virtual filesystem. If the plugin suffers a memory corruption bug, the damage is strictly confined to the WASM Linear Memory. The Rust host remains completely untouched, allowing us to safely execute untrusted third-party code at near-native speeds.</p>
</section>"""

content = re.sub(r'<section class="chapter" id="gateway">.*?</section>', essay_20, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="rag">.*?</section>', essay_21, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="async">.*?</section>', essay_22, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="security">.*?</section>', essay_23, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="wasm">.*?</section>', essay_24, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapters 20, 21, 22, 23, and 24.")
