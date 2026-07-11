import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="gateway">
    <div class="chapter-label">Chapter 20</div>
    <h1>Intensive Deep Dive: Token Buckets, Leaky Buckets, & LUA Pipelining</h1>

    <h2>1. The Economics and Physics of API Abuse</h2>
    <p>When operating a public-facing API, specifically one that interfaces with expensive external LLMs (where you are charged per token), a single malicious scraper or a runaway <code>while(true)</code> loop on a client can literally bankrupt your company in hours. A production-grade system must implement a ruthless API Gateway that enforces cryptographically secure rate limiting at the absolute edge of the network, before the request ever reaches your core business logic.</p>

    <h2>2. The Token Bucket Algorithm</h2>
    <p>The naive approach to rate limiting is the "Fixed Window" counter (e.g., allow 100 requests per minute). This is fundamentally broken due to burst mechanics: a user can send 100 requests at 12:00:59, and another 100 requests at 12:01:01, effectively hammering your database with 200 requests in 2 seconds.</p>
    <p>We solve this mathematically using the <strong>Token Bucket Algorithm</strong>. Imagine a virtual bucket with a maximum capacity of 100 tokens. A background mathematical function (based on the system clock) continuously adds 1 token to the bucket every 0.6 seconds. When a request arrives, the algorithm checks the bucket. If a token exists, it removes the token and allows the request. If the bucket is empty, it returns a <code>429 Too Many Requests</code>. This algorithm allows small, mathematically defined bursts (up to the bucket capacity), but perfectly smooths out long-term traffic to the exact refill rate.</p>

    <h2>3. The Leaky Bucket Variation for Downstream Protection</h2>
    <p>If the goal is not to limit user cost, but to protect a fragile, legacy downstream database, we use the <strong>Leaky Bucket Algorithm</strong>. In this model, incoming requests pour into the top of the bucket at any rate. However, the bucket has a small hole in the bottom, and requests drip out into the database at a perfectly constant, metronome-like rate (e.g., exactly 10 requests per second).</p>
    <p>If the incoming traffic spikes and the bucket fills up, excess requests spill over the top and are rejected. This guarantees that your downstream database receives a perfectly flat, horizontal line of traffic, rendering it completely immune to traffic spikes.</p>

    <h2>4. Atomic Concurrency via Redis LUA Scripts</h2>
    <p>Implementing these algorithms in a distributed cluster introduces a massive Race Condition. If you use a Rust worker to read the current tokens from Garnet (Redis), decrement them in Rust, and write them back, you will fail under load. If 1,000 requests arrive at the exact same millisecond, all 1,000 workers will read <code>tokens=100</code>, and all will write <code>tokens=99</code>. The rate limit is bypassed by 999 requests.</p>
    <p>We eliminate this using <strong>Atomic LUA Scripts</strong>. We write the Token Bucket mathematics as a LUA script and send it to Garnet. Garnet executes LUA scripts in a single, atomic, single-threaded transaction space. The script reads, decrements, and updates the token count entirely inside Garnet's memory, completely blocking all other operations. By combining this atomic execution with Redis TCP pipelining, we guarantee absolute thread safety across 10,000 distributed Rust workers with zero lock contention.</p>
</section>"""

pattern = r'<section class="chapter" id="gateway">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 20 applied.")
