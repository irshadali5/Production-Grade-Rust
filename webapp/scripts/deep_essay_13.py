import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="deploy">
    <div class="chapter-label">Chapter 13</div>
    <h1>Intensive Deep Dive: Zero-Day Escapes & `musl` Static Linking</h1>

    <h2>1. The Myth of Docker Isolation</h2>
    <p>A staggering percentage of senior engineers incorrectly believe that a Docker container is a Virtual Machine. It is not. A Docker container does not have a hypervisor, it does not emulate hardware, and it does not have its own OS kernel. A container is simply a standard Linux process running directly on the host machine's kernel, surrounded by a thin illusion of isolation created by <code>cgroups</code> and <code>namespaces</code>.</p>
    <p>Because every container on a Node shares the exact same Linux kernel, a vulnerability in the kernel is fatal for the entire cluster. If a hacker exploits a Zero-Day vulnerability in the kernel's memory management subsystem from inside a container, they can shatter the <code>namespaces</code> illusion, escape the container, and achieve root access on the physical host machine, instantly compromising every other container on that Node.</p>

    <h2>2. The Attack Surface of Base Images</h2>
    <p>When you deploy a Rust application using a standard <code>ubuntu:latest</code> or <code>debian:bullseye</code> base image, you are packing a massive attack surface into your container. These images contain a full filesystem complete with package managers (<code>apt</code>), shells (<code>bash</code>), and network utilities (<code>curl</code>, <code>wget</code>).</p>
    <p>If an attacker finds a Remote Code Execution (RCE) vulnerability in your Rust application (perhaps by tricking your JSON parser into overflowing a buffer), they will immediately spawn a <code>bash</code> shell. From there, they will use your conveniently provided <code>curl</code> binary to download a crypto-miner or a lateral-movement toolkit from their command-and-control server, completely overtaking your infrastructure.</p>

    <h2>3. The `scratch` Image and Dynamic Linking (`glibc`)</h2>
    <p>To mathematically eliminate this attack surface, we must deploy our Rust binary into a <strong><code>scratch</code></strong> image. A <code>scratch</code> image is a Docker image that contains literally zero bytes. There is no filesystem, no <code>bash</code>, and no utilities.</p>
    <p>However, if you compile a standard Rust binary (target: <code>x86_64-unknown-linux-gnu</code>) and place it in a <code>scratch</code> image, it will crash instantly. This is due to <strong>Dynamic Linking</strong>. The Rust compiler does not include the standard C library (like the code for memory allocation or DNS resolution) in your binary. It leaves placeholders, expecting the host operating system to provide the GNU C Library (<code>glibc</code>) via shared object files (<code>.so</code>) at runtime. Because the <code>scratch</code> image is empty, the kernel cannot find <code>glibc</code>, and the execution aborts with a cryptic "no such file or directory" error.</p>

    <h2>4. Absolute Isolation via `musl`</h2>
    <p>We solve this by changing our compiler target to <code>x86_64-unknown-linux-musl</code>. <strong>musl</strong> is an incredibly lightweight, clean implementation of the C standard library designed specifically for static linking.</p>
    <p>When compiling for <code>musl</code>, the Rust compiler (and the <code>mold</code> linker) physically copy the actual machine code for all necessary C functions directly into your final ELF (Executable and Linkable Format) binary. The resulting binary is completely self-contained; it relies on absolutely zero external files. It communicates directly with the Linux kernel via raw system calls.</p>
    <p>When this statically linked binary is placed inside an empty <code>scratch</code> image, it boots flawlessly. You have created an impenetrable mathematical fortress. If an attacker achieves RCE, they are trapped in a vacuum. There is no shell to spawn, no tools to leverage, and no filesystem to navigate. You have reduced the OS-level attack surface to absolute zero.</p>
</section>"""

pattern = r'<section class="chapter" id="deploy">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 13 applied.")
