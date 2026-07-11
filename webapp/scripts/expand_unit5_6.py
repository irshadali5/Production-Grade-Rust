import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "security": """<section class="chapter" id="security">
    <div class="chapter-label">Chapter 23</div>
    <h1>Security: RBAC, CSRF, & JWT Revocation</h1>

    <h2>The Stateless JWT Fallacy</h2>
    <p>A massive vulnerability in modern architectures is the blind trust of stateless JSON Web Tokens (JWTs). While mathematically verifying the RSA signature of a JWT guarantees the server issued it, a purely stateless token cannot be revoked. If a malicious actor steals a JWT with a 1-hour expiration, they possess god-level access to your API for an hour, even if the victim changes their password. We must bridge the gap between stateless scalability and stateful security.</p>

    <h2>The Revocation Blocklist</h2>
    <p>We implement a highly optimized <strong>JWT Revocation Blocklist</strong> using a distributed in-memory datastore like Garnet. When a user logs out or changes their password, we hash the JWT's `jti` (JWT ID) and store it in Garnet with a Time-To-Live (TTL) exactly matching the token's remaining expiration time. Every API request must query this blocklist. Because Garnet's lookup time is O(1) in the microsecond range, we achieve stateful, immediate revocation without degrading our API's throughput.</p>

    <h2>CSRF and Strict Site Tokens</h2>
    <p>Cross-Site Request Forgery (CSRF) occurs when a malicious website forces a user's browser to execute an authenticated API request against your domain using the user's implicit session cookies. We mitigate this using a multi-layered defense. First, all authentication cookies are marked `HttpOnly` (blocking JavaScript access) and `SameSite=Strict` (blocking cross-domain transmission). Second, we implement the <strong>Double Submit Cookie</strong> pattern. The server issues a cryptographically random CSRF token. The frontend must extract this token and submit it in a custom HTTP header (e.g., `X-CSRF-Token`). Since malicious domains cannot read the CSRF cookie due to the Same-Origin Policy (SOP), they cannot forge the required header, mathematically neutralizing the attack.</p>
</section>""",

    "wasm": """<section class="chapter" id="wasm">
    <div class="chapter-label">Chapter 24</div>
    <h1>WebAssembly: Linear Memory Internals</h1>

    <h2>The Flaw of JavaScript Engine Overhead</h2>
    <p>JavaScript engines (like V8) are marvels of engineering, utilizing Just-In-Time (JIT) compilation to run dynamic code at near-native speeds. However, for heavily computational tasks—like cryptographic hashing, video encoding, or complex DOM diffing—the JIT compiler is forced to make speculative assumptions about types. If those assumptions fail (a de-optimization), performance plummets. WebAssembly (WASM) circumvents this entirely by delivering a low-level, statically typed bytecode that the browser executes directly on the CPU without JIT warmup.</p>

    <h2>Linear Memory and the FFI Boundary</h2>
    <p>Compiling Rust to WASM using `wasm-bindgen` is trivial, but achieving high performance requires understanding WebAssembly's memory model. A WASM module does not have access to the DOM or the host OS. It operates inside a completely sandboxed, flat `ArrayBuffer` called <strong>Linear Memory</strong>.</p>
    <p>When you pass a massive array of data (like a 4K image) from JavaScript to Rust, the naive approach is to serialize it to JSON, pass it across the Foreign Function Interface (FFI) boundary, and deserialize it in Rust. This requires deep copies of memory, completely negating the performance benefits of WASM.</p>

    <h2>Zero-Copy Pointer Sharing</h2>
    <p>To operate at the expert level, we avoid serialization entirely. Instead, we allocate memory inside the Rust WASM module and pass the raw memory pointer (`*const u8`) back to JavaScript. JavaScript can then read and write directly to the WASM Linear Memory `ArrayBuffer` at that exact pointer index. By sharing memory instead of copying data, we achieve true zero-copy, native-speed execution within the browser.</p>
</section>""",

    "infrastructure": """<section class="chapter" id="infrastructure">
    <div class="chapter-label">Chapter 25</div>
    <h1>Infrastructure as Code (IaC): Terraform via Rust</h1>

    <h2>The YAML Fatigue Problem</h2>
    <p>Managing cloud infrastructure (AWS VPCs, RDS instances, ECS clusters) via the AWS Console is considered an anti-pattern. The industry standard is Infrastructure as Code (IaC) using Terraform (HCL) or AWS CloudFormation (YAML). However, these declarative languages lack the rigor of a true programming language. They lack strong typing, proper unit testing, and abstract interfaces, leading to massive, brittle configuration files.</p>

    <h2>Pulumi and Rust Bindings</h2>
    <p>We solve this using <strong>Pulumi</strong>, which allows us to define our AWS infrastructure using a general-purpose programming language. While Python and TypeScript are common, we utilize Rust bindings for maximum rigor. By defining our infrastructure in Rust, the compiler mathematically guarantees that we cannot pass an integer to a field that expects a VPC ID string.</p>
    <p>This allows us to write standard Rust unit tests for our infrastructure. We can test that every S3 bucket struct generated by our code has the `public_access_block` property set to `true`, preventing data leaks before the infrastructure is even provisioned.</p>
</section>""",

    "openapi": """<section class="chapter" id="openapi">
    <div class="chapter-label">Chapter 26</div>
    <h1>OpenAPI: Compile-Time Swagger Generation</h1>

    <h2>The Drift Between Code and Documentation</h2>
    <p>In standard REST architectures, the API documentation (like a Swagger JSON file or a Postman collection) is maintained manually. Over time, a developer will add a new field to a database model but forget to update the Swagger file. This results in "Documentation Drift," where the API contract given to the frontend team is fundamentally false, leading to production crashes.</p>

    <h2>Compile-Time Generation via `utoipa`</h2>
    <p>We eliminate Documentation Drift mathematically by generating our OpenAPI specification at compile-time directly from our Rust source code using the `utoipa` crate. By annotating our Axum handlers and Domain structs with macros, the Rust compiler inspects the actual, living code (including the exact types, enums, and required fields) and generates a flawless OpenAPI v3 JSON schema.</p>
    <p>If a developer changes a field in the Rust struct from an `Option<String>` to a required `String`, the OpenAPI documentation updates automatically. We then use this generated schema to automatically compile highly-typed frontend API clients in TypeScript, guaranteeing absolute synchronization between the backend and frontend.</p>
</section>""",

    "graphql": """<section class="chapter" id="graphql">
    <div class="chapter-label">Chapter 27</div>
    <h1>GraphQL: Over-fetching and the N+1 Problem</h1>

    <h2>The Limitations of REST</h2>
    <p>In a standard REST API, endpoints are rigid. If a mobile app needs a user's profile, their recent posts, and the comments on those posts, it might have to make 3 separate HTTP requests, resulting in massive network latency. Alternatively, the backend could create a massive `/api/user_full_payload` endpoint, but this results in "Over-fetching"—sending megabytes of data to a mobile client that only needed the user's avatar.</p>

    <h2>GraphQL and the N+1 Problem</h2>
    <p>GraphQL solves this by allowing the client to specify exactly the fields it wants in a single query. We implement a GraphQL server in Rust using the `async-graphql` crate. However, naive GraphQL implementations inevitably trigger the infamous <strong>N+1 Query Problem</strong>.</p>
    <p>If a user requests 50 posts, and the author of each post, a naive GraphQL resolver will execute 1 query to get the posts, and then 50 separate SQL queries to get the authors. This will instantly bring down your Postgres database.</p>

    <h2>The Dataloader Pattern</h2>
    <p>We solve the N+1 problem using the <strong>Dataloader</strong> pattern. The Dataloader intercepts the 50 individual requests for authors, batches them into a single mathematical queue, and executes a single SQL query (`SELECT * FROM authors WHERE id IN (...)`). It then maps the results back to the individual GraphQL resolvers. This reduces 51 database queries down to 2, allowing our GraphQL API to scale infinitely without crushing the database.</p>
</section>""",

    "kubernetes": """<section class="chapter" id="kubernetes">
    <div class="chapter-label">Chapter 28</div>
    <h1>Kubernetes: Autoscaling & Helm Charts</h1>

    <h2>The Orchestration Imperative</h2>
    <p>Running a single Docker container via `docker run` is sufficient for a side project, but a production system requires orchestration. If a container crashes, the orchestrator must restart it. If traffic spikes, the orchestrator must provision more instances. We deploy our Rust application to a <strong>Kubernetes (K8s)</strong> cluster using Helm.</p>

    <h2>Horizontal Pod Autoscaling (HPA)</h2>
    <p>We implement a <strong>Horizontal Pod Autoscaler (HPA)</strong> to dynamically scale our Rust API. The HPA continuously polls the Kubernetes Metrics Server. We configure it so that if the average CPU utilization across all Rust pods exceeds 75%, Kubernetes will automatically provision new pods. Because our Rust application is statically linked and hyper-optimized, a new pod can boot and begin accepting HTTP traffic in less than 50 milliseconds.</p>

    <h2>Liveness and Readiness Probes</h2>
    <p>Kubernetes must know the exact state of our application to route traffic safely. We expose two critical endpoints: `/healthz` (Liveness) and `/readyz` (Readiness). The Liveness probe simply returns a 200 OK. If the Rust application deadlocks and stops responding, the Liveness probe fails, and Kubernetes physically terminates and restarts the pod.</p>
    <p>The Readiness probe is more complex; it pings the Postgres database and the Garnet cache. If the database is unreachable, the pod is alive but not ready. Kubernetes will temporarily remove the pod from the Load Balancer rotation until the database connection is restored, ensuring users never see a 500 Error.</p>
</section>""",

    "benchmarking": """<section class="chapter" id="benchmarking">
    <div class="chapter-label">Chapter 29</div>
    <h1>Performance: Micro-Benchmarking & p99 Latency</h1>

    <h2>The Fallacy of the Mean</h2>
    <p>When measuring API performance, analyzing the "Average" (Mean) response time is a catastrophic mistake. If 99 requests take 1ms, and 1 request takes 10,000ms (due to a garbage collection pause or a database lock), the average response time is a healthy 100ms. The average hides the fact that 1% of your users experienced a severe, unacceptable outage. In hyperscale systems, we measure the <strong>p99 Tail Latency</strong>—the worst-case response time experienced by the 99th percentile of users.</p>

    <h2>Micro-benchmarking with `criterion`</h2>
    <p>We do not guess at performance optimizations. We mathematically prove them using the `criterion` crate. Criterion is a statistically rigorous micro-benchmarking framework. It performs thousands of warmup iterations to bring the CPU cache to a steady state, and then measures the exact instruction-level cycle counts of our Rust functions.</p>
    <p>By hooking `criterion` into our CI/CD pipeline, we can detect performance regressions automatically. If a developer accidentally adds an O(N^2) sorting algorithm that increases the p99 latency of our hashing function by 5%, `criterion` will fail the build, protecting our production throughput.</p>
</section>""",

    "ebpf": """<section class="chapter" id="ebpf">
    <div class="chapter-label">Chapter 30</div>
    <h1>eBPF: Zero-Overhead Kernel Profiling</h1>

    <h2>The Observer Effect in Profiling</h2>
    <p>Traditional performance profiling tools (like `perf` or `strace`) suffer from the Observer Effect. To measure an application, they must interrupt its execution, often injecting massive overhead (sometimes up to 50%). Running `strace` on a production database to debug latency will likely take the database offline.</p>

    <h2>The Power of eBPF</h2>
    <p>We utilize <strong>eBPF (Extended Berkeley Packet Filter)</strong> to achieve true zero-overhead observability. eBPF is a revolutionary technology that allows us to compile restricted C-like code into a specialized bytecode, verify it for safety (guaranteeing it cannot crash the OS), and inject it directly into the Linux Kernel.</p>
    <p>By attaching eBPF programs to kernel tracepoints (like `tcp_sendmsg` or disk I/O interrupts), we can monitor the exact latency of every single network packet and disk write generated by our Rust application at the kernel level. Because eBPF runs in kernel space, there are no expensive context switches to user space. We can generate highly detailed CPU Flamegraphs of a production server operating at 100,000 requests per second with less than 1% overhead.</p>
</section>""",

    "firecracker": """<section class="chapter" id="firecracker">
    <div class="chapter-label">Chapter 31</div>
    <h1>Firecracker: MicroVM Isolation</h1>

    <h2>The Container Escape Threat</h2>
    <p>Docker containers are not security boundaries; they are resource isolation boundaries (using Linux `cgroups` and `namespaces`). Because all containers on a node share the same underlying Linux Kernel, a zero-day kernel exploit (like Dirty COW) allows an attacker to "escape" the container and gain root access to the host machine. In multi-tenant environments (like AWS Lambda), this is a catastrophic threat.</p>

    <h2>Hardware Virtualization with Firecracker</h2>
    <p>To achieve true security, we must use Hardware Virtualization (Virtual Machines). However, traditional VMs (like QEMU) are bloated, taking minutes to boot and consuming gigabytes of RAM. We utilize <strong>Firecracker</strong>, a microVM manager written in Rust by AWS.</p>
    <p>Firecracker strips out all legacy hardware emulation (floppy drives, USB controllers) and implements only the bare minimum `virtio` devices required for network and disk access. The result is a highly secure microVM that boots a full Linux kernel in less than 125 milliseconds and consumes only 5MB of memory overhead. By deploying our Rust API inside Firecracker microVMs, we achieve the absolute security of hardware virtualization with the agility and density of Docker containers.</p>
</section>""",

    "io-uring": """<section class="chapter" id="io-uring">
    <div class="chapter-label">Chapter 32</div>
    <h1>io_uring: The Future of Asynchronous I/O</h1>

    <h2>The Syscall Bottleneck</h2>
    <p>The standard Tokio runtime (and Node.js) relies on `epoll` for asynchronous network I/O. However, for file system I/O, `epoll` is notoriously ineffective. When you read a file, your application must issue a system call (syscall), causing the CPU to context-switch from User Space to Kernel Space. At 1 million operations per second, the CPU spends the vast majority of its time simply switching contexts, rather than actually processing data.</p>

    <h2>Shared Memory Ring Buffers</h2>
    <p>We circumvent this bottleneck using <strong>io_uring</strong>, a revolutionary Linux kernel interface. Instead of issuing synchronous syscalls, `io_uring` establishes two shared-memory ring buffers between User Space (our Rust application) and Kernel Space.</p>
    <p>When our Rust app wants to read a file, it drops a Submission Queue Entry (SQE) into the shared memory ring. The Kernel, running asynchronously on a separate polling thread, reads the entry, performs the disk I/O, and drops a Completion Queue Entry (CQE) into the second ring. Because the application and the kernel are communicating entirely through shared memory, there are <strong>zero syscalls</strong> and zero context switches. This architecture allows Rust to saturate modern NVMe SSDs to their absolute physical limits, achieving millions of IOPS on a single core.</p>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to Unit 5 and Unit 6.")
