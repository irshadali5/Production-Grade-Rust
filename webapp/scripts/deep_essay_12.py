import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="workers">
    <div class="chapter-label">Chapter 12</div>
    <h1>Intensive Deep Dive: The Raft Consensus Algorithm & Exactly-Once Semantics</h1>

    <h2>1. The Two Generals' Problem and TCP Unreliability</h2>
    <p>When orchestrating a fleet of distributed background workers, you must confront the most devastating mathematical reality of distributed systems: <strong>The Two Generals' Problem</strong>. No network is reliable. TCP/IP can drop packets, routers can reboot, and BGP routes can blackhole traffic.</p>
    <p>If Worker A attempts to charge a credit card and the TCP connection to the Stripe API hangs, Worker A does not know if the payload reached Stripe and the ACK was lost, or if the payload never reached Stripe at all. If it retries, it might double-charge the user. If it crashes, the charge is lost forever. Achieving perfect state coordination over an unreliable network is mathematically impossible.</p>

    <h2>2. Distributed Consensus via the Raft Protocol</h2>
    <p>To coordinate the distribution of jobs, we use Garnet as our message broker. But what if the primary Garnet node suffers a kernel panic? The cluster must immediately promote a replica to primary. If a network partition occurs (a split-brain), two nodes might both claim to be the primary, silently accepting conflicting job updates and permanently corrupting the system state.</p>
    <p>We solve this using the <strong>Raft Consensus Algorithm</strong>. Raft mathematically prevents split-brains by enforcing a strict <strong>Quorum</strong>. In a 5-node cluster, a node can only be elected Leader if it receives cryptographic votes from at least 3 nodes (the majority). If a network partition cuts the cluster into a group of 2 and a group of 3, the group of 2 can never elect a leader, preventing data corruption. The group of 3 will seamlessly continue processing, ensuring high availability with absolute mathematical consistency.</p>

    <h2>3. Exactly-Once Delivery and the Pending Entries List (PEL)</h2>
    <p>A standard message queue provides "At-Most-Once" delivery (fire and forget) or "At-Least-Once" delivery (retry until acknowledged). In a financial system, neither is acceptable. We require the illusion of <strong>Exactly-Once Delivery</strong>.</p>
    <p>We achieve this using Garnet Streams and the <strong>Pending Entries List (PEL)</strong>. When Worker A pulls a job from the stream, the job is not deleted. It is atomically moved into Worker A's PEL. The job remains trapped in this list until Worker A successfully processes it and sends an explicit <code>XACK</code> (Acknowledge) command.</p>
    <p>If Worker A is OOM-Killed by Kubernetes mid-execution, the <code>XACK</code> is never sent. A specialized Rust Supervisor Task continuously scans the cluster using the <code>XPENDING</code> command. If it finds a job that has been sitting in a PEL for more than 60 seconds, it uses the <code>XCLAIM</code> command to forcefully rip ownership of the job away from the dead worker, reassigning it to a healthy Worker B.</p>

    <h2>4. Idempotency Keys and Database Locking</h2>
    <p>What if Worker A wasn't dead? What if it was merely paused by a massive 50-second Garbage Collection spike, and the Supervisor assigned the job to Worker B? Now, Worker A wakes up, and both workers attempt to charge the credit card simultaneously.</p>
    <p>We defeat this race condition using <strong>Idempotency Keys</strong>. Every job payload includes a cryptographic UUID. Before charging the card, the Rust worker executes an atomic SQL query: <code>INSERT INTO processed_jobs (id) VALUES ($1)</code>. Because the <code>id</code> column has a Unique Constraint, Postgres utilizes its internal B-Tree locks to guarantee that only one <code>INSERT</code> can possibly succeed. The slower worker will receive a Unique Constraint Violation from Postgres, mathematically preventing the double-charge, and perfectly fulfilling our Exactly-Once guarantee.</p>
</section>"""

pattern = r'<section class="chapter" id="workers">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 12 applied.")
