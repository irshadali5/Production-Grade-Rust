import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "intro": """<section class="chapter" id="intro">
    <div class="chapter-label">Chapter 00</div>
    <h1>The Psychological Matrix of Rust</h1>

    <h2>The Compiler as a Co-Founder</h2>
    <p>When migrating from languages like Python or Node.js to Rust, developers often experience severe friction. In dynamic languages, you write code, run it, and it crashes at runtime. The developer is in charge of maintaining the mental model of the application's state. In Rust, the compiler forces you to prove, mathematically, that your mental model is flawless before it will emit a single byte of machine code.</p>
    <p>This paradigm shift requires a psychological rewiring. The Rust compiler (rustc) is not an adversary trying to slow you down; it is a hyper-vigilant co-founder that refuses to let you ship a memory leak or a data race to production. Once you internalize this, the "borrow checker" ceases to be an obstacle and becomes the ultimate safety net.</p>

    <h2>Zero-Cost Abstractions</h2>
    <p>A core tenet of Rust is the concept of <strong>Zero-Cost Abstractions</strong>. In languages like Java or C#, abstracting a complex concept (like an iterator or a state machine) usually incurs a runtime penalty (garbage collection overhead or virtual method dispatch). In Rust, thanks to monomorphization and LLVM optimization passes, high-level abstractions are compiled down to the exact same machine code you would have written by hand in C or Assembly.</p>
    <p>This means you can write beautiful, declarative, highly abstracted code without sacrificing a single nanosecond of performance. This book will teach you how to leverage these abstractions to build hyperscale, production-grade systems.</p>
</section>""",

    "workers": """<section class="chapter" id="workers">
    <div class="chapter-label">Chapter 12</div>
    <h1>Distributed Workers & Garnet Streams</h1>

    <h2>The Fallacy of Blocking the Main Thread</h2>
    <p>In a web API, the HTTP response must be returned to the client as fast as mathematically possible (typically under 50ms). If an HTTP handler needs to generate a massive PDF report, encode a video, or send 10,000 emails, performing this work directly inside the HTTP handler is a catastrophic architectural flaw. It blocks the Tokio worker thread, preventing it from processing new incoming requests, leading to immediate starvation and a cascading outage.</p>

    <h2>Decoupling via Garnet Streams</h2>
    <p>We solve this using <strong>Distributed Background Workers</strong>. When the HTTP handler receives a request to generate a PDF, it does not generate the PDF. It simply serializes the request parameters into a JSON payload and pushes it into a <strong>Garnet Stream</strong> (an append-only log, similar to Kafka, but operating at in-memory speeds via RESP).</p>
    <p>The HTTP handler then instantly returns a `202 Accepted` response to the user. The main API thread is now completely free.</p>

    <h2>Consumer Groups and Exactly-Once Semantics</h2>
    <p>On separate physical servers, we deploy a fleet of Rust Worker nodes. These nodes do not listen for HTTP traffic; they exclusively listen to the Garnet Stream using a <strong>Consumer Group</strong>.</p>
    <p>A Consumer Group guarantees that if 5 worker nodes are listening to the stream, a specific PDF generation task is only delivered to exactly one node. When a worker finishes generating the PDF, it sends an `XACK` (Acknowledge) command back to Garnet. If the worker node suffers a hardware failure and crashes before sending the `XACK`, Garnet's Pending Entries List (PEL) detects the timeout and safely reassigns the task to a healthy node, guaranteeing that no job is ever lost.</p>
</section>""",

    "caching": """<section class="chapter" id="caching">
    <div class="chapter-label">Chapter 17</div>
    <h1>Caching & Garnet High Availability (HA)</h1>

    <h2>The Singleflight Deduplication Pattern</h2>
    <p>Caching is not just about speed; it is about protecting the database from the <strong>Thundering Herd</strong> problem. Imagine a massive spike in traffic where 10,000 users simultaneously request the exact same expensive database query. If the cache is empty, all 10,000 requests will bypass the cache and hit Postgres at the exact same millisecond, instantly crashing it.</p>
    <p>We solve this in Rust using the <strong>Singleflight</strong> pattern. When the 10,000 requests arrive, the first request acquires a lock and begins the database query. The remaining 9,999 requests do not hit the database; they are mathematically suspended in memory, waiting for the first request to finish. When the first request finishes, it populates the cache and simultaneously broadcasts the result to the 9,999 waiting requests. One database query satisfies 10,000 users.</p>

    <h2>Garnet: The MIT-Licensed Cache Datastore</h2>
    <p>For distributed caching, we use <strong>Garnet</strong>, built by Microsoft Research. Garnet is an MIT-licensed, ultra-fast datastore that natively speaks the RESP (Redis Serialization Protocol). This allows us to use the standard `redis-rs` crate in Rust while avoiding restrictive RSALv2 licenses.</p>
    <p>Garnet operates in a highly concurrent, multi-threaded environment, unlike traditional single-threaded caches. It utilizes an epoch-based memory reclamation system and a highly optimized lock-free hash table to achieve throughputs of tens of millions of operations per second on a single node.</p>

    <h2>High Availability and Cluster Sharding</h2>
    <p>To ensure 99.999% uptime, Garnet is deployed in a High Availability (HA) cluster. Data is automatically replicated asynchronously to standby nodes. If the primary node suffers a catastrophic failure, a consensus algorithm (like Raft) detects the failure and automatically promotes a standby node to primary within milliseconds. Furthermore, for datasets that exceed the RAM of a single machine, Garnet supports Cluster Sharding, mathematically distributing keys across multiple physical servers using consistent hashing algorithms.</p>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to the final missed chapters (Intro, Workers, Caching).")
