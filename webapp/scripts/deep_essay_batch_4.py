import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay_25 = """<section class="chapter" id="iac">
    <div class="chapter-label">Chapter 25</div>
    <h1>Intensive Deep Dive: Directed Acyclic Graphs in Terraform</h1>

    <h2>1. The Fallacy of Imperative Infrastructure</h2>
    <p>Managing cloud infrastructure via the AWS Console or using imperative shell scripts (e.g., <code>aws ec2 run-instances</code>) guarantees an eventual catastrophic state divergence. If a script fails halfway through, the infrastructure is left in a corrupted, intermediate state. We must treat infrastructure as a declarative state machine using Infrastructure as Code (IaC) tools like Terraform.</p>

    <h2>2. The Terraform State Lock and AST Execution</h2>
    <p>When you run <code>terraform apply</code>, Terraform parses your HCL (HashiCorp Configuration Language) into an Abstract Syntax Tree (AST). It then mathematically compares this desired state AST against the <strong>State File</strong> (a JSON representation of reality). It constructs a Directed Acyclic Graph (DAG) of the differences to determine the precise order of execution (e.g., creating a VPC before creating the EC2 instance inside it).</p>
    <p>Crucially, before Terraform modifies reality, it acquires a Distributed State Lock (typically in DynamoDB). This mathematical lock guarantees that if two DevOps engineers run <code>terraform apply</code> simultaneously, they will not corrupt the infrastructure by creating duplicate resources, ensuring perfect concurrency control at the cloud level.</p>
</section>"""

essay_26 = """<section class="chapter" id="openapi">
    <div class="chapter-label">Chapter 26</div>
    <h1>Intensive Deep Dive: Compile-Time OpenAPI Generation</h1>

    <h2>1. The Desync Between Code and Documentation</h2>
    <p>If an API developer manually writes Swagger documentation, the documentation will inevitably desync from the actual Rust code, leading to broken client applications. We must mathematically bind the documentation to the Rust Abstract Syntax Tree (AST).</p>

    <h2>2. AST Macros and Type Reflection</h2>
    <p>Using the <code>utoipa</code> crate, we decorate our Rust structs and Axum handlers with procedural macros. During compilation, these macros intercept the AST. If a struct field is defined as an <code>Option&lt;String&gt;</code>, the macro uses Rust's type system to mathematically deduce that the OpenAPI JSON Schema field must be <code>type: "string", nullable: true</code>.</p>
    <p>If a developer changes the struct field to <code>i32</code> but forgets to update the documentation, the compiler automatically updates the generated JSON Schema. This creates a zero-maintenance, mathematically perfect API contract that clients (like React or iOS apps) can use to autogenerate type-safe SDKs.</p>
</section>"""

essay_27 = """<section class="chapter" id="graphql">
    <div class="chapter-label">Chapter 27</div>
    <h1>Intensive Deep Dive: The N+1 Problem & Dataloaders</h1>

    <h2>1. The Graph Resolution Algorithm</h2>
    <p>GraphQL is not just a query language; it is an AST execution engine. When a client requests <code>query { users { posts { comments } } }</code>, the server parses the string into an AST. The GraphQL executor traverses this tree, invoking Resolver functions at each node.</p>

    <h2>2. The Catastrophic N+1 Query Problem</h2>
    <p>This tree traversal introduces the deadliest database anti-pattern: the N+1 problem. If the <code>users</code> query returns 100 users, the executor will invoke the <code>posts</code> resolver 100 separate times. The <code>posts</code> resolver will invoke the <code>comments</code> resolver thousands of times. A single HTTP request will trigger 10,000 separate SQL queries, instantly crashing the Postgres instance.</p>

    <h2>3. Batching via the Dataloader Pattern</h2>
    <p>We eliminate this mathematically using the <strong>Dataloader Pattern</strong>. A Dataloader is an asynchronous batching queue. When the <code>posts</code> resolver needs a user's posts, it does not query the database. It pushes the <code>user_id</code> into the Dataloader's queue and returns a <code>Future</code>.</p>
    <p>The Tokio executor suspends all 100 resolvers. At the end of the tick, the Dataloader looks at its queue, deduplicates the IDs, and executes a <strong>single</strong> SQL query: <code>SELECT * FROM posts WHERE user_id IN (1, 2, ..., 100)</code>. It then distributes the results back to the suspended Futures. By utilizing Tokio's event loop, we mathematically compress 10,000 SQL queries into exactly 3 queries, achieving O(1) database performance.</p>
</section>"""

essay_28 = """<section class="chapter" id="k8s">
    <div class="chapter-label">Chapter 28</div>
    <h1>Intensive Deep Dive: Control Plane Physics & cgroups</h1>

    <h2>1. Linux Kernel Namespaces</h2>
    <p>Kubernetes (K8s) is the pinnacle of distributed orchestration. However, to understand K8s, you must understand the Linux Kernel. A K8s Pod is not a VM. It is an illusion created by <strong>Linux Namespaces</strong> and <strong>cgroups</strong>. Namespaces partition kernel resources. When a Rust binary runs inside a Pod, the <code>PID</code> namespace tricks the binary into thinking it is Process ID 1. The <code>Network</code> namespace gives it a virtual ethernet device (veth) with its own IP address.</p>
    
    <h2>2. The Kubelet and cgroup v2</h2>
    <p>To prevent a single Pod from consuming all physical RAM and triggering an OOM panic, the Kubelet interfaces with the Linux kernel's <strong>cgroups v2</strong> API. It sets a hard mathematical limit on the memory controller for that specific Process Tree. If the Rust binary allocates 1 byte over the limit, the kernel's OOM Killer instantly assassinates the process.</p>

    <h2>3. The Control Plane Reconciliation Loop</h2>
    <p>The true genius of K8s is the Control Plane (the API Server and Controller Manager). It operates as a continuous state machine. You provide a declarative YAML file (the Desired State: "I want 5 replicas"). The Controller Manager constantly polls the <code>etcd</code> database to view the Actual State (e.g., "There are currently 4 replicas because a node burned down").</p>
    <p>The Controller calculates the delta, and executes a <strong>Reconciliation Loop</strong>. It mathematically forces the Actual State to match the Desired State by instructing the scheduler to spin up a new Pod on a healthy node, achieving absolute distributed self-healing.</p>
</section>"""

essay_29 = """<section class="chapter" id="benchmarking">
    <div class="chapter-label">Chapter 29</div>
    <h1>Intensive Deep Dive: Flamegraphs & p99 Tail Latency</h1>

    <h2>1. The Deception of Average Latency</h2>
    <p>Junior engineers measure performance using average (mean) latency. This is statistically useless. In a hyperscale system, if the average latency is 10ms, but 1% of requests take 5,000ms (due to garbage collection or DB locks), that 1% represents thousands of angry users per minute. True engineering requires focusing entirely on the <strong>99th Percentile (p99) Tail Latency</strong>.</p>

    <h2>2. Hardware Profiling via `perf` and Flamegraphs</h2>
    <p>To optimize tail latency in Rust, we cannot rely on logging. We must profile the physical CPU. We use the Linux <code>perf</code> tool. <code>perf</code> taps into the hardware performance counters of the CPU. Every 1 millisecond, it interrupts the CPU and records the exact memory address of the instruction pointer (the stack trace).</p>
    <p>By collecting millions of these stack traces, we use Brendan Gregg's scripts to generate a <strong>Flamegraph</strong>. The Flamegraph visually stacks the function calls. The wider a function block is on the graph, the more CPU cycles it physically consumed. This mathematically proves exactly where the CPU is stalling, allowing us to pinpoint unnecessary memory allocations or lock contention down to the exact line of Rust code.</p>
</section>"""

essay_30 = """<section class="chapter" id="ebpf">
    <div class="chapter-label">Chapter 30</div>
    <h1>Intensive Deep Dive: eBPF & Kernel Hooking</h1>

    <h2>1. The Overhead of Kernel Space Transitions</h2>
    <p>When a Rust application reads a network packet, the data arrives in the Linux Kernel Space. To access it, the Rust application must issue a <code>read()</code> system call, forcing a CPU Context Switch from User Space to Kernel Space, copying the memory across the boundary, and switching back. At 10 million packets per second, this context switching overhead completely maxes out the CPU.</p>

    <h2>2. The eBPF Virtual Machine</h2>
    <p>We bypass this overhead using <strong>eBPF (Extended Berkeley Packet Filter)</strong>. eBPF is a highly restricted, sandboxed Virtual Machine that physically resides <em>inside</em> the Linux Kernel. We write a small Rust program (using the <code>aya</code> crate), compile it to eBPF bytecode, and inject it directly into the kernel.</p>
    <p>When a network packet hits the physical NIC, the kernel instantly executes our eBPF program at the XDP (eXpress Data Path) layer, before the packet even reaches the TCP/IP stack. The kernel's JIT compiler translates the eBPF bytecode directly into native machine code. Our program can inspect the packet, drop malicious DDoS traffic, or update telemetry metrics natively in Kernel Space, achieving wire-speed performance with zero User Space context switches.</p>
</section>"""

essay_31 = """<section class="chapter" id="firecracker">
    <div class="chapter-label">Chapter 31</div>
    <h1>Intensive Deep Dive: Firecracker MicroVMs & KVM</h1>

    <h2>1. The Multi-Tenant Vulnerability of Containers</h2>
    <p>If you run a Serverless platform (like AWS Lambda), you must execute untrusted code from thousands of different customers on the same physical server. Standard Docker containers are completely insufficient. Because containers share the same Linux Kernel, a zero-day exploit in the kernel allows a malicious user in Container A to read the memory of Container B, stealing SSL keys.</p>

    <h2>2. Hardware Virtualization (KVM)</h2>
    <p>To achieve physical isolation, we must use Virtual Machines via <strong>KVM (Kernel-based Virtual Machine)</strong>. KVM utilizes hardware virtualization extensions (Intel VT-x or AMD-V). The CPU physically isolates the memory and execution context of the Guest OS from the Host OS at the silicon level. However, booting a standard Linux VM takes several minutes and consumes hundreds of megabytes of RAM.</p>

    <h2>3. Firecracker MicroVMs</h2>
    <p>We solve this using <strong>Firecracker</strong>, a hypervisor written entirely in Rust by AWS. Firecracker strips out 99% of the legacy hardware emulation (no USB controllers, no floppy drives, no VGA drivers). It provides only a virtio-net network interface and a virtio-blk block device.</p>
    <p>Because it is so heavily stripped down, Firecracker can boot a complete Linux microVM using KVM in less than 125 milliseconds, consuming less than 5 MB of memory overhead. This allows us to pack 5,000 completely hardware-isolated Serverless functions onto a single physical server, achieving the security of VMs with the agility of containers.</p>
</section>"""

essay_32 = """<section class="chapter" id="io_uring">
    <div class="chapter-label">Chapter 32</div>
    <h1>Intensive Deep Dive: `io_uring` & Zero-Copy Ring Buffers</h1>

    <h2>1. The Bottleneck of `epoll`</h2>
    <p>Throughout this book, we have praised `epoll` as the foundation of asynchronous I/O (Tokio). However, `epoll` has a fundamental flaw: it only tells you that a socket is <em>ready</em> to be read. The Rust application must still issue a `read()` system call to physically pull the data from the kernel, triggering an expensive CPU context switch.</p>

    <h2>2. Asynchronous Ring Buffers (`io_uring`)</h2>
    <p>To achieve the absolute bleeding-edge of Linux performance, we replace `epoll` with <strong>`io_uring`</strong>. `io_uring` establishes two lock-free ring buffers (the Submission Queue and the Completion Queue) directly in memory that is shared between User Space and Kernel Space via `mmap`.</p>
    <p>When our Rust application needs to read a socket, it does not execute a system call. It simply drops a read request into the Submission Queue. A background kernel thread polls this queue, performs the read, and drops the result into the Completion Queue. The Rust application polls the Completion Queue to get the data. We have achieved true, 100% asynchronous, zero-copy, system-call-free I/O, allowing our server to process tens of millions of HTTP requests per second on a single physical machine. You have reached the absolute peak of software engineering.</p>
</section>"""

essay_00 = """<section class="chapter" id="intro">
    <div class="chapter-label">Chapter 00</div>
    <h1>Intensive Deep Dive: The Philosophy of Systems Engineering</h1>
    <p>Welcome to Production-Grade Rust. This is not a beginner's tutorial. This is an exhaustive, mathematically rigorous deconstruction of hyperscale systems engineering.</p>
    <p>To survive at scale, you must understand the physical constraints of the silicon you operate on. You must understand CPU Cache Lines, MESI protocols, Context Switches, eBPF Kernel Hooks, and the statistical mathematics of Tail Latencies and Exponential Backoff.</p>
    <p>In the following 32 chapters, we will construct a system that can sustain 10 million concurrent connections. We will abandon abstractions and manipulate memory at the architectural level. Prepare for the most intensive technical deep dive in the Rust ecosystem.</p>
</section>"""


content = re.sub(r'<section class="chapter" id="iac">.*?</section>', essay_25, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="openapi">.*?</section>', essay_26, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="graphql">.*?</section>', essay_27, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="k8s">.*?</section>', essay_28, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="benchmarking">.*?</section>', essay_29, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="ebpf">.*?</section>', essay_30, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="firecracker">.*?</section>', essay_31, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="io_uring">.*?</section>', essay_32, content, flags=re.DOTALL)
content = re.sub(r'<section class="chapter" id="intro">.*?</section>', essay_00, content, flags=re.DOTALL)


with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapters 25-32 and 00.")
