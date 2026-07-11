import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="reliability">
    <div class="chapter-label">Chapter 16</div>
    <h1>Intensive Deep Dive: Little's Law, Circuit Breakers, & Cryptographic Jitter</h1>

    <h2>1. The Mathematics of Cascading Failures (Little's Law)</h2>
    <p>In a distributed system, reliability is not a software design pattern; it is a mathematical property defined by <strong>Queueing Theory</strong>. The foundational equation of Queueing Theory is Little's Law: <code>L = &lambda;W</code>, where <code>L</code> is the total number of concurrent requests in the system, <code>&lambda;</code> is the arrival rate (requests per second), and <code>W</code> is the average processing time per request.</p>
    <p>Assume your Rust API receives 1,000 requests per second (<code>&lambda; = 1000</code>), and your external Postgres database responds in 0.05 seconds (<code>W = 0.05</code>). According to Little's Law, your server handles exactly 50 concurrent requests at any given microsecond. Tokio effortlessly multiplexes these 50 requests across your CPU cores.</p>
    <p>Now, imagine Postgres suffers a minor degradation, and its response time spikes to 5.0 seconds. Your arrival rate remains 1,000 req/sec. Instantly, <code>L = 1000 * 5.0 = 5000</code>. Your Rust API is now holding 5,000 concurrent requests open. Each request consumes a TCP socket file descriptor, memory for the HTTP payload, and a Tokio task overhead. Within seconds, your server physically exhausts its RAM and OS file descriptors. The Linux Kernel's OOM Killer assassinates your Rust process. A minor database slowdown has mathematically caused a total Cascading Failure of your entire API tier.</p>

    <h2>2. The Circuit Breaker Pattern</h2>
    <p>To prevent Cascading Failures, we must actively intervene in the <code>W</code> (processing time) variable of Little's Law. We wrap all external network calls in a <strong>Circuit Breaker</strong> (e.g., via the <code>tower</code> crate).</p>
    <p>A Circuit Breaker operates like a physical electrical fuse. It monitors the failure rate and latency of the external Postgres database. If 5 consecutive queries timeout or exceed 2.0 seconds, the Circuit Breaker "trips" into an <strong>Open State</strong>.</p>
    <p>While the circuit is open, the Circuit Breaker intercepts all incoming database queries and instantly returns an error (e.g., <code>503 Service Unavailable</code>) without even attempting to contact the database. By failing instantly, the processing time <code>W</code> drops to 0.001 seconds. Little's Law dictates that the concurrent load <code>L</code> plummets immediately, freeing up the Tokio threads. Your server remains perfectly healthy and can continue serving cached data or other non-database routes.</p>

    <h2>3. The Thundering Herd and Cryptographic Jitter</h2>
    <p>After a designated timeout (e.g., 30 seconds), the Circuit Breaker enters a <strong>Half-Open State</strong>, allowing a single test request through to see if Postgres has recovered. If it succeeds, the circuit closes, and normal operation resumes. However, if 5,000 waiting background workers immediately retry their failed jobs the second the database recovers, they will instantly knock Postgres offline again—a phenomenon known as the <strong>Thundering Herd</strong>.</p>
    <p>We eliminate this using <strong>Exponential Backoff with Cryptographic Jitter</strong>. Instead of retrying every 1 second, we double the delay mathematically: 1s, 2s, 4s, 8s, 16s. This exponential decay prevents the database from being overwhelmed.</p>
    <p>Crucially, if 1,000 Kubernetes Pods all crashed at exactly 12:00:00, they will all retry at exactly 12:00:01, 12:00:03, etc., still creating synchronized spikes. We break this synchronization by injecting <strong>Jitter</strong>. We use a cryptographically secure random number generator to apply variance to the backoff duration (e.g., 1.1s, 2.8s, 4.2s). By randomizing the retry intervals across the cluster, we physically scatter the network load, ensuring the database receives a smooth, manageable stream of recovery traffic.</p>
</section>"""

pattern = r'<section class="chapter" id="reliability">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 16 applied.")
