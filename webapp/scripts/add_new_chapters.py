import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

# 1. Add Sidebar Links
sidebar_links = """
    <a href="#ebpf" class="nav-item"><span class="chapter-num">30</span>eBPF Profiling</a>
    <a href="#firecracker" class="nav-item"><span class="chapter-num">31</span>Firecracker VMs</a>
    <a href="#io-uring" class="nav-item"><span class="chapter-num">32</span>io_uring</a>
"""
# Insert before </div>\n</aside>
content = content.replace('</div>\n</aside>', sidebar_links + '</div>\n</aside>')

# 2. Add the 3 new Chapters
new_chapters = """
  <!-- CHAPTER 30: eBPF -->
  <section class="chapter" id="ebpf">
    <div class="chapter-label">Chapter 30</div>
    <h1>Expert Architecture: eBPF Profiling & Flamegraphs</h1>
    <p>When your production Rust service experiences sporadic latency spikes, guessing is not an option. Traditional profilers add unacceptable overhead. We must utilize <strong>eBPF (Extended Berkeley Packet Filter)</strong> to trace our application directly from the Linux kernel in real-time with near-zero overhead.</p>

    <h2>Generating Flamegraphs</h2>
    <p>We use <code>cargo-flamegraph</code>, which relies on the Linux <code>perf</code> subsystem, to visualize exactly where CPU cycles are spent.</p>

    <div class="code-block">
      <div class="code-header">
        <span class="code-filename">terminal</span>
        <span class="code-lang">bash</span>
      </div>
      <pre><span class="cmt"># Run the application under perf and generate a flamegraph.svg</span>
sudo cargo flamegraph --root --bin zero2prod</pre>
    </div>

    <h2>DTrace Probes (USDT)</h2>
    <p>For even deeper introspection without relying solely on CPU sampling, we can embed <strong>User-Level Statically Defined Tracing (USDT)</strong> probes directly into our Rust code using the <code>probe</code> macro. We can then attach eBPF scripts via <code>bpftrace</code> to fire exactly when these probes are hit.</p>
  </section>

  <!-- CHAPTER 31: FIRECRACKER -->
  <section class="chapter" id="firecracker">
    <div class="chapter-label">Chapter 31</div>
    <h1>Serverless: Firecracker MicroVMs</h1>
    <p>Docker containers share the host kernel. For true multi-tenant isolation in a serverless environment, we need Virtual Machines. However, traditional VMs take seconds to boot. AWS <strong>Firecracker</strong> allows us to boot a secure MicroVM in less than 5 milliseconds.</p>

    <h2>Building Static Binaries for Rootfs</h2>
    <p>To run in a MicroVM, we strip away Debian or Alpine and provide only our raw Rust binary mapped as the <code>init</code> process on a bare `ext4` filesystem.</p>

    <div class="code-block">
      <div class="code-header">
        <span class="code-filename">terminal</span>
        <span class="code-lang">bash</span>
      </div>
      <pre><span class="cmt"># Cross-compile a fully statically linked binary using musl</span>
cargo build --target x86_64-unknown-linux-musl --release

<span class="cmt"># Create a raw ext4 image</span>
dd if=/dev/zero of=rootfs.ext4 bs=1M count=50
mkfs.ext4 rootfs.ext4

<span class="cmt"># Mount and inject our static Rust binary as the /sbin/init process</span>
mkdir -p /tmp/my-rootfs
sudo mount rootfs.ext4 /tmp/my-rootfs
sudo cp target/x86_64-unknown-linux-musl/release/zero2prod /tmp/my-rootfs/sbin/init
sudo umount /tmp/my-rootfs</pre>
    </div>
    <p>We then launch Firecracker via its socket API, passing the <code>vmlinux</code> kernel and our <code>rootfs.ext4</code>. The VM boots instantly, executing our Rust API directly.</p>
  </section>

  <!-- CHAPTER 32: IO_URING -->
  <section class="chapter" id="io-uring">
    <div class="chapter-label">Chapter 32</div>
    <h1>High-Performance I/O with io_uring</h1>
    <p>Tokio relies on the Linux <code>epoll</code> subsystem for asynchronous networking. However, <code>epoll</code> requires multiple context switches between user-space and kernel-space per socket event. To bypass this, we use <strong>io_uring</strong>, a revolutionary kernel feature that provides true asynchronous I/O via shared memory ring buffers.</p>

    <h2>tokio-uring Implementation</h2>
    <p>Using <code>tokio-uring</code>, we can queue network read/write operations on the Submission Queue (SQ) and reap them on the Completion Queue (CQ) without a single syscall.</p>

    <div class="code-block">
      <div class="code-header">
        <span class="code-filename">src/uring.rs</span>
        <span class="code-lang">rust</span>
      </div>
      <pre><span class="kw">use</span> <span class="type">tokio_uring</span>::<span class="type">net</span>::<span class="type">TcpListener</span>;

<span class="kw">fn</span> <span class="fn">main</span>() {
    <span class="cmt">// Start the tokio-uring runtime instead of the standard tokio runtime</span>
    <span class="type">tokio_uring</span>::<span class="fn">start</span>(<span class="kw">async</span> {
        <span class="kw">let</span> listener = <span class="type">TcpListener</span>::<span class="fn">bind</span>(<span class="str">"0.0.0.0:8000"</span>.parse().unwrap()).unwrap();
        <span class="kw">loop</span> {
            <span class="kw">let</span> (stream, _) = listener.<span class="fn">accept</span>().<span class="kw">await</span>.unwrap();
            
            <span class="type">tokio_uring</span>::<span class="fn">spawn</span>(<span class="kw">async move</span> {
                <span class="kw">let</span> <span class="kw">mut</span> buf = <span class="type">vec!</span>[<span class="num">0</span>; <span class="num">1024</span>];
                <span class="cmt">// Zero-copy read directly into the buffer via io_uring</span>
                <span class="kw">let</span> (res, buf) = stream.<span class="fn">read</span>(buf).<span class="kw">await</span>;
                <span class="kw">if</span> res.is_ok() {
                    <span class="cmt">// Echo back</span>
                    <span class="kw">let</span> _ = stream.<span class="fn">write</span>(buf).<span class="kw">await</span>;
                }
            });
        }
    });
}</pre>
    </div>
  </section>
"""

# Insert right before </main>
content = content.replace('</main>', new_chapters + '\n</main>')

with open(filepath, 'w') as f:
    f.write(content)

print("Added 3 new expert chapters successfully.")
