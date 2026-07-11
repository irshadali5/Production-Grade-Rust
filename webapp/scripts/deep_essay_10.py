import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="concurrency">
    <div class="chapter-label">Chapter 10</div>
    <h1>Intensive Deep Dive: Hardware Concurrency, Memory Orderings & `loom`</h1>

    <h2>1. The Illusion of Shared Memory</h2>
    <p>In concurrent programming, junior developers assume that memory is a single, unified block of RAM. They believe that if Thread A writes <code>x = 5</code>, Thread B will instantly see <code>x = 5</code>. This mental model is catastrophically wrong and leads to fatal race conditions in hyperscale systems.</p>
    <p>Modern CPUs (Intel, AMD, ARM) are deeply distributed systems on a single silicon die. A 64-core EPYC processor has 64 independent L1 caches. When Thread A writes a value, it does not write to main memory; it writes to its local L1 cache. Unless a strict synchronization primitive forces a hardware-level broadcast (memory barrier), Thread B (running on a different core) will read stale data from its own L1 cache indefinitely. True concurrency requires understanding the physical propagation of electrons across the silicon ring bus.</p>

    <h2>2. Memory Orderings: Relaxed, Acquire, Release, SeqCst</h2>
    <p>Rust exposes this hardware reality through <code>std::sync::atomic::Ordering</code>. You cannot simply increment an atomic counter; you must explicitly dictate the compiler and CPU reordering permissions.</p>
    
    <h3>2.1 Ordering::Relaxed</h3>
    <p><code>Relaxed</code> provides zero synchronization. It only guarantees that the specific 8-byte variable is modified atomically without tearing. The CPU and the LLVM compiler are legally permitted to reorder instructions that surround the <code>Relaxed</code> operation. If you use <code>Relaxed</code> for a spinlock, the CPU will likely reorder your protected data access <em>before</em> the lock is acquired, destroying the state.</p>
    
    <h3>2.2 Acquire-Release Semantics</h3>
    <p>To build a lock-free queue or a Mutex, we rely on the <strong>Acquire-Release</strong> pair. When Thread A finishes writing data, it publishes a flag using <code>Ordering::Release</code>. This acts as a mathematical barrier: no memory writes that occurred <em>before</em> the Release operation can be reordered <em>after</em> it.</p>
    <p>When Thread B reads the flag using <code>Ordering::Acquire</code>, it establishes a <strong>Happened-Before Relationship</strong>. Any memory reads occurring <em>after</em> the Acquire operation are mathematically guaranteed to see the memory writes that occurred before the Release operation on Thread A. This hardware-level handshake synchronizes the local L1 caches across the silicon.</p>
    
    <h3>2.3 Ordering::SeqCst (Sequentially Consistent)</h3>
    <p><code>SeqCst</code> is the most restrictive ordering. It guarantees a single, global total order of operations across all threads. However, enforcing this global order requires the CPU to lock the entire memory bus, stalling all cores. Overusing <code>SeqCst</code> in a hyperscale system will completely destroy CPU throughput, reducing a 64-core server to the speed of a single core.</p>

    <h2>3. The MESI Protocol & False Sharing</h2>
    <p>Cache Coherence is maintained by the hardware using the MESI (Modified, Exclusive, Shared, Invalid) protocol. CPUs load memory in 64-byte chunks called <strong>Cache Lines</strong>. If Thread A modifies a variable, the CPU broadcasts an Invalidate signal for that entire 64-byte line to all other cores.</p>
    <p>This introduces <strong>False Sharing</strong>. If two completely independent atomic variables reside in the same 64-byte struct padding, Thread A and Thread B will continuously invalidate each other's L1 caches, causing the Cache Line to violently bounce across the physical ring bus. We eliminate this by using the <code>#[repr(align(64))]</code> attribute in Rust, forcing the compiler to space the atomics across different physical cache lines.</p>

    <h2>4. Permutation Testing via `loom`</h2>
    <p>Standard unit testing cannot verify lock-free code. A race condition might require a specific thread to be preempted by the OS scheduler at the exact nanosecond between two atomic reads. This specific interleaving might only occur once in 100 billion executions in production.</p>
    <p>We solve this using <strong>`loom`</strong>, Tokio's permutation testing engine. <code>loom</code> replaces the standard OS threads and atomics with deterministic mocks. During <code>cargo test</code>, <code>loom</code> systematically explores <em>every single mathematically possible sequence</em> of thread interleavings. If there is a one-in-a-trillion state machine vulnerability where Thread B reads before Thread A writes, <code>loom</code> will forcefully execute that exact path, crash the test, and output the physical trace. Code that passes <code>loom</code> is not just "tested"; it is mathematically proven to be thread-safe.</p>
</section>"""

pattern = r'<section class="chapter" id="concurrency">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 10 applied.")
