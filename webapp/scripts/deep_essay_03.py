import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="axum">
    <div class="chapter-label">Chapter 03</div>
    <h1>Intensive Deep Dive: Axum, Tower, & Backpressure</h1>

    <h2>1. The Illusion of Web Frameworks</h2>
    <p>Junior engineers often view web frameworks like Django, Express, or Axum as magical black boxes. They write a function, attach a routing macro (like <code>#[get("/")]</code>), and somehow HTTP requests are magically translated into function invocations. To operate at an expert, production-grade level in Rust, you must brutally deconstruct this illusion. Axum is not actually a web framework; it is a microscopic layer of syntactic sugar built entirely upon the mathematical foundation of <strong>Tower</strong> and the <strong>Tokio Asynchronous Runtime</strong>.</p>
    <p>To master network programming in Rust, you must understand exactly how a TCP socket byte stream is parsed by <code>hyper</code>, how it is converted into a <code>http::Request</code>, and how that request is mathematically mapped through a pipeline of <code>tower::Service</code> traits.</p>

    <h2>2. Deconstructing `tower::Service`</h2>
    <p>The <code>tower::Service</code> trait is the most critical abstraction in the entire Rust backend ecosystem. It represents an asynchronous mathematical function that accepts a Request and yields a Response, or an Error. Every single component of Axum—every router, every endpoint handler, every piece of middleware—is fundamentally just a struct that implements <code>tower::Service</code>.</p>
    
    <div class="code-block"><div class="code-header"><span class="code-filename">tower/src/service.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">pub trait</span> <span class="type">Service</span>&lt;Request&gt; {
    <span class="cmt">/// Responses given by the service.</span>
    <span class="kw">type</span> <span class="type">Response</span>;

    <span class="cmt">/// Errors produced by the service.</span>
    <span class="kw">type</span> <span class="type">Error</span>;

    <span class="cmt">/// The future response value.</span>
    <span class="kw">type</span> <span class="type">Future</span>: <span class="type">Future</span>&lt;Output = <span class="type">Result</span>&lt;<span class="kw">Self</span>::<span class="type">Response</span>, <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt;;

    <span class="cmt">/// Returns `Poll::Ready(Ok(()))` when the service is able to process requests.</span>
    <span class="kw">fn</span> <span class="fn">poll_ready</span>(&amp;<span class="kw">mut self</span>, cx: &amp;<span class="kw">mut</span> <span class="type">Context</span>&lt;<span class="lifetime">'_</span>&gt;) -&gt; <span class="type">Poll</span>&lt;<span class="type">Result</span>&lt;(), <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt;;

    <span class="cmt">/// Process the request and return the response asynchronously.</span>
    <span class="kw">fn</span> <span class="fn">call</span>(&amp;<span class="kw">mut self</span>, req: Request) -&gt; <span class="kw">Self</span>::<span class="type">Future</span>;
}</pre></div>

    <p>This trait is remarkably simple, but its implications are profound. Because everything implements <code>Service</code>, you can wrap Services inside of other Services indefinitely. This is known as the <strong>Decorator Pattern</strong>, and it is how middleware is constructed. An authentication middleware is simply a <code>Service</code> that intercepts the <code>Request</code>, checks the JWT, and if valid, passes the <code>Request</code> to the inner <code>Service</code> (the router), which then passes it to the inner <code>Service</code> (your handler).</p>

    <h2>3. The Mathematics of Backpressure</h2>
    <p>A critical observer will notice a strange detail in the <code>Service</code> trait. Why does <code>poll_ready</code> exist? If a Service is just a function that takes a request and returns a future, why not just call <code>call</code> directly? The answer lies in <strong>Backpressure</strong>, the single most important concept for preventing server crashes in hyperscale distributed systems.</p>
    <p>Imagine your Rust API is connected to a Postgres database. The database is currently under extreme load, performing a massive sequential scan, and queries are taking 5 seconds to complete. Suddenly, a traffic spike hits your API, sending 100,000 HTTP requests per second. If you use a naive framework that simply accepts connections and calls the handler, Tokio will spawn 100,000 asynchronous tasks. All 100,000 tasks will attempt to connect to Postgres. Because Postgres is busy, these tasks will wait.</p>
    <p>As the tasks wait, they consume heap memory (for the State Machine variables). Within milliseconds, your Rust server will consume all available RAM and the Linux kernel will instantly execute the OOM (Out-Of-Memory) Killer, terminating your process. You have accidentally executed a Denial of Service (DoS) attack against yourself.</p>

    <h3>3.1 Load Shedding via `poll_ready`</h3>
    <p>The <code>poll_ready</code> method mathematically prevents this. Before a caller (like the Hyper HTTP server) is allowed to invoke the <code>call</code> method, it <em>must</em> invoke <code>poll_ready</code>. If the Service (perhaps a Rate Limiting middleware, or a Concurrency Limiting middleware) determines that the system is at capacity, <code>poll_ready</code> returns <code>Poll::Ready(Err(...))</code>. The request is instantly rejected (shedding load) before it is even parsed, before a Tokio task is spawned, and before any memory is consumed.</p>
    <p>This allows your server to degrade gracefully. Instead of crashing, it simply returns <code>503 Service Unavailable</code> to excess traffic while successfully serving the traffic it can handle.</p>

    <h2>4. Writing Expert-Level Custom Middleware</h2>
    <p>While standard crates like <code>tower-http</code> provide excellent middleware (Trace, Timeout, Compression), true engineering mastery requires the ability to write custom <code>Service</code> implementations to solve bespoke business problems.</p>
    <p>Let us write an intensive, highly advanced custom middleware from scratch. We will build an <strong>Atomic Concurrency Limiter</strong>. This middleware will track the exact number of requests currently executing in the inner service. If the concurrent requests exceed a hard limit, it will apply backpressure and instantly reject the request with a 429 Too Many Requests HTTP status.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/middleware/concurrency.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">std</span>::<span class="type">sync</span>::<span class="type">atomic</span>::{<span class="type">AtomicUsize</span>, <span class="type">Ordering</span>};
<span class="kw">use</span> <span class="type">std</span>::<span class="type">sync</span>::<span class="type">Arc</span>;
<span class="kw">use</span> <span class="type">std</span>::<span class="type">task</span>::{<span class="type">Context</span>, <span class="type">Poll</span>};
<span class="kw">use</span> <span class="type">tower</span>::<span class="type">Service</span>;
<span class="kw">use</span> <span class="type">futures_util</span>::<span class="type">future</span>::<span class="type">BoxFuture</span>;
<span class="kw">use</span> <span class="type">axum</span>::{<span class="type">response</span>::<span class="type">IntoResponse</span>, <span class="type">http</span>::{<span class="type">Request</span>, <span class="type">StatusCode</span>}};

<span class="attr">#[derive(Clone)]</span>
<span class="kw">pub struct</span> <span class="type">ConcurrencyLimiter</span>&lt;S&gt; {
    inner: S,
    active_requests: <span class="type">Arc</span>&lt;<span class="type">AtomicUsize</span>&gt;,
    max_concurrent: <span class="type">usize</span>,
}

<span class="kw">impl</span>&lt;S, <span class="type">ReqBody</span>&gt; <span class="type">Service</span>&lt;<span class="type">Request</span>&lt;<span class="type">ReqBody</span>&gt;&gt; <span class="kw">for</span> <span class="type">ConcurrencyLimiter</span>&lt;S&gt;
<span class="kw">where</span>
    S: <span class="type">Service</span>&lt;<span class="type">Request</span>&lt;<span class="type">ReqBody</span>&gt;, <span class="type">Response</span> = <span class="type">axum</span>::<span class="type">response</span>::<span class="type">Response</span>&gt; + <span class="type">Clone</span> + <span class="type">Send</span> + <span class="lifetime">'static</span>,
    S::<span class="type">Future</span>: <span class="type">Send</span> + <span class="lifetime">'static</span>,
{
    <span class="kw">type</span> <span class="type">Response</span> = S::<span class="type">Response</span>;
    <span class="kw">type</span> <span class="type">Error</span> = S::<span class="type">Error</span>;
    <span class="kw">type</span> <span class="type">Future</span> = <span class="type">BoxFuture</span>&lt;<span class="lifetime">'static</span>, <span class="type">Result</span>&lt;<span class="kw">Self</span>::<span class="type">Response</span>, <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt;;

    <span class="kw">fn</span> <span class="fn">poll_ready</span>(&amp;<span class="kw">mut self</span>, cx: &amp;<span class="kw">mut</span> <span class="type">Context</span>&lt;<span class="lifetime">'_</span>&gt;) -&gt; <span class="type">Poll</span>&lt;<span class="type">Result</span>&lt;(), <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt; {
        <span class="cmt">// Backpressure Check: Are we over capacity?</span>
        <span class="kw">let</span> current = <span class="kw">self</span>.active_requests.load(<span class="type">Ordering</span>::<span class="type">Acquire</span>);
        <span class="kw">if</span> current &gt;= <span class="kw">self</span>.max_concurrent {
            <span class="cmt">// We must wait until capacity drops. In a real system, we would register a Waker here.</span>
            <span class="cmt">// For strict load shedding, returning an error instantly protects the server.</span>
            <span class="cmt">// We defer to inner's poll_ready to see if the inner service itself is clogged.</span>
        }
        <span class="kw">self</span>.inner.poll_ready(cx)
    }

    <span class="kw">fn</span> <span class="fn">call</span>(&amp;<span class="kw">mut self</span>, req: <span class="type">Request</span>&lt;<span class="type">ReqBody</span>&gt;) -&gt; <span class="kw">Self</span>::<span class="type">Future</span> {
        <span class="kw">let</span> current = <span class="kw">self</span>.active_requests.load(<span class="type">Ordering</span>::<span class="type">Acquire</span>);
        
        <span class="cmt">// If we somehow bypassed poll_ready (or concurrency spiked between poll_ready and call)</span>
        <span class="kw">if</span> current &gt;= <span class="kw">self</span>.max_concurrent {
            <span class="kw">return</span> <span class="type">Box</span>::<span class="fn">pin</span>(<span class="kw">async move</span> {
                <span class="type">Ok</span>((<span class="type">StatusCode</span>::<span class="type">TOO_MANY_REQUESTS</span>, <span class="str">"System at absolute capacity. Load Shedding."</span>).<span class="fn">into_response</span>())
            });
        }

        <span class="cmt">// Increment atomic counter</span>
        <span class="kw">self</span>.active_requests.fetch_add(<span class="num">1</span>, <span class="type">Ordering</span>::<span class="type">Release</span>);
        <span class="kw">let</span> active_requests = <span class="kw">self</span>.active_requests.clone();
        
        <span class="kw">let</span> <span class="kw">mut</span> inner = <span class="kw">self</span>.inner.clone();
        <span class="kw">let</span> fut = inner.call(req);

        <span class="type">Box</span>::<span class="fn">pin</span>(<span class="kw">async move</span> {
            <span class="cmt">// Await the inner future</span>
            <span class="kw">let</span> result = fut.<span class="kw">await</span>;
            <span class="cmt">// Decrement atomic counter instantly when the future completes</span>
            active_requests.fetch_sub(<span class="num">1</span>, <span class="type">Ordering</span>::<span class="type">Release</span>);
            result
        })
    }
}</pre></div>

    <h2>5. The `Pin` Struct and Memory Addresses</h2>
    <p>In the code block above, you will notice the usage of <code>Box::pin</code>. Why must we pin the future? This is a fundamental concept in Rust's asynchronous architecture. When a Future is created (by calling an <code>async fn</code>), it is essentially a struct containing all the local variables of that function. If that Future contains references to itself (e.g., a local variable pointing to another local variable within the same function), moving that Future in memory would invalidate the memory address, causing a catastrophic segmentation fault.</p>
    <p>To prevent this, Rust introduces the <code>Pin</code> wrapper. By pinning a Future, you mathematically guarantee to the compiler that the Future will never be moved to a different memory address for the remainder of its lifecycle. This allows the compiler to safely generate Self-Referential Structs, which are strictly required for zero-cost State Machine generators. By boxing and pinning our custom middleware future, we satisfy the rigid memory-safety requirements of the Tokio runtime while dynamically constructing our execution graph.</p>
</section>"""

pattern = r'<section class="chapter" id="axum">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 03.")
