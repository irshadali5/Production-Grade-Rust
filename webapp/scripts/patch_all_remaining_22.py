import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "setup": """<section class="chapter" id="setup">
    <div class="chapter-label">Chapter 01</div>
    <h1>Expert Toolchain: Nix Flakes & mold</h1>
    <p>Relying on global `cargo` installations leads to "works on my machine" failures. We use <strong>Nix Flakes</strong> to guarantee bit-for-bit reproducible development environments across Linux and macOS. To solve Rust's slow compilation times, we swap the default GNU linker for <code>mold</code>, a modern drop-in replacement that links massive binaries in milliseconds instead of seconds.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">flake.nix</span><span class="code-lang">nix</span></div>
    <pre><span class="cmt"># Pinning the exact rust-toolchain to guarantee identical builds globally</span>
<span class="kw">let</span> toolchain = fenix.packages.${system}.fromToolchainFile {
  file = ./rust-toolchain.toml;
  sha256 = "sha256-s1MutIG0IMZ...";
}; <span class="kw">in</span> pkgs.mkShell {
  buildInputs = [ toolchain pkgs.mold pkgs.clang ];
}</pre></div></section>""",

    "axum": """<section class="chapter" id="axum">
    <div class="chapter-label">Chapter 03</div>
    <h1>Advanced Routing: The Tower Service Trait</h1>
    <p>Axum is just syntax sugar over Tokio's <code>tower::Service</code>. To achieve true mastery, you must write custom middleware from scratch. By implementing <code>Service</code> directly, we gain fine-grained control over backpressure via <code>poll_ready</code>, allowing us to shed load dynamically before a handler even begins executing.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/middleware/rate_limit.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">impl</span>&lt;S, <span class="type">ReqBody</span>&gt; <span class="type">Service</span>&lt;<span class="type">Request</span>&lt;<span class="type">ReqBody</span>&gt;&gt; <span class="kw">for</span> <span class="type">RateLimit</span>&lt;S&gt; {
    <span class="kw">fn</span> <span class="fn">poll_ready</span>(&amp;<span class="kw">mut self</span>, cx: &amp;<span class="kw">mut</span> <span class="type">Context</span>&lt;<span class="lifetime">'_</span>&gt;) -&gt; <span class="type">Poll</span>&lt;<span class="type">Result</span>&lt;(), <span class="type">Self::Error</span>&gt;&gt; {
        <span class="kw">if</span> <span class="kw">self</span>.limiter.check().is_err() {
            <span class="cmt">// Backpressure: Shed load immediately before processing the request</span>
            <span class="kw">return</span> <span class="type">Poll</span>::<span class="type">Ready</span>(<span class="type">Err</span>(Error::TooManyRequests));
        }
        <span class="kw">self</span>.inner.poll_ready(cx)
    }
}</pre></div></section>""",

    "config": """<section class="chapter" id="config">
    <div class="chapter-label">Chapter 04</div>
    <h1>Zero-Trust Configuration: HashiCorp Vault</h1>
    <p>Storing secrets in environment variables is a critical security flaw; they can be dumped via <code>/proc/pid/environ</code>. We use the <code>figment</code> crate to dynamically merge configurations, and directly fetch short-lived database credentials from HashiCorp Vault or AWS KMS in memory.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/config.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">figment</span>::{<span class="type">Figment</span>, <span class="type">providers</span>::{<span class="type">Env</span>, <span class="type">Format</span>, <span class="type">Yaml</span>}};
<span class="kw">use</span> <span class="type">secrecy</span>::<span class="type">Secret</span>;

<span class="attr">#[derive(Deserialize)]</span>
<span class="kw">pub struct</span> <span class="type">Settings</span> {
    <span class="cmt">// Memory zeroing on drop guarantees the secret is wiped from RAM</span>
    <span class="kw">pub</span> database_url: <span class="type">Secret</span>&lt;<span class="type">String</span>&gt;,
}</pre></div></section>""",

    "database": """<section class="chapter" id="database">
    <div class="chapter-label">Chapter 05</div>
    <h1>Database Internals: PgBouncer & WAL</h1>
    <p>Postgres spawns a new OS process for every connection. At 10,000 concurrent Rust tasks, Postgres will crash from process overhead. We deploy <strong>PgBouncer</strong> in transaction-pooling mode to multiplex thousands of Rust tasks onto 50 physical Postgres connections. We rely on Postgres's Write-Ahead Log (WAL) to guarantee durability during sudden power loss.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/db.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="cmt">// Connect to PgBouncer port (6432), not directly to Postgres (5432)</span>
<span class="kw">let</span> pool = <span class="type">PgPoolOptions</span>::<span class="fn">new</span>()
    .max_connections(<span class="num">50</span>)
    .acquire_timeout(<span class="type">Duration</span>::<span class="fn">from_secs</span>(<span class="num">2</span>))
    .connect_with(config.with_db()).<span class="kw">await</span>?;</pre></div></section>""",

    "telemetry": """<section class="chapter" id="telemetry">
    <div class="chapter-label">Chapter 06</div>
    <h1>Observability: OpenTelemetry (OTLP)</h1>
    <p>When a microservice architecture fails, <code>println!</code> is useless. We implement <strong>OpenTelemetry (OTLP)</strong> distributed tracing using <code>tracing-opentelemetry</code>. We inject W3C Trace Context headers into every outgoing HTTP request, allowing us to visualize the exact critical path of a request across 5 different services in Jaeger.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/telemetry.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">opentelemetry</span>::<span class="type">global</span>;
<span class="kw">use</span> <span class="type">tracing_subscriber</span>::{<span class="type">layer</span>::<span class="type">SubscriberExt</span>, <span class="type">Registry</span>};

<span class="kw">let</span> tracer = <span class="type">opentelemetry_otlp</span>::<span class="fn">new_pipeline</span>()
    .tracing()
    .with_exporter(<span class="type">opentelemetry_otlp</span>::<span class="fn">new_exporter</span>().<span class="fn">tonic</span>())
    .install_batch(<span class="type">opentelemetry</span>::<span class="type">runtime</span>::<span class="type">Tokio</span>).unwrap();

<span class="kw">let</span> telemetry = <span class="type">tracing_opentelemetry</span>::<span class="fn">layer</span>().<span class="fn">with_tracer</span>(tracer);</pre></div></section>""",

    "errors": """<section class="chapter" id="errors">
    <div class="chapter-label">Chapter 07</div>
    <h1>Expert Error Handling: thiserror & Hooks</h1>
    <p>Do not use <code>anyhow</code> in libraries. We use <code>thiserror</code> to meticulously define our domain errors, and map them to HTTP 500s or 400s via transparent delegation. For catastrophic panics, we install a custom panic hook to log the exact thread backtrace into our centralized OTLP collector before the pod crashes.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/error.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">thiserror</span>::<span class="type">Error</span>;

<span class="attr">#[derive(Error, Debug)]</span>
<span class="kw">pub enum</span> <span class="type">DomainError</span> {
    <span class="attr">#[error(<span class="str">"Database connection severed"</span>)]</span>
    <span class="type">Database</span>(<span class="attr">#[from]</span> <span class="type">sqlx</span>::<span class="type">Error</span>),
    
    <span class="attr">#[error(<span class="str">"Invalid subscriber format"</span>)]</span>
    <span class="type">Validation</span>(<span class="attr">#[transparent]</span> <span class="type">ValidationError</span>),
}</pre></div></section>""",

    "validation": """<section class="chapter" id="validation">
    <div class="chapter-label">Chapter 08</div>
    <h1>Domain Modeling: Zero-Cost Newtypes</h1>
    <p>Primitive obsession (passing raw Strings around) leads to catastrophic security bugs like SQL injection. We utilize the <strong>Newtype Pattern</strong> with <code>#[repr(transparent)]</code>. This guarantees at compile-time that an unvalidated String can never reach the database layer, with exactly zero memory overhead compared to a raw String.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/domain/email.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="attr">#[derive(Debug, Clone)]</span>
<span class="attr">#[repr(transparent)]</span>
<span class="kw">pub struct</span> <span class="type">SubscriberEmail</span>(<span class="type">String</span>);

<span class="kw">impl</span> <span class="type">SubscriberEmail</span> {
    <span class="kw">pub fn</span> <span class="fn">parse</span>(s: <span class="type">String</span>) -&gt; <span class="type">Result</span>&lt;<span class="kw">Self</span>, <span class="type">String</span>&gt; {
        <span class="kw">if</span> validator::<span class="fn">validate_email</span>(&amp;s) { <span class="type">Ok</span>(<span class="kw">Self</span>(s)) } <span class="kw">else</span> { <span class="type">Err</span>(<span class="str">"Invalid format"</span>.into()) }
    }
}</pre></div></section>""",

    "testing": """<section class="chapter" id="testing">
    <div class="chapter-label">Chapter 10</div>
    <h1>Testing: Mathematical Concurrency Proofs</h1>
    <p>Standard unit tests cannot catch race conditions reliably. Instead, we use AWS's <strong>loom</strong> crate. Loom systematically permutes every possible thread interleaving of our lock-free data structures to mathematically prove the absence of data races, deadlocks, and use-after-free errors.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">tests/concurrency.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="attr">#[test]</span>
<span class="kw">fn</span> <span class="fn">test_concurrent_singleflight</span>() {
    <span class="cmt">// Loom intercepts all atomic operations and forces every possible thread schedule</span>
    <span class="type">loom</span>::<span class="type">model</span>(|| {
        <span class="kw">let</span> sf = <span class="type">Arc</span>::<span class="fn">new</span>(<span class="type">Singleflight</span>::<span class="fn">new</span>());
        <span class="type">loom</span>::<span class="type">thread</span>::<span class="fn">spawn</span>({ <span class="cmt">/* Thread 1 */</span> });
        <span class="type">loom</span>::<span class="type">thread</span>::<span class="fn">spawn</span>({ <span class="cmt">/* Thread 2 */</span> });
    });
}</pre></div></section>""",

    "deploy": """<section class="chapter" id="deploy">
    <div class="chapter-label">Chapter 13</div>
    <h1>Deployment: Distroless & Static Musl</h1>
    <p>A standard Debian Docker image contains bash, apt, and thousands of vulnerable binaries. We execute multi-stage builds using `x86_64-unknown-linux-musl` to statically link C dependencies, allowing us to deploy on Google's <strong>Distroless</strong> (or FROM scratch) images. Our attack surface becomes mathematically zero.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">Dockerfile</span><span class="code-lang">dockerfile</span></div>
    <pre><span class="cmt"># Multi-stage build for ultimate security</span>
<span class="kw">FROM</span> rust:1.80 AS builder
<span class="kw">RUN</span> rustup target add x86_64-unknown-linux-musl
<span class="kw">RUN</span> cargo build --release --target x86_64-unknown-linux-musl

<span class="cmt"># Final image has literally zero OS binaries (no bash, no curl)</span>
<span class="kw">FROM</span> gcr.io/distroless/static-debian11
<span class="kw">COPY</span> --from=builder /app/target/x86_64-unknown-linux-musl/release/zero2prod /
<span class="kw">CMD</span> ["./zero2prod"]</pre></div></section>""",

    "reliability": """<section class="chapter" id="reliability">
    <div class="chapter-label">Chapter 16</div>
    <h1>Reliability: Circuit Breakers</h1>
    <p>When an external API (like Postmark) goes down, blindly retrying destroys our own CPU. We implement the <strong>Circuit Breaker</strong> pattern using `tower::retry`. If the failure rate crosses a threshold, the circuit "trips" open, instantly failing-fast all incoming requests to protect system stability.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/client.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">let</span> policy = <span class="type">ConsecutiveFailures</span>::<span class="fn">new</span>(<span class="num">5</span>);
<span class="kw">let</span> client = <span class="type">ServiceBuilder</span>::<span class="fn">new</span>()
    .buffer(<span class="num">100</span>)
    .concurrency_limit(<span class="num">10</span>)
    .retry(policy) <span class="cmt">// Trips open after 5 consecutive failures</span>
    .service(reqwest_client);</pre></div></section>""",

    "wasm": """<section class="chapter" id="wasm">
    <div class="chapter-label">Chapter 24</div>
    <h1>WebAssembly: Linear Memory Internals</h1>
    <p>Compiling Rust to WASM using `wasm-bindgen` is easy, but achieving performance requires understanding WebAssembly's flat ArrayBuffer linear memory. Passing strings between JS and Rust requires expensive deep copies. We show how to share raw memory pointers across the JS-WASM FFI boundary to manipulate massive WebGL buffers at native speeds.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">src/lib.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="attr">#[wasm_bindgen]</span>
<span class="kw">pub fn</span> <span class="fn">get_memory_pointer</span>() -&gt; *<span class="kw">const</span> <span class="type">u8</span> {
    <span class="cmt">// Return raw pointer to JS so it can read linear memory directly</span>
    <span class="kw">let</span> data = <span class="type">vec!</span>[<span class="num">1</span>, <span class="num">2</span>, <span class="num">3</span>];
    data.as_ptr()
}</pre></div></section>""",

    "kubernetes": """<section class="chapter" id="kubernetes">
    <div class="chapter-label">Chapter 28</div>
    <h1>Kubernetes: HPA & Mutating Webhooks</h1>
    <p>We deploy our Rust API to a Kubernetes cluster using Helm. To handle hyperscale traffic spikes, we configure the <strong>Horizontal Pod Autoscaler (HPA)</strong> to dynamically scale replicas based on CPU utilization and custom Prometheus metrics. We implement Mutating Admission Webhooks in Rust to dynamically inject sidecars.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">helm/templates/hpa.yaml</span><span class="code-lang">yaml</span></div>
    <pre>apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 3
  maxReplicas: 100
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 75</pre></div></section>""",
          
    "benchmarking": """<section class="chapter" id="benchmarking">
    <div class="chapter-label">Chapter 29</div>
    <h1>Performance: Micro-Benchmarking & p99</h1>
    <p>Never guess at performance optimizations. We use the <code>criterion</code> crate to perform statistically rigorous micro-benchmarks on our Rust functions, tracking p99 tail latency and instruction-level cycle counts to prevent performance regressions in CI/CD.</p>
    <div class="code-block"><div class="code-header"><span class="code-filename">benches/my_benchmark.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">criterion</span>::{<span class="type">black_box</span>, <span class="type">criterion_group</span>, <span class="type">criterion_main</span>, <span class="type">Criterion</span>};

<span class="kw">fn</span> <span class="fn">bench_hashing</span>(c: &amp;<span class="kw">mut</span> <span class="type">Criterion</span>) {
    c.<span class="fn">bench_function</span>(<span class="str">"argon2id_hash"</span>, |b| {
        <span class="cmt">// black_box prevents the compiler from optimizing away the loop</span>
        b.<span class="fn">iter</span>(|| hash_password(<span class="type">black_box</span>(<span class="str">"password123"</span>)))
    });
}
<span class="mac">criterion_group!</span>(benches, bench_hashing);
<span class="mac">criterion_main!</span>(benches);</pre></div></section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive expert patches applied to all remaining chapters.")
