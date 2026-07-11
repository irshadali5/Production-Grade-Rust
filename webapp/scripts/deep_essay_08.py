import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="telemetry">
    <div class="chapter-label">Chapter 08</div>
    <h1>Intensive Deep Dive: Telemetry & Asynchronous Spans</h1>

    <h2>1. The Impossibility of `println!` in Distributed Systems</h2>
    <p>In a simple synchronous application, logging is trivial: you use <code>println!</code> or <code>log::info!</code> to write text to standard output. However, in a hyperscale asynchronous Rust application powered by Tokio, standard logging is completely useless. Tokio multiplexes thousands of concurrent tasks onto a handful of OS threads. If you look at standard output, you will see a chaotic, interleaved mess of log lines from thousands of different users. You have absolutely no mathematical way to prove which log line belongs to which HTTP request.</p>
    <p>If a user reports a 500 Internal Server Error, and your application is processing 10,000 requests per second, finding the specific log lines that caused their error using grep is like finding a needle in a hurricane. We must abandon standard logging and adopt <strong>Structured Tracing</strong>.</p>

    <h2>2. Spans, Events, and the `tracing` Crate</h2>
    <p>To solve the concurrency problem, we use the <code>tracing</code> crate. Instead of emitting isolated strings, <code>tracing</code> operates on <strong>Spans</strong>. A Span represents a period of time with a distinct beginning and end (e.g., "process_payment"). Any log lines (called <strong>Events</strong>) emitted while inside that Span are mathematically bound to it.</p>
    <p>Crucially, because Rust is asynchronous, a single Span might be paused and resumed dozens of times as Tokio yields execution to wait for database I/O. The <code>tracing</code> crate tracks this context dynamically. Using the <code>#[instrument]</code> macro on an <code>async fn</code> forces the Rust compiler to automatically generate a Span, record the function's arguments as structured JSON key-value pairs, and attach the Span to the Future. Whenever Tokio polls the Future, the Span is entered; whenever Tokio yields, the Span is exited. This guarantees that all logs are perfectly grouped by request, regardless of which physical CPU core executed them.</p>

    <h2>3. The W3C Trace Context & Distributed Propagation</h2>
    <p>Grouping logs within a single Rust binary is only half the battle. In a modern architecture, a single user action might traverse an API Gateway, a Rust monolith, a Python machine learning worker, and a Postgres database. To debug a latency spike, we must track the request across the physical network boundaries.</p>
    <p>We implement the <strong>W3C Trace Context</strong> specification. When a request hits the edge of our network, the API Gateway generates a cryptographically random 128-bit <code>trace_id</code>. It injects this ID into the HTTP headers (specifically, the <code>traceparent</code> header). When our Rust Axum server receives the HTTP request, our <code>tower::Service</code> middleware intercepts the headers, extracts the <code>trace_id</code>, and attaches it to the root tracing Span.</p>
    <p>If the Rust server then makes an HTTP request to an external billing service, it injects that exact same <code>trace_id</code> into the outgoing headers. This is called <strong>Distributed Context Propagation</strong>. When all these microservices export their telemetry, we can reconstruct a single, continuous waterfall graph of the entire network transaction.</p>

    <h2>4. OpenTelemetry (OTLP) and gRPC Batch Exporting</h2>
    <p>Where does this telemetry data go? Writing gigabytes of structured JSON to a local log file will destroy the server's NVMe SSD through write amplification. Instead, we use <strong>OpenTelemetry (OTel)</strong>.</p>
    <p>We configure the Rust <code>tracing-opentelemetry</code> layer to act as an asynchronous telemetry pipeline. When a Span closes, it is not written to disk. It is pushed into a lock-free memory buffer. A background Tokio thread continuously monitors this buffer. Every 5 seconds, it takes a massive batch of thousands of Spans, compresses them, and exports them directly to an observability backend (like Jaeger, Datadog, or Honeycomb) using the <strong>OTLP (OpenTelemetry Protocol) over gRPC</strong>.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/telemetry.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">tracing_subscriber</span>::{<span class="type">layer</span>::<span class="type">SubscriberExt</span>, <span class="type">Registry</span>, <span class="type">util</span>::<span class="type">SubscriberInitExt</span>};
<span class="kw">use</span> <span class="type">opentelemetry_otlp</span>::<span class="type">WithExportConfig</span>;
<span class="kw">use</span> <span class="type">opentelemetry_sdk</span>::<span class="type">trace</span>::{<span class="kw">self</span>, <span class="type">Sampler</span>};

<span class="kw">pub fn</span> <span class="fn">init_telemetry</span>() {
    <span class="cmt">// 1. Configure the OTLP Exporter to send data via gRPC</span>
    <span class="kw">let</span> tracer = <span class="type">opentelemetry_otlp</span>::<span class="fn">new_pipeline</span>()
        .<span class="fn">tracing</span>()
        .<span class="fn">with_exporter</span>(
            <span class="type">opentelemetry_otlp</span>::<span class="fn">new_exporter</span>()
                .<span class="fn">tonic</span>() <span class="cmt">// Use high-performance gRPC</span>
                .<span class="fn">with_endpoint</span>(<span class="str">"http://jaeger:4317"</span>)
        )
        <span class="cmt">// 2. Configure a Batch Span Processor to prevent blocking the main application thread</span>
        .<span class="fn">with_trace_config</span>(
            <span class="type">trace</span>::<span class="fn">config</span>()
                .<span class="fn">with_sampler</span>(<span class="type">Sampler</span>::<span class="type">AlwaysOn</span>)
        )
        .<span class="fn">install_batch</span>(<span class="type">opentelemetry_sdk</span>::<span class="type">runtime</span>::<span class="type">Tokio</span>)
        .unwrap();

    <span class="cmt">// 3. Create the Tracing Layer that maps Rust Spans to OTel Spans</span>
    <span class="kw">let</span> telemetry_layer = <span class="type">tracing_opentelemetry</span>::<span class="fn">layer</span>().<span class="fn">with_tracer</span>(tracer);

    <span class="cmt">// 4. Compose the global subscriber</span>
    <span class="type">Registry</span>::<span class="fn">default</span>()
        .<span class="fn">with</span>(<span class="type">tracing_subscriber</span>::<span class="type">EnvFilter</span>::<span class="fn">new</span>(<span class="str">"info"</span>))
        .<span class="fn">with</span>(telemetry_layer)
        .<span class="fn">init</span>();
}</pre></div>

    <p>By transmitting batches via gRPC, we utilize HTTP/2 multiplexing, drastically reducing TCP overhead. The Rust API can process 100,000 requests per second while exporting millions of telemetry spans with negligible impact on CPU or latency, achieving absolute observability at hyperscale.</p>
</section>"""

pattern = r'<section class="chapter" id="telemetry">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 08.")
