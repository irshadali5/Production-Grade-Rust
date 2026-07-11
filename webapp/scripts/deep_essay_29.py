import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="benchmarking">
    <div class="chapter-label">Chapter 29</div>
    <h1>Intensive Deep Dive: Hardware Profiling & Flamegraphs</h1>

    <h2>1. The Deception of Mean Latency</h2>
    <p>Junior engineers measure performance using average (mean) latency. In a hyperscale system processing 10,000 requests per second, the average is a mathematically useless metric. If the average latency is 10ms, but 1% of your requests take 5,000ms (due to a lock contention or a massive memory allocation), that 1% represents 100 furious users every single second.</p>
    <p>True engineering mastery requires focusing exclusively on the <strong>99th Percentile (p99) Tail Latency</strong>. If your p99 latency is 12ms, it means that 99% of all users experience a response time of 12ms or better. Optimizing the p99 guarantees a perfectly uniform experience across the entire user base.</p>

    <h2>2. Hardware Profiling via `perf`</h2>
    <p>To optimize tail latency in Rust, standard logging is completely inadequate. Logging requires modifying the code and recompiling, and it introduces its own latency observer effect. To truly understand performance, we must profile the physical CPU silicon.</p>
    <p>We use the Linux <code>perf</code> tool. <code>perf</code> does not modify your Rust code. It taps directly into the hardware performance counters of the CPU. We configure <code>perf</code> to execute a hardware interrupt every 1 millisecond. When the interrupt fires, the CPU halts, and <code>perf</code> records the exact memory address of the Instruction Pointer (the current physical stack trace of the Rust binary).</p>

    <h2>3. Flamegraph Visualization</h2>
    <p>By running the server under extreme load and collecting millions of these stack traces, we can statistically reconstruct exactly what the CPU was doing. We use Brendan Gregg's scripts to compile this data into a <strong>Flamegraph</strong>.</p>
    <p>A Flamegraph visually stacks the function calls. The X-axis represents CPU time. The wider a function block is on the graph, the more CPU cycles it physically consumed. By analyzing the Flamegraph, we can mathematically prove exactly where the CPU is stalling. We might discover that a seemingly harmless <code>serde_json::to_string</code> call is consuming 40% of our CPU cycles due to unnecessary string allocations. The Flamegraph allows us to pinpoint the exact line of Rust code causing the p99 spike, enabling surgical, nanosecond-level optimizations.</p>
</section>"""

pattern = r'<section class="chapter" id="benchmarking">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 29 applied.")
