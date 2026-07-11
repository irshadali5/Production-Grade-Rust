import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "auth": """<section class="chapter" id="auth">
    <div class="chapter-label">Chapter 11</div>
    <h1>Expert Security: Argon2id & OAuth2 PKCE</h1>

    <h2>The Mathematical Necessity of Argon2id</h2>
    <p>Authentication in modern systems demands rigorous defense against both GPU-accelerated brute force attacks and side-channel timing attacks. Using legacy hashing algorithms like MD5 or SHA-256 is professional negligence, as modern ASICs can calculate billions of hashes per second. Even bcrypt, while mathematically sound against CPUs, falls short against dedicated FPGAs due to its low memory hardness.</p>
    <p>We implement <strong>Argon2id</strong>, the winner of the Password Hashing Competition. Argon2id is a hybrid algorithm that protects against both side-channel attacks (like Argon2i) and GPU cracking (like Argon2d). Its primary defense mechanism is <em>memory hardness</em>. By forcing the algorithm to require gigabytes of RAM to compute a single hash, it renders GPU architectures (which rely on thousands of cores with tiny amounts of memory) completely useless for parallel cracking.</p>

    <h2>Timing Attacks and Constant-Time Verification</h2>
    <p>When verifying a password, if your code uses a standard string equality check (`==`), it will return `false` the exact millisecond it hits a mismatching character. An attacker can send thousands of requests, measure the exact microsecond response times, and literally guess the password character-by-character based on how long the server took to reject it. This is a side-channel timing attack. Argon2id uses cryptographic constant-time comparison functions to guarantee that a rejection takes the exact same amount of CPU cycles regardless of where the mismatch occurred.</p>

    <h2>The PKCE Flow for OAuth2</h2>
    <p>For third-party authentication, we utilize OAuth2. However, the standard Authorization Code grant is vulnerable in mobile or Single-Page Applications (SPAs) because the `client_secret` cannot be securely stored on the user's device. If a malicious app intercepts the Authorization Code, it can hijack the user's session.</p>
    <p>We implement <strong>PKCE (Proof Key for Code Exchange)</strong>. In PKCE, the client dynamically generates a cryptographically random `code_verifier` and a `code_challenge` (a SHA-256 hash of the verifier) for every single login attempt. The client sends the challenge to the auth server. Later, when redeeming the code for a token, the client must provide the raw verifier. The server hashes the verifier and ensures it matches the original challenge. Because an intercepting attacker cannot mathematically reverse the SHA-256 hash to guess the verifier, the hijacked code is rendered utterly useless.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/auth.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">argon2</span>::{<span class="type">Argon2</span>, <span class="type">PasswordHasher</span>};
<span class="kw">use</span> <span class="type">rand_core</span>::{<span class="type">OsRng</span>, <span class="type">RngCore</span>};

<span class="kw">pub fn</span> <span class="fn">hash_password</span>(password: &amp;str) -&gt; <span class="type">String</span> {
    <span class="kw">let</span> salt = <span class="type">argon2</span>::<span class="type">password_hash</span>::<span class="type">SaltString</span>::<span class="fn">generate</span>(&amp;<span class="kw">mut</span> <span class="type">OsRng</span>);
    <span class="cmt">// Argon2id is resistant to both GPU and side-channel timing attacks</span>
    <span class="type">Argon2</span>::<span class="fn">default</span>().<span class="fn">hash_password</span>(password.as_bytes(), &amp;salt).unwrap().<span class="fn">to_string</span>()
}</pre></div>
</section>""",

    "deploy": """<section class="chapter" id="deploy">
    <div class="chapter-label">Chapter 13</div>
    <h1>Deployment: Distroless & Static Musl</h1>

    <h2>The Catastrophic Attack Surface of Containers</h2>
    <p>A standard Docker deployment usually relies on an image like `ubuntu` or `debian`. These images contain gigabytes of software: Bash, `curl`, package managers (`apt`), and Python. If an attacker manages to achieve Remote Code Execution (RCE) inside your Rust container—perhaps through a zero-day vulnerability in an image processing library—they instantly have access to a full Linux terminal. They can `curl` a reverse shell, install malware, and pivot into your internal Kubernetes network.</p>
    <p>This is a completely unnecessary risk. Your Rust application does not need `bash` to run. It only needs the Linux kernel.</p>

    <h2>Static Linking with `musl`</h2>
    <p>By default, the Rust compiler dynamically links the GNU C Library (`glibc`). This means your compiled binary will not run unless the host machine has the exact same version of `glibc` installed. We solve this by targeting `x86_64-unknown-linux-musl`. The `musl` target forces the Rust compiler to statically link the entire C standard library directly into your final binary. The resulting binary is completely self-contained; it relies on zero shared objects (`.so` files) on the host operating system.</p>

    <h2>Google Distroless & Scratch Images</h2>
    <p>Once we possess a fully statically linked Rust binary, we execute a multi-stage Docker build to deploy it onto Google's <strong>Distroless</strong> images, or even `FROM scratch` (an empty filesystem). A scratch image contains literally zero files. No shell, no utilities, no `curl`. If an attacker achieves RCE, they find themselves trapped in a void with no tools to execute. We reduce our attack surface to mathematically zero.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">Dockerfile</span><span class="code-lang">dockerfile</span></div>
    <pre><span class="cmt"># Multi-stage build for ultimate security</span>
<span class="kw">FROM</span> rust:1.80 AS builder
<span class="kw">RUN</span> rustup target add x86_64-unknown-linux-musl
<span class="kw">RUN</span> cargo build --release --target x86_64-unknown-linux-musl

<span class="cmt"># Final image has literally zero OS binaries (no bash, no curl)</span>
<span class="kw">FROM</span> gcr.io/distroless/static-debian11
<span class="kw">COPY</span> --from=builder /app/target/x86_64-unknown-linux-musl/release/zero2prod /
<span class="kw">CMD</span> ["./zero2prod"]</pre></div>
</section>""",

    "stack": """<section class="chapter" id="stack">
    <div class="chapter-label">Chapter 14</div>
    <h1>Full Stack: Astro SSR & Rust FFI</h1>

    <h2>The Microservices Anti-Pattern for UI</h2>
    <p>In modern web development, teams often split the frontend (React/Vue) and the backend (Rust) into separate repositories. This introduces extreme cognitive overhead. Every feature requires synchronizing API contracts, managing CORS policies, and dealing with network latency between the browser and the JSON API.</p>
    <p>We advocate for a unified Full Stack architecture. We use <strong>Astro</strong> running in Server-Side Rendering (SSR) mode directly alongside our Rust API. Astro is a next-generation web framework that ships zero JavaScript to the client by default, rendering pure HTML on the server. When interactivity is required, it utilizes "Islands Architecture" to hydrate specific components with React or Svelte.</p>

    <h2>Crossing the FFI Boundary (WebAssembly)</h2>
    <p>While Astro/Node handles HTML rendering, core domain logic must remain in Rust. To bridge the gap without the overhead of HTTP requests, we compile critical Rust modules into <strong>WebAssembly (WASM)</strong>. We use the Foreign Function Interface (FFI) provided by `wasm-bindgen` to allow Node.js to directly execute our Rust mathematical models or cryptographic functions in memory.</p>
    <p>This allows us to share code. The exact same Rust validation struct used by our Postgres database can be compiled to WASM and executed by the Astro frontend to provide instant, mathematically identical form validation in the user's browser, completely eliminating logic duplication.</p>
</section>""",

    "reliability": """<section class="chapter" id="reliability">
    <div class="chapter-label">Chapter 16</div>
    <h1>Reliability: Circuit Breakers & Retries</h1>

    <h2>The Cascade of Failure</h2>
    <p>In a distributed system, partial failure is not a possibility; it is a mathematical certainty. Suppose your Rust API relies on a third-party payment gateway. The payment gateway experiences an outage and begins dropping packets, causing TCP timeouts. If your Rust API blindly continues to send requests, your Tokio worker threads will become trapped waiting for timeouts. Within seconds, your entire thread pool is exhausted, and your API crashes, bringing down the entire system. This is a cascading failure.</p>

    <h2>The Circuit Breaker Pattern</h2>
    <p>We mitigate cascading failures using the <strong>Circuit Breaker</strong> pattern, implemented via the `tower` crate. A Circuit Breaker acts as an electrical fuse for your network calls. It monitors the failure rate of an external service. If 5 consecutive requests fail, the circuit "trips" open. While open, the Circuit Breaker intercepts all incoming requests and instantly returns a failure, shedding the load without ever attempting the network call.</p>
    <p>By failing-fast, your Tokio threads are instantly freed to process other tasks, isolating the failure to the specific payment route and keeping the rest of your API online.</p>

    <h2>Exponential Backoff and Jitter</h2>
    <p>When the third-party service eventually recovers, a naïve system will immediately flood it with thousands of queued retries, causing a Thundering Herd that instantly knocks the service offline again. We solve this using <strong>Exponential Backoff with Jitter</strong>.</p>
    <p>Instead of retrying every 1 second, we retry after 1s, 2s, 4s, 8s, 16s. This exponential decay gives the struggling service breathing room. Furthermore, we inject "Jitter"—a randomized cryptographic variance to the delay (e.g., 1.1s, 2.3s, 3.8s). Jitter breaks the synchronization of retries across your Kubernetes pods, spreading the load evenly and preventing accidental DDoS attacks against your own infrastructure.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/client.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">let</span> policy = <span class="type">ConsecutiveFailures</span>::<span class="fn">new</span>(<span class="num">5</span>);
<span class="kw">let</span> client = <span class="type">ServiceBuilder</span>::<span class="fn">new</span>()
    .buffer(<span class="num">100</span>)
    .concurrency_limit(<span class="num">10</span>)
    .retry(policy) <span class="cmt">// Trips open after 5 consecutive failures</span>
    .service(reqwest_client);</pre></div>
</section>""",

    "websockets": """<section class="chapter" id="websockets">
    <div class="chapter-label">Chapter 18</div>
    <h1>WebSockets & The Actor Model</h1>

    <h2>The Inefficiency of HTTP Polling</h2>
    <p>For real-time analytics dashboards or chat applications, relying on traditional HTTP requires the client to aggressively "poll" the server every second for updates. This generates massive network overhead, as every request requires a full TCP handshake, TLS negotiation, and header parsing, just to receive a response of "No new data".</p>
    <p>We solve this using <strong>WebSockets</strong>. A WebSocket establishes a single, persistent TCP connection that remains open indefinitely, allowing bi-directional, full-duplex communication with negligible overhead. Axum handles the protocol upgrade via the `ws` extractor.</p>

    <h2>Concurrency Management with the Actor Model</h2>
    <p>Maintaining 100,000 concurrent WebSocket connections introduces terrifying concurrency challenges. If User A sends a message to User B, how does Thread A safely locate and write to Thread B's socket without triggering a data race or a deadlock on a massive shared `Mutex`?</p>
    <p>We solve this using the <strong>Actor Model</strong> and Tokio MPSC (Multi-Producer, Single-Consumer) channels. Instead of sharing state, we share memory by communicating. Every connected WebSocket is assigned an "Actor" task. The central application state maintains a lock-free `DashMap` containing the `Sender` half of each Actor's MPSC channel.</p>
    <p>When User A wants to message User B, they do not lock User B's socket. They simply drop a message into User B's channel queue. User B's Actor independently consumes messages from its queue and writes them to its own socket sequentially. This lock-free architecture allows us to saturate 100% of CPU cores linearly, easily handling millions of concurrent connections.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/ws.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">axum</span>::<span class="type">extract</span>::<span class="type">ws</span>::{<span class="type">WebSocket</span>, <span class="type">Message</span>};

<span class="kw">pub async fn</span> <span class="fn">handle_socket</span>(<span class="kw">mut</span> socket: <span class="type">WebSocket</span>) {
    <span class="kw">while let</span> <span class="type">Some</span>(msg) = socket.<span class="fn">recv</span>().<span class="kw">await</span> {
        <span class="kw">let</span> msg = msg.unwrap();
        <span class="kw">if let</span> <span class="type">Message</span>::<span class="type">Text</span>(t) = msg {
            <span class="cmt">// Dispatch to internal Actor via channel without acquiring locks</span>
            <span class="mac">println!</span>(<span class="str">"Received: {}"</span>, t);
        }
    }
}</pre></div>
</section>""",

    "qol": """<section class="chapter" id="qol">
    <div class="chapter-label">Chapter 19</div>
    <h1>Quality of Life: CI/CD & Static Analysis</h1>

    <h2>The CI/CD Iron Clad Guarantee</h2>
    <p>A production codebase is only as stable as its Continuous Integration (CI) pipeline. If a developer can merge code that breaks compilation or fails tests, the entire system degrades. We implement an iron-clad GitHub Actions pipeline that mathematically guarantees code quality before a merge is ever allowed.</p>
    <p>Our pipeline runs `cargo check` and `cargo test` across multiple operating systems, but this is the bare minimum. We enforce expert-level strictness using the following tools.</p>

    <h2>Clippy and Formatting Strictness</h2>
    <p>We run `cargo fmt -- --check` to enforce identical code formatting across the team, ending style debates forever. We run `cargo clippy -- -D warnings`, elevating all linting warnings to fatal compilation errors. Clippy does not just check syntax; it performs semantic analysis to catch inefficient memory allocations, unidiomatic lifetime bounds, and potential deadlocks.</p>

    <h2>Supply Chain Security and Bloat Reduction</h2>
    <p>Rust's ecosystem is heavily reliant on crates.io. A single compromised dependency can result in a catastrophic supply-chain attack. We integrate `cargo-audit` into our CI pipeline. It cross-references every crate in our `Cargo.lock` against the RustSec Advisory Database. If a dependency contains a known vulnerability (e.g., an RCE or memory leak), the pipeline instantly fails.</p>
    <p>Furthermore, large workspaces inevitably accumulate unused dependencies, bloating binary size and compile times. We utilize `cargo-udeps` in a nightly toolchain matrix to statically analyze our dependency graph. If a crate is imported in `Cargo.toml` but never actually used in the source code, `cargo-udeps` forces a CI failure, keeping the codebase mathematically lean.</p>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to Unit 3 (Production Systems).")
