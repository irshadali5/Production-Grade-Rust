import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="ebpf">
    <div class="chapter-label">Chapter 30</div>
    <h1>Intensive Deep Dive: eBPF & XDP Kernel Hooking</h1>

    <h2>1. The Context Switch Bottleneck</h2>
    <p>When an attacker launches a massive DDoS attack against your server, a naive architecture attempts to block the IPs using application logic. However, for a network packet to reach your Rust Axum application, the Linux kernel must first receive the packet on the NIC, parse the TCP/IP headers, allocate a socket buffer (<code>sk_buff</code>), and copy the data from Kernel Space into User Space.</p>
    <p>This Kernel-to-User Space boundary requires an expensive CPU Context Switch. If you receive 10 million malicious packets per second, the context switching overhead alone will completely saturate all your CPU cores, causing the server to crash before your Rust code even has a chance to inspect the IP addresses.</p>

    <h2>2. The eBPF Virtual Machine</h2>
    <p>To operate at hyperscale, we must push our code down into the OS kernel. We achieve this using <strong>eBPF (Extended Berkeley Packet Filter)</strong>. eBPF is a highly restricted, mathematically proven Virtual Machine that resides physically <em>inside</em> the Linux Kernel.</p>
    <p>Using the <code>aya</code> crate, we write a small Rust program and compile it to eBPF bytecode. When we inject this bytecode into the kernel, the kernel runs a strict Verifier to mathematically guarantee that our code contains no infinite loops or invalid memory accesses (ensuring our code cannot kernel-panic the OS). Once verified, the kernel's JIT compiler translates our eBPF bytecode directly into native machine code.</p>

    <h2>3. XDP (eXpress Data Path) Hooking</h2>
    <p>We hook our compiled eBPF program directly into the <strong>XDP (eXpress Data Path)</strong> layer. XDP is the absolute lowest level of the Linux network stack, executing immediately after the physical NIC driver receives an electron pulse.</p>
    <p>When a malicious packet arrives, the kernel instantly executes our eBPF program in Kernel Space, completely bypassing the TCP/IP stack and socket buffers. Our eBPF program parses the raw IP headers, identifies the malicious IP, and issues the <code>XDP_DROP</code> command.</p>
    <p>The kernel drops the packet instantly, without a single byte ever crossing the User Space boundary. By executing our Rust logic as a JIT-compiled kernel extension, we can easily drop 20 million DDoS packets per second using only 2% of the CPU's capacity.</p>
</section>"""

pattern = r'<section class="chapter" id="ebpf">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 30 applied.")
