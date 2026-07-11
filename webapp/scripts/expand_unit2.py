import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "database": """<section class="chapter" id="database">
    <div class="chapter-label">Chapter 05</div>
    <h1>SQLx & Postgres Internals</h1>

    <h2>The Connection Multiplexing Bottleneck</h2>
    <p>A common misconception in backend engineering is that more database connections equal higher throughput. This is mathematically false. Postgres operates using a process-per-connection model. Every time your Rust application opens a connection to Postgres, the Postgres OS process forks, allocating roughly 10MB of RAM and occupying an OS process slot. If your Rust application, running on Tokio, effortlessly spawns 10,000 concurrent asynchronous tasks, and each task attempts to checkout a database connection, Postgres will instantly attempt to fork 10,000 processes. This results in catastrophic memory exhaustion and CPU context-switching thrash, effectively taking your database offline.</p>
    <p>The solution is not to increase the <code>max_connections</code> setting in <code>postgresql.conf</code>. The solution is <strong>Connection Multiplexing via PgBouncer</strong>. PgBouncer sits between your Rust application and Postgres. Your Rust application opens 10,000 connections to PgBouncer. PgBouncer, operating in "transaction pooling" mode, maintains a tiny, fixed pool of (e.g., 50) physical connections to Postgres. It rapidly assigns a physical connection to an incoming Rust task for the exact duration of a transaction (milliseconds), and then instantly reassigns it to the next task. This keeps Postgres CPU utilization perfectly flat while allowing your Rust app to handle hyperscale traffic.</p>

    <h2>Compile-Time Query Verification with SQLx</h2>
    <p>Object-Relational Mappers (ORMs) like Diesel or Prisma are excellent for simple CRUD applications, but they often abstract away the power of raw SQL, leading to inefficient N+1 queries. We use <strong>SQLx</strong>, an async, pure Rust SQL crate that does not use a Domain Specific Language (DSL).</p>
    <p>SQLx's superpower is the <code>query!</code> macro. When you compile your Rust code, the SQLx macro actually connects to your live Postgres development database at compile-time. It executes a `PREPARE` statement to ask Postgres for the exact AST of the query, verifying that the syntax is correct, the tables exist, and the column types mathematically map to your Rust structs. If you misspell a column name in a SQL string, your Rust code will refuse to compile. This provides the safety of an ORM with the raw, unadulterated performance of native SQL.</p>

    <h2>Write-Ahead Logging (WAL) and Durability</h2>
    <p>When you execute an `INSERT` statement and Postgres returns a successful response, how do you know the data actually hit the physical hard drive? Hard drives are slow, and waiting for the magnetic disk to spin (or SSD blocks to erase) for every transaction would cripple performance. Postgres achieves ACID durability using a <strong>Write-Ahead Log (WAL)</strong>.</p>
    <p>When your Rust code commits a transaction, Postgres writes the change to the WAL file sequentially. Sequential disk writes are orders of magnitude faster than random-access tree updates. Once the sequential WAL write is flushed to disk via `fsync()`, Postgres returns a success to Rust. The actual database data files (the heap and B-trees) are updated asynchronously in the background. If the server loses power, Postgres simply reads the WAL upon reboot and replays any missing transactions, guaranteeing zero data loss while maximizing IOPS.</p>
    
    <div class="code-block"><div class="code-header"><span class="code-filename">src/db.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="cmt">// Connect to PgBouncer port (6432), not directly to Postgres (5432)</span>
<span class="kw">let</span> pool = <span class="type">PgPoolOptions</span>::<span class="fn">new</span>()
    .max_connections(<span class="num">50</span>)
    .acquire_timeout(<span class="type">Duration</span>::<span class="fn">from_secs</span>(<span class="num">2</span>))
    .connect_with(config.with_db()).<span class="kw">await</span>?;</pre></div>
</section>""",

    "telemetry": """<section class="chapter" id="telemetry">
    <div class="chapter-label">Chapter 06</div>
    <h1>Telemetry & Distributed Tracing (OTLP)</h1>

    <h2>The Inadequacy of Standard Logging</h2>
    <p>In a monolithic application, writing <code>println!("User created: {}", user.id)</code> is sufficient. You can tail the application logs and read the narrative sequentially. In a modern distributed architecture, a single user request might traverse an API Gateway, an Authentication Microservice, a Rust Worker Node, and a Postgres Database. If the request fails, grepping through 4 different log streams for a specific error is like finding a needle in a haystack.</p>
    <p>We solve this using <strong>Distributed Tracing</strong>. Tracing elevates logging from simple text strings to structured, hierarchical metadata. We use the <code>tracing</code> crate in Rust, which allows us to define "Spans". A Span represents a duration of time with a definite start and end, and can contain key-value properties. When a function executes, it enters a span. If it calls another function, that child function enters a nested span.</p>

    <h2>OpenTelemetry (OTLP) and W3C Trace Context</h2>
    <p>To track a request across network boundaries (e.g., from our API Gateway to our Rust Worker), we utilize the <strong>OpenTelemetry (OTLP)</strong> standard. When a request enters the system, OpenTelemetry generates a globally unique <code>Trace ID</code>.</p>
    <p>When our Rust service makes an HTTP request to another microservice, we use the <strong>W3C Trace Context</strong> specification to inject this Trace ID into the HTTP Headers (specifically, the <code>traceparent</code> header). The receiving microservice reads this header, adopts the Trace ID, and continues the trace. This forms an unbroken, mathematical chain of causality across your entire infrastructure.</p>

    <h2>Visualizing the Critical Path with Jaeger</h2>
    <p>We use <code>tracing-opentelemetry</code> to batch and export all of these spans asynchronously to a centralized collector (like Jaeger or DataDog). The collector mathematically reconstructs the spans using their Parent IDs and visualizes them as a waterfall diagram.</p>
    <p>This allows us to identify the exact <strong>Critical Path</strong> of a request. If an endpoint takes 2.5 seconds, Jaeger will show you instantly that 2.4 seconds were spent waiting for a poorly indexed Postgres query inside a downstream microservice, completely eliminating the guesswork from performance debugging.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/telemetry.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">opentelemetry</span>::<span class="type">global</span>;
<span class="kw">use</span> <span class="type">tracing_subscriber</span>::{<span class="type">layer</span>::<span class="type">SubscriberExt</span>, <span class="type">Registry</span>};

<span class="kw">let</span> tracer = <span class="type">opentelemetry_otlp</span>::<span class="fn">new_pipeline</span>()
    .tracing()
    .with_exporter(<span class="type">opentelemetry_otlp</span>::<span class="fn">new_exporter</span>().<span class="fn">tonic</span>())
    .install_batch(<span class="type">opentelemetry</span>::<span class="type">runtime</span>::<span class="type">Tokio</span>).unwrap();

<span class="kw">let</span> telemetry = <span class="type">tracing_opentelemetry</span>::<span class="fn">layer</span>().<span class="fn">with_tracer</span>(tracer);</pre></div>
</section>""",

    "errors": """<section class="chapter" id="errors">
    <div class="chapter-label">Chapter 07</div>
    <h1>Expert Error Handling & Panic Hooks</h1>

    <h2>Recoverable vs. Unrecoverable Errors</h2>
    <p>In Rust, errors are values. The <code>Result&lt;T, E&gt;</code> enum forces you to explicitly acknowledge that a function might fail. However, not all errors are created equal. We must distinguish between <strong>Recoverable Errors</strong> (where the business logic can decide to retry or return a graceful HTTP 400 to the client) and <strong>Unrecoverable Errors</strong> (like an OOM event or a corrupted memory state where the only safe option is to crash the process).</p>

    <h2>The `thiserror` and `anyhow` Paradigms</h2>
    <p>In application binaries (the top level of your codebase), it is often acceptable to use the <code>anyhow</code> crate. <code>anyhow::Error</code> is a type-erased, dynamic error type that allows you to easily propagate any error up the call stack using the <code>?</code> operator and attach contextual strings.</p>
    <p>However, inside your domain libraries and core business logic, type-erased errors are disastrous because the caller cannot easily pattern-match on them to perform specific recovery logic. Therefore, in our domain layer, we strictly use the <code>thiserror</code> crate.</p>
    <p><code>thiserror</code> provides a macro to easily derive the <code>std::error::Error</code> trait for your custom enums. By defining a meticulous enum of all possible failure states (e.g., <code>DatabaseConnectionLost</code>, <code>InvalidSubscriberEmail</code>), you provide callers with a mathematically exhaustive list of failure modes to handle.</p>

    <h2>Transparent Error Delegation</h2>
    <p>When propagating errors from an underlying crate (like <code>sqlx</code>) through your domain layer, exposing the raw <code>sqlx::Error</code> to your HTTP handlers violates the Dependency Rule of Hexagonal Architecture. We use <code>thiserror</code>'s <code>#[transparent]</code> attribute to wrap the underlying error. This allows the error to propagate up the stack while masquerading as a Domain error, preventing architectural leakage.</p>

    <h2>Centralized Panic Hooks</h2>
    <p>When an Unrecoverable Error occurs (a <code>panic!</code>), the default Rust behavior is to print the backtrace to standard error (stderr) and terminate the thread. In a containerized Kubernetes environment, capturing stderr reliably can be difficult, and you lose the structured OpenTelemetry metadata associated with the crash.</p>
    <p>To solve this, we override the default behavior using <code>std::panic::set_hook</code>. Our custom hook intercepts the panic payload, extracts the backtrace, and manually emits a <code>tracing::error!</code> event. This guarantees that the fatal crash, along with its exact thread backtrace, is safely transmitted to Jaeger or DataDog before the operating system reaps the dead process.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/error.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">thiserror</span>::<span class="type">Error</span>;

<span class="attr">#[derive(Error, Debug)]</span>
<span class="kw">pub enum</span> <span class="type">DomainError</span> {
    <span class="attr">#[error(<span class="str">"Database connection severed"</span>)]</span>
    <span class="type">Database</span>(<span class="attr">#[from]</span> <span class="type">sqlx</span>::<span class="type">Error</span>),
    
    <span class="attr">#[error(<span class="str">"Invalid subscriber format"</span>)]</span>
    <span class="type">Validation</span>(<span class="attr">#[transparent]</span> <span class="type">ValidationError</span>),
}</pre></div>
</section>""",

    "validation": """<section class="chapter" id="validation">
    <div class="chapter-label">Chapter 08</div>
    <h1>Domain Modeling: Zero-Cost Newtypes</h1>

    <h2>The Dangers of Primitive Obsession</h2>
    <p>A string in Rust (<code>String</code>) is mathematically defined as a heap-allocated, UTF-8 encoded sequence of bytes. A subscriber's email address is also represented as a string. However, an email address has strict business rules: it must contain an '@' symbol, a domain name, and cannot exceed certain lengths. If we pass raw <code>String</code> types into our database functions, we suffer from <strong>Primitive Obsession</strong>.</p>
    <p>Primitive Obsession means relying on generic data types to represent domain-specific concepts. If an HTTP handler accepts a raw <code>String</code> and passes it to the database module, the database module must blindly trust that the handler performed the necessary email validation. If a developer forgets to validate the string, invalid data (or worse, a SQL injection payload) breaches the database. This is unacceptable.</p>

    <h2>The Newtype Pattern</h2>
    <p>We solve this using Type-Driven Design and the <strong>Newtype Pattern</strong>. We create a tuple struct containing a single primitive: <code>pub struct SubscriberEmail(String);</code>. We then make the inner <code>String</code> private, so it cannot be instantiated directly.</p>
    <p>The only way to construct a <code>SubscriberEmail</code> is by passing a <code>String</code> through a public <code>parse</code> function (often implementing the <code>TryFrom</code> trait). This function contains our rigorous regex validation. If validation fails, it returns an Error. If it succeeds, it returns the <code>SubscriberEmail</code> struct.</p>
    <p>Now, our database functions require a <code>SubscriberEmail</code> as their argument. The Rust compiler structurally guarantees that it is impossible for an unvalidated string to reach the database. We have offloaded our business logic assertions to the compile-time type checker.</p>

    <h2>Zero-Cost Abstractions via `#[repr(transparent)]`</h2>
    <p>Wrapping primitives in custom structs might seem inefficient. Does instantiating a <code>SubscriberEmail</code> struct add memory overhead compared to a raw <code>String</code>? In Rust, the answer is no, thanks to <strong>Zero-Cost Abstractions</strong>.</p>
    <p>By annotating our Newtype with <code>#[repr(transparent)]</code>, we instruct the Rust compiler that the memory layout of <code>SubscriberEmail</code> must be mathematically identical to the memory layout of its inner <code>String</code>. During compilation, LLVM optimizes the struct away completely. At runtime, there is absolutely zero CPU or memory overhead; it is executed as raw String pointers, giving us compile-time safety with native C-level performance.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/domain/email.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="attr">#[derive(Debug, Clone)]</span>
<span class="attr">#[repr(transparent)]</span>
<span class="kw">pub struct</span> <span class="type">SubscriberEmail</span>(<span class="type">String</span>);

<span class="kw">impl</span> <span class="type">SubscriberEmail</span> {
    <span class="kw">pub fn</span> <span class="fn">parse</span>(s: <span class="type">String</span>) -&gt; <span class="type">Result</span>&lt;<span class="kw">Self</span>, <span class="type">String</span>&gt; {
        <span class="kw">if</span> validator::<span class="fn">validate_email</span>(&amp;s) { <span class="type">Ok</span>(<span class="kw">Self</span>(s)) } <span class="kw">else</span> { <span class="type">Err</span>(<span class="str">"Invalid format"</span>.into()) }
    }
}</pre></div>
</section>""",

    "email": """<section class="chapter" id="email">
    <div class="chapter-label">Chapter 09</div>
    <h1>Email Client & SMTP Internals</h1>

    <h2>Abstracting the Email Provider</h2>
    <p>Sending emails in production requires interacting with third-party providers like Postmark, SendGrid, or AWS SES via their REST APIs or SMTP relays. Tightly coupling our business logic to a specific provider is a violation of Hexagonal Architecture. If Postmark suffers an outage, we should be able to hot-swap to SendGrid by simply changing an adapter, not rewriting our domain.</p>
    <p>We define a core <code>EmailSender</code> trait in our Domain crate. We then implement a <code>PostmarkClient</code> struct that fulfills this trait using the <code>reqwest</code> HTTP client. This strict boundary allows us to mock the email client during tests.</p>

    <h2>Deliverability: SPF and DKIM Mathematics</h2>
    <p>Sending an HTTP request to Postmark is easy; ensuring the email actually reaches the user's inbox (and not the spam folder) requires cryptographic DNS configuration. The modern email ecosystem relies on two mathematical proofs to verify sender identity: SPF and DKIM.</p>
    <p><strong>SPF (Sender Policy Framework)</strong> is a DNS TXT record that whitelists the exact IP addresses (e.g., Postmark's servers) authorized to send emails on behalf of your domain. When Gmail receives an email, it checks the IP address of the sender against your domain's SPF record. If it doesn't match, the email is rejected as spoofing.</p>
    <p><strong>DKIM (DomainKeys Identified Mail)</strong> uses asymmetric RSA cryptography. You publish a public key in your DNS records. Your email provider signs the headers and body of every outgoing email with the corresponding private key. When Gmail receives the email, it uses the public key from your DNS to mathematically verify the signature. This guarantees the email was not tampered with in transit.</p>

    <h2>Robust Testing with Wiremock</h2>
    <p>How do we test our <code>PostmarkClient</code> in CI/CD without actually sending test emails and getting our domain blacklisted by spam filters? We use the <code>wiremock</code> crate.</p>
    <p><code>wiremock</code> is an incredibly powerful testing tool that spins up a real, local HTTP server on a random port during your test execution. We configure our <code>PostmarkClient</code> to point its <code>base_url</code> at the wiremock server. We can then dynamically program the wiremock server to return specific responses (e.g., 200 OK, 500 Internal Server Error, or network timeouts) to mathematically verify that our Rust code handles provider failures gracefully.</p>
</section>""",

    "testing": """<section class="chapter" id="testing">
    <div class="chapter-label">Chapter 10</div>
    <h1>Testing: Mathematical Concurrency Proofs</h1>

    <h2>The Fragility of Example-Based Testing</h2>
    <p>Standard unit testing relies on example-based assertions: you pass `x=2`, you expect `y=4`. This is insufficient for production systems because humans are remarkably bad at predicting edge cases. Example-based tests prove that the code works for the specific inputs you thought of; they do not prove that the code is correct.</p>
    <p>To elevate our testing, we use <strong>Property-Based Testing</strong> via the <code>proptest</code> crate. Instead of hardcoding "test@example.com", we define mathematical properties our code must uphold (e.g., "The email parser must never panic, regardless of input"). <code>proptest</code> then generates thousands of random, mutated edge-cases (UTF-8 anomalies, null bytes, massively nested strings) and bombards our parser to ensure the property holds true. If it finds a failing input, it automatically "shrinks" it to the smallest reproducible test case.</p>

    <h2>The Impossible Problem of Concurrency Testing</h2>
    <p>While Property-Based Testing solves data edge cases, it cannot solve <strong>Concurrency Edge Cases</strong>. In a multi-threaded Rust application, the operating system's scheduler determines the exact order in which threads execute instructions. A race condition or deadlock might only occur if Thread B executes a specific instruction precisely 2 nanoseconds after Thread A writes to a shared <code>AtomicUsize</code>.</p>
    <p>Writing a standard unit test for a concurrent data structure (like the Singleflight cache deduplicator we built) is useless. The test might pass 10,000 times on your machine and then fail in production because the OS schedule was slightly different. You cannot reliably test concurrency using standard tools.</p>

    <h2>Proving Correctness with `loom`</h2>
    <p>We solve this impossible problem using the <strong>loom</strong> crate, developed by AWS for verifying the Tokio runtime itself. Loom is a model checker for concurrent Rust code.</p>
    <p>When you run a test under <code>loom</code>, it intercepts every single atomic operation, mutex lock, and thread spawn. It then systematically and mathematically permutes <strong>every possible valid thread interleaving schedule</strong> defined by the C++11 memory model. If there is even one single microscopic thread schedule that results in a data race, a deadlock, or a use-after-free, <code>loom</code> will find it and intentionally trigger a panic, outputting the exact sequence of thread executions that caused the failure. When a <code>loom</code> test passes, you have mathematically proven the absence of concurrency bugs in your architecture.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">tests/concurrency.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="attr">#[test]</span>
<span class="kw">fn</span> <span class="fn">test_concurrent_singleflight</span>() {
    <span class="cmt">// Loom intercepts all atomic operations and forces every possible thread schedule</span>
    <span class="type">loom</span>::<span class="type">model</span>(|| {
        <span class="kw">let</span> sf = <span class="type">Arc</span>::<span class="fn">new</span>(<span class="type">Singleflight</span>::<span class="fn">new</span>());
        <span class="type">loom</span>::<span class="type">thread</span>::<span class="fn">spawn</span>({ <span class="cmt">/* Thread 1 execution */</span> });
        <span class="type">loom</span>::<span class="type">thread</span>::<span class="fn">spawn</span>({ <span class="cmt">/* Thread 2 execution */</span> });
    });
}</pre></div>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to Unit 2 (Chapters 05-10).")
