import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay_15 = """<section class="chapter" id="ai">
    <div class="chapter-label">Chapter 15</div>
    <h1>Intensive Deep Dive: Structured Generation & Logit Bias</h1>

    <h2>1. The Catastrophe of Probabilistic Output</h2>
    <p>When integrating Large Language Models (LLMs) into a production system, developers often attempt to use Prompt Engineering to coerce the model into returning a specific data structure, such as JSON. This is a fatal architectural error. An LLM is not a deterministic function; it is a massive, probabilistic neural network that predicts the next token. If you ask it for JSON, there is a non-zero statistical probability that it will hallucinate a trailing comma, prefix the output with "Here is your JSON:", or wrap the data in markdown backticks.</p>
    <p>If you feed this probabilistic output directly into a deterministic JSON parser like <code>serde_json</code>, your Rust application will immediately throw a parsing panic. In a hyperscale system processing thousands of AI queries, a 1% hallucination rate means your API crashes 10 times a second.</p>

    <h2>2. Deterministic Structured Generation</h2>
    <p>We eliminate this failure mode mathematically using <strong>Structured Generation</strong>. Instead of asking the model nicely, we leverage advanced LLM API features (like OpenAI's <code>json_schema</code>) to physically alter the neural network's generation engine.</p>
    <p>We begin by defining our exact desired output format as a Rust struct (e.g., <code>struct ExtractionResult { confidence: f32, entities: Vec&lt;String&gt; }</code>). We use the <code>schemars</code> crate to automatically analyze this struct at compile-time and generate a rigorous, mathematical JSON Schema. We inject this Schema directly into the LLM API request payload.</p>

    <h2>3. The Physics of Logit Masking</h2>
    <p>When the LLM backend receives the JSON Schema, it alters how it calculates probabilities (logits). Before the neural network selects the next token, the backend applies a mathematical mask to the output vector. If the JSON Schema dictates that the next character <em>must</em> be a floating-point number, the backend multiplies the logits of every token that is a letter (A-Z) or a symbol by negative infinity.</p>
    <p>Because the probability of outputting an invalid token has been mathematically crushed to absolute zero, the model is physically forced to output a valid number. By utilizing Logit Masking, we guarantee with 100% mathematical certainty that the string returned by the LLM will map flawlessly to our Rust struct via <code>serde_json::from_str</code>, completely eliminating runtime panics and achieving true deterministic AI.</p>
</section>"""

essay_16 = """<section class="chapter" id="reliability">
    <div class="chapter-label">Chapter 16</div>
    <h1>Intensive Deep Dive: Little's Law & Circuit Breakers</h1>

    <h2>1. Queueing Theory and Little's Law</h2>
    <p>To architect a reliable system, you must understand the mathematics of Queueing Theory. The fundamental theorem is <strong>Little's Law</strong>: <code>L = λW</code> (The long-term average number of customers in a stable system (L) is equal to the long-term average effective arrival rate (λ) multiplied by the average time a customer spends in the system (W)).</p>
    <p>In the context of a Rust web API, if your server receives 1,000 requests per second (λ), and each request takes 0.1 seconds to process (W), you will have exactly 100 concurrent requests occupying Tokio threads (L). However, if your third-party payment gateway degrades, and the processing time (W) spikes from 0.1 seconds to 5.0 seconds, Little's Law dictates that the concurrent requests (L) will instantly spike to 5,000.</p>
    <p>Because each concurrent request consumes TCP sockets, memory, and database connections, this spike will instantly exhaust your server's resources. The payment gateway's outage has mathematically caused a <strong>Cascading Failure</strong> that brings down your entire Rust API.</p>

    <h2>2. The Circuit Breaker Pattern</h2>
    <p>We prevent Cascading Failures using the <strong>Circuit Breaker</strong> pattern via the <code>tower</code> crate. A Circuit Breaker acts as an electrical fuse. It wraps the HTTP client and monitors the failure rate. If 5 consecutive requests to the payment gateway timeout, the Circuit Breaker "trips" open.</p>
    <p>While the circuit is open, the Circuit Breaker intercepts all new outgoing requests and instantly returns a local failure (e.g., <code>503 Service Unavailable</code>) without even attempting the network call. Because the failure is instantaneous, the processing time (W) drops to zero, and the concurrent load (L) drops to zero. Your Tokio threads are instantly freed to process other routes, isolating the failure and keeping the rest of your API perfectly healthy.</p>

    <h2>3. Exponential Backoff and Cryptographic Jitter</h2>
    <p>When the third-party service eventually recovers, a naive system will immediately flood it with thousands of queued retries, causing a <strong>Thundering Herd</strong> that instantly knocks the service offline again.</p>
    <p>We solve this using <strong>Exponential Backoff with Jitter</strong>. Instead of retrying every 1 second, we double the delay on each failure: 1s, 2s, 4s, 8s. This exponential decay gives the struggling service breathing room. Crucially, we inject "Jitter"—a cryptographically randomized variance to the delay (e.g., 1.1s, 2.3s, 3.8s). Jitter breaks the synchronization of retries across your Kubernetes pods. If 100 pods all fail at exactly 12:00:00, Jitter guarantees they will not all retry at exactly 12:00:01, spreading the load evenly and mathematically preventing accidental DDoS attacks against your own infrastructure.</p>
</section>"""

essay_17 = """<section class="chapter" id="caching">
    <div class="chapter-label">Chapter 17</div>
    <h1>Intensive Deep Dive: Cache Stampedes & Singleflight</h1>

    <h2>1. The Cache Stampede Problem</h2>
    <p>Caching is mandatory for hyperscale systems, but naive caching implementations introduce a catastrophic vulnerability known as a <strong>Cache Stampede</strong> (or Thundering Herd). Imagine your API caches a massive, 10-second analytical database query with a Time-To-Live (TTL) of 1 hour. For 59 minutes, the system is perfectly stable, serving the query from Garnet in 1 millisecond.</p>
    <p>At exactly 1 hour, the cache key expires. If your API is processing 1,000 requests per second, the next 1,000 requests will all check Garnet simultaneously, see a Cache Miss, and all 1,000 requests will simultaneously execute the 10-second analytical query against Postgres. The database will instantly lock up, memory will spike, and the entire cluster will crash.</p>

    <h2>2. The Singleflight Deduplication Algorithm</h2>
    <p>We mathematically prevent Cache Stampedes using the <strong>Singleflight</strong> pattern. The Singleflight algorithm intercepts concurrent requests for the same cache key. When the 1,000 requests arrive, Singleflight allows exactly <strong>one</strong> request (the leader) to proceed to the database. The remaining 999 requests do not query the database; they are placed into a lock-free asynchronous waiting queue in memory.</p>
    <p>When the leader finishes the 10-second query, it populates the Garnet cache and simultaneously broadcasts the result to the 999 waiting requests. A single database query satisfies 1,000 users. By collapsing concurrent requests into a single execution, Singleflight completely immunizes your database against Thundering Herds, regardless of how much traffic spikes during a cache miss.</p>
</section>"""

essay_18 = """<section class="chapter" id="websockets">
    <div class="chapter-label">Chapter 18</div>
    <h1>Intensive Deep Dive: The C10k Problem & Actor Model</h1>

    <h2>1. The Mathematics of TCP Polling</h2>
    <p>In traditional HTTP, a client requests data, the server responds, and the TCP connection is closed. If the client needs real-time updates, it must "poll" the server every second. This introduces extreme overhead: every second, the client performs a full TCP handshake (SYN, SYN-ACK, ACK), TLS cryptographic negotiation, and HTTP header parsing, just to receive a 1-byte response of "No new data".</p>
    <p>To eliminate this overhead, we upgrade the connection to <strong>WebSockets</strong>, establishing a persistent, full-duplex TCP stream. However, maintaining tens of thousands of persistent TCP connections introduces the legendary <strong>C10k Problem</strong>.</p>

    <h2>2. The C10k Problem and Epoll</h2>
    <p>In the 1990s, web servers used a thread-per-connection model. To handle 10,000 concurrent WebSockets, the OS had to spawn 10,000 physical threads. The Linux kernel spent 99% of its CPU time simply context-switching between threads, causing massive latency and memory exhaustion. Modern runtimes (like Tokio) solve this using asynchronous I/O multiplexing via <code>epoll</code>.</p>
    <p>Tokio maintains a single thread that monitors 10,000 sockets simultaneously. When a TCP packet arrives on socket 4,092, <code>epoll</code> fires a hardware interrupt, waking up the specific Tokio task assigned to that socket. This allows us to handle millions of concurrent WebSockets using only a handful of physical CPU cores.</p>

    <h2>3. The Actor Model and Lock-Free Queues</h2>
    <p>Managing the state of 10,000 WebSockets introduces terrifying concurrency challenges. If User A wants to send a chat message to User B, Thread A must locate User B's socket and write data to it. If we wrap all 10,000 sockets in a massive global <code>Mutex</code>, we guarantee Thread A will block Thread B, destroying our concurrency and deadlocking the server.</p>
    <p>We solve this using the <strong>Actor Model</strong>. Instead of sharing state, we share memory by communicating. Every connected WebSocket is assigned an "Actor"—an isolated Tokio task. We store the <code>Sender</code> half of an MPSC (Multi-Producer, Single-Consumer) channel in a lock-free <code>DashMap</code>.</p>
    <p>When User A wants to message User B, they do not lock User B's socket. They simply drop the message into User B's MPSC channel queue. User B's Actor independently consumes messages from its queue and writes them to its own socket sequentially. This lock-free message-passing architecture allows us to saturate 100% of CPU cores linearly without a single Mutex collision.</p>
</section>"""

essay_19 = """<section class="chapter" id="qol">
    <div class="chapter-label">Chapter 19</div>
    <h1>Intensive Deep Dive: CI/CD, AST Linting, & DAGs</h1>

    <h2>1. The Fragility of Human Review</h2>
    <p>In hyperscale engineering teams, relying on human Code Review to catch memory leaks, suboptimal allocations, or security vulnerabilities is a statistical impossibility. Humans suffer from fatigue. A production codebase must be protected by an Iron-Clad Continuous Integration (CI) pipeline that mathematically guarantees code quality before a merge is ever allowed.</p>

    <h2>2. Semantic AST Linting with Clippy</h2>
    <p>Our pipeline relies heavily on <code>clippy</code>, but it is crucial to understand how <code>clippy</code> operates. It does not perform basic Regex string matching like standard linters (e.g., ESLint). <code>clippy</code> hooks directly into the Rust compiler's internal pipeline. It analyzes the <strong>Abstract Syntax Tree (AST)</strong> and the <strong>High-Level Intermediate Representation (HIR)</strong> of your code.</p>
    <p>Because it understands the exact types and lifetimes of every variable, <code>clippy</code> can detect semantic flaws. It can mathematically prove that you are allocating a <code>String</code> inside a tight loop when a zero-cost <code>&str</code> slice would suffice. By running <code>cargo clippy -- -D warnings</code>, we elevate these semantic warnings into fatal compilation errors. We force developers to write optimal code, not just functioning code.</p>

    <h2>3. Supply Chain Security and `cargo-audit`</h2>
    <p>The Rust ecosystem heavily relies on external crates. A single compromised dependency can result in a catastrophic supply-chain attack. We integrate <code>cargo-audit</code> into our CI pipeline. It parses the cryptographic hashes in our <code>Cargo.lock</code> and cross-references them against the RustSec Advisory Database. If a dependency contains a known CVE (e.g., a buffer overflow or RCE), the pipeline instantly fails.</p>

    <h2>4. DAG Execution and Pipeline Optimization</h2>
    <p>A sequential CI pipeline (Build -> Test -> Lint -> Audit) is too slow for agile iteration. We utilize GitHub Actions to construct a <strong>Directed Acyclic Graph (DAG)</strong>. The DAG mathematically defines the dependency relationships between CI jobs. Because Linting and Auditing do not depend on the output of the Unit Tests, the DAG engine executes them simultaneously across multiple isolated virtual machines.</p>
    <p>By heavily utilizing aggressive caching (caching the <code>target/</code> directory and the Cargo registry based on the hash of the <code>Cargo.lock</code>), we reduce the compilation time from 15 minutes to under 30 seconds. A mathematically perfect, hyper-optimized CI pipeline is the only way to maintain velocity in a hyperscale team.</p>
</section>"""

content = re.sub(r'<section class="chapter" id="ai">.*?</section>', essay_15, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="reliability">.*?</section>', essay_16, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="caching">.*?</section>', essay_17, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="websockets">.*?</section>', essay_18, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="qol">.*?</section>', essay_19, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapters 15, 16, 17, 18, and 19.")
