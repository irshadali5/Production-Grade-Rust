import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="async">
    <div class="chapter-label">Chapter 22</div>
    <h1>Intensive Deep Dive: The Physics of the `Future` Trait & Wakers</h1>

    <h2>1. The Illusion of Asynchronous Magic</h2>
    <p>Junior engineers often believe that the <code>async</code> keyword magically executes functions in parallel using hidden threads. This is a profound misunderstanding. An <code>async fn</code> in Rust does not execute immediately when called. It returns an inert <code>Future</code>. A <code>Future</code> is simply an enum representing a massive, compiler-generated State Machine.</p>
    <p>When you write the <code>.await</code> keyword, you are defining the exact boundaries of the state machine. The Rust compiler physically rewrites your function. All variables that must survive across the <code>.await</code> point are mathematically packed into the state machine's enum variants. This is why attempting to hold a non-Send type (like <code>std::rc::Rc</code> or a standard <code>MutexGuard</code>) across an <code>.await</code> boundary causes a fatal compilation error: if the state machine is moved to a different thread, the non-Send variable would corrupt the new thread's memory space.</p>

    <h2>2. Polling and the Tokio Executor</h2>
    <p>Because the <code>Future</code> is inert, it must be driven to completion by an Executor (Tokio). Tokio calls the <code>poll()</code> method on the Future. The Future executes its state machine until it hits an <code>.await</code> point (e.g., waiting for TCP data). At this point, the Future returns <code>Poll::Pending</code>.</p>
    <p>Crucially, <strong>Tokio does not block</strong>. When it receives <code>Poll::Pending</code>, it completely drops the Future, parks it in memory, and immediately uses the physical CPU core to execute a different user's HTTP request. This cooperative multitasking allows a single CPU core to juggle tens of thousands of concurrent connections.</p>

    <h2>3. The Waker and Epoll Hardware Interrupts</h2>
    <p>If the Future is parked, how does Tokio know when to poll it again? It would be a catastrophic waste of CPU cycles to continuously <code>poll()</code> the Future in a loop (busy-waiting). The entire asynchronous ecosystem revolves around the <code>Waker</code>.</p>
    <p>When Tokio calls <code>poll()</code>, it passes a <code>Context</code> object containing a <code>Waker</code>. If the Future is waiting on a TCP socket, the underlying Rust network library registers that specific socket with the Linux Kernel's <code>epoll</code> subsystem, and stores the <code>Waker</code> deep inside the kernel's event queue.</p>
    <p>Milliseconds later, a physical packet of light travels through a fiber-optic cable, strikes the server's Network Interface Card (NIC), and generates a hardware interrupt. The OS kernel reads the packet, identifies the TCP socket, and triggers the <code>epoll</code> event.</p>
    <p>The <code>epoll</code> event physically invokes <code>Waker::wake()</code>. The <code>wake()</code> function does exactly one thing: it pushes the parked Task back onto Tokio's Run Queue. The Tokio executor eventually pops the task and calls <code>poll()</code> again. The state machine resumes exactly where it left off, successfully reads the network buffer, and returns <code>Poll::Ready</code>. By perfectly aligning compiler state machines with hardware interrupts, Rust achieves absolute peak CPU utilization.</p>
</section>"""

pattern = r'<section class="chapter" id="async">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 22 applied.")
