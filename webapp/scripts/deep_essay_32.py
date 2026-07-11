import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="io_uring">
    <div class="chapter-label">Chapter 32</div>
    <h1>Intensive Deep Dive: `io_uring` & Zero-Copy Kernel Bypassing</h1>

    <h2>1. The Overhead of `epoll` and System Calls</h2>
    <p>Throughout this book, we have explored how Tokio uses the `epoll` kernel subsystem to efficiently manage tens of thousands of concurrent connections. However, at the absolute limits of hardware capability (processing 10+ million HTTP requests per second), `epoll` itself becomes the bottleneck.</p>
    <p>The flaw is that `epoll` is a blocking system call that merely tells the Rust application that a socket is <em>ready</em> to be read. Once notified, the Rust application must issue a subsequent `read()` system call to physically pull the data from the kernel's network buffer into the Rust user-space memory buffer. Every single system call requires the CPU to execute an expensive Context Switch, saving all user-space registers, switching the CPU privilege ring to Kernel Mode, executing the kernel code, and context switching back. At 10 million operations per second, this context switching overhead completely maxes out the CPU.</p>

    <h2>2. True Asynchronous I/O via `io_uring`</h2>
    <p>We eliminate this bottleneck entirely using <strong>`io_uring`</strong>. This is not just a faster `epoll`; it is a complete architectural paradigm shift in how User Space communicates with Kernel Space.</p>
    <p>`io_uring` establishes two highly optimized, lock-free circular Ring Buffers (the Submission Queue and the Completion Queue). Crucially, these buffers are instantiated in memory that is shared directly between User Space and Kernel Space via `mmap`. This means both the Rust application and the Linux Kernel can read and write to these buffers simultaneously without triggering a context switch.</p>

    <h2>3. Zero-Copy Kernel Bypassing</h2>
    <p>When our Rust application needs to read from a TCP socket, it does not execute a system call. It simply formats a Read Request packet and drops it into the Submission Queue. Because the memory is shared, the Linux Kernel instantly sees the request.</p>
    <p>A background kernel thread polls the Submission Queue, performs the network read, and writes the resulting byte array directly into the Completion Queue. The Rust application polls the Completion Queue to retrieve the data. No system calls were executed. No context switches occurred.</p>
    <p>By relying entirely on shared memory ring buffers, `io_uring` achieves 100% true, asynchronous, system-call-free I/O. It allows a single Rust monolith to saturate 100-Gigabit NICs, processing tens of millions of concurrent operations per second on a single physical machine. You have reached the absolute apex of hyperscale software engineering.</p>
</section>"""

pattern = r'<section class="chapter" id="io_uring">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 32 applied.")
