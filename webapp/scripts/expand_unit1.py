import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "setup": """<section class="chapter" id="setup">
    <div class="chapter-label">Chapter 01</div>
    <h1>Expert Toolchain: Nix Flakes, LLVM, & mold</h1>
    
    <h2>The Illusion of Global Toolchains</h2>
    <p>In the vast majority of engineering organizations, local development environments are managed via global toolchains. A developer might run <code>curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh</code>, installing the latest stable Rust compiler. Another developer joining the team three months later runs the exact same command and receives a completely different minor version of the compiler. When a production bug manifests only on the newer compiler due to an obscure LLVM optimization pass, the entire engineering team loses days attempting to reproduce a bug that simply does not exist on their machine. This is the "works on my machine" anti-pattern.</p>
    <p>For production-grade systems, environmental mutation is unacceptable. A build must be a pure, deterministic function mapping source code to a binary executable. If the inputs (source code and compiler version) are identical, the output must be mathematically identical. To achieve this, we completely abandon global toolchains in favor of <strong>Nix Flakes</strong>.</p>
    
    <h2>Nix Flakes: Deterministic Development</h2>
    <p>Nix is a purely functional package manager. It calculates cryptographic hashes of every dependency in the entire dependency tree—down to the specific version of <code>glibc</code> and the exact C compiler used to compile the Rust compiler itself. By declaring our environment in a <code>flake.nix</code> file, we guarantee bit-for-bit reproducible environments across macOS and Linux.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">flake.nix</span><span class="code-lang">nix</span></div>
    <pre><span class="cmt"># Pinning the exact rust-toolchain to guarantee identical builds globally</span>
<span class="kw">let</span> toolchain = fenix.packages.${system}.fromToolchainFile {
  file = ./rust-toolchain.toml;
  sha256 = "sha256-s1MutIG0IMZ...";
}; <span class="kw">in</span> pkgs.mkShell {
  buildInputs = [ toolchain pkgs.mold pkgs.clang ];
}</pre></div>

    <h2>LLVM Internals and the Linker Bottleneck</h2>
    <p>To understand why large Rust projects compile slowly, you must understand the compilation pipeline. When you run <code>cargo build</code>, the Rust compiler (<code>rustc</code>) performs Lexical Analysis, Parsing, and Semantic Analysis (borrow checking, type checking). It then generates High-Level Intermediate Representation (HIR), lowers it to Mid-Level Intermediate Representation (MIR), and finally translates it into LLVM IR.</p>
    <p>LLVM takes this IR, performs aggressive optimization passes (inlining, loop unrolling), and emits machine code object files (<code>.o</code>). However, generating object files is highly parallelizable. The true bottleneck in Rust compilation occurs in the final step: <strong>Linking</strong>.</p>
    <p>The linker must take thousands of independent object files, resolve symbol references between them (e.g., function calls across crates), and stitch them together into a single executable binary. The default GNU linker (<code>ld</code>) is single-threaded and mathematically inefficient at this task. For large monolithic workspaces, linking alone can take 15-30 seconds per compilation, destroying developer velocity.</p>

    <h2>Overcoming the Bottleneck with `mold`</h2>
    <p>We replace the default GNU linker with <code>mold</code>, a modern, highly parallelized drop-in replacement written by the creator of the LLD linker. By leveraging multi-threading and optimized data structures for symbol resolution, <code>mold</code> can link multi-gigabyte binaries in mere milliseconds. This single change can drastically improve the feedback loop for an entire engineering team.</p>
</section>""",

    "project": """<section class="chapter" id="project">
    <div class="chapter-label">Chapter 02</div>
    <h1>Hexagonal Architecture & Cargo Workspaces</h1>

    <h2>The Monolith vs Microservices Debate</h2>
    <p>When starting a new project, architects often face the dilemma of choosing between a monolithic repository or a microservices architecture. Microservices offer isolated deployments and language flexibility, but introduce catastrophic complexity in network latency, distributed transactions, and eventual consistency. A monolith is easy to deploy, but often devolves into a "Big Ball of Mud" where domain boundaries are breached, making the codebase impossible to maintain.</p>
    <p>The solution is the <strong>Modular Monolith</strong>, implemented in Rust via <strong>Cargo Workspaces</strong>. A workspace allows us to split our codebase into multiple independent Crates (packages) within a single repository. Each Crate is compiled independently, enforcing strict compilation boundaries that prevent accidental architectural coupling.</p>

    <h2>Hexagonal Architecture (Ports and Adapters)</h2>
    <p>Within our workspace, we structure our crates using Hexagonal Architecture, also known as Ports and Adapters. The fundamental rule of Hexagonal Architecture is the <strong>Dependency Rule</strong>: source code dependencies must only point inward toward the core domain logic.</p>
    <p>The <strong>Domain</strong> is the absolute center of the application. It contains the core business logic, entities, and validation rules. It must have zero dependencies on external frameworks, databases, or HTTP protocols. It represents pure, uncontaminated logic.</p>
    <p>Surrounding the Domain are <strong>Ports</strong>. Ports are interfaces (in Rust, typically <code>Traits</code>) that define how the Domain wishes to communicate with the outside world. For example, the Domain might define an <code>EmailSender</code> trait.</p>
    <p>Finally, on the outer edges are the <strong>Adapters</strong>. Adapters implement the Ports using specific technologies. You might have an <code>adapters/postmark</code> crate that implements the <code>EmailSender</code> trait using the Postmark API, and an <code>adapters/axum</code> crate that translates HTTP requests into Domain commands.</p>

    <h2>Enforcing Boundaries with Rust Traits</h2>
    <p>By enforcing this architecture, if you decide to migrate from Postgres to MongoDB, or from Axum to Actix-Web, your core Domain logic does not change by a single line of code. You simply write a new Adapter crate and swap the dependency in your application's root composition layer. Cargo Workspaces mathematically enforce this separation, as the compiler will reject any attempt by the Domain crate to import from an Adapter crate.</p>
</section>""",

    "axum": """<section class="chapter" id="axum">
    <div class="chapter-label">Chapter 03</div>
    <h1>Advanced Routing: The Tower Service Trait</h1>

    <h2>Deconstructing the Web Framework</h2>
    <p>At first glance, the Axum web framework appears to be a magical black box that magically maps URL routes to asynchronous functions. However, to operate at the expert level, you must understand the underlying machinery. Axum is not actually a web framework; it is a thin layer of syntactic sugar built entirely on top of <code>tower::Service</code> and Tokio's asynchronous runtime.</p>
    
    <h2>The Tower Service Trait</h2>
    <p>The <code>tower::Service</code> trait is arguably the most important trait in the Rust backend ecosystem. It is an abstraction of an asynchronous function that takes a Request and returns a Response. Every router, every middleware, and every endpoint handler in Axum is fundamentally just an implementation of <code>Service</code>.</p>
    <p>The trait consists of two primary methods: <code>poll_ready</code> and <code>call</code>.</p>
    
    <div class="code-block"><div class="code-header"><span class="code-filename">tower/service.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">pub trait</span> <span class="type">Service</span>&lt;Request&gt; {
    <span class="kw">type</span> <span class="type">Response</span>;
    <span class="kw">type</span> <span class="type">Error</span>;
    <span class="kw">type</span> <span class="type">Future</span>: <span class="type">Future</span>&lt;Output = <span class="type">Result</span>&lt;<span class="kw">Self</span>::<span class="type">Response</span>, <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt;;

    <span class="kw">fn</span> <span class="fn">poll_ready</span>(&amp;<span class="kw">mut self</span>, cx: &amp;<span class="kw">mut</span> <span class="type">Context</span>&lt;<span class="lifetime">'_</span>&gt;) -&gt; <span class="type">Poll</span>&lt;<span class="type">Result</span>&lt;(), <span class="kw">Self</span>::<span class="type">Error</span>&gt;&gt;;
    <span class="kw">fn</span> <span class="fn">call</span>(&amp;<span class="kw">mut self</span>, req: Request) -&gt; <span class="kw">Self</span>::<span class="type">Future</span>;
}</pre></div>

    <h2>Backpressure and Resource Exhaustion</h2>
    <p>Why does <code>poll_ready</code> exist? Why not just use <code>call</code> directly? The answer is <strong>Backpressure</strong>. In a hyperscale system, if a downstream component (like a database) is overwhelmed, continuing to accept incoming HTTP requests will result in an unbounded queue of futures waiting in memory, inevitably leading to an Out-Of-Memory (OOM) crash.</p>
    <p><code>poll_ready</code> allows a Service to signal whether it has the capacity to handle a new request *before* the request is actually processed. If a Rate Limiting middleware implements <code>poll_ready</code> and detects that the quota is exceeded, it can return an error immediately, shedding the load and protecting the core system.</p>
    
    <h2>Writing Custom Middleware</h2>
    <p>While standard middleware crates exist, complex business logic often requires custom implementations. By writing a struct that implements <code>Service</code>, you can intercept requests, manipulate headers, query databases, or execute dynamic Lua scripts in Redis to determine if a request should proceed. Understanding <code>tower::Service</code> is the key to unlocking the true power of the Rust network stack.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/middleware/rate_limit.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">impl</span>&lt;S, <span class="type">ReqBody</span>&gt; <span class="type">Service</span>&lt;<span class="type">Request</span>&lt;<span class="type">ReqBody</span>&gt;&gt; <span class="kw">for</span> <span class="type">RateLimit</span>&lt;S&gt; {
    <span class="kw">fn</span> <span class="fn">poll_ready</span>(&amp;<span class="kw">mut self</span>, cx: &amp;<span class="kw">mut</span> <span class="type">Context</span>&lt;<span class="lifetime">'_</span>&gt;) -&gt; <span class="type">Poll</span>&lt;<span class="type">Result</span>&lt;(), <span class="type">Self::Error</span>&gt;&gt; {
        <span class="kw">if</span> <span class="kw">self</span>.limiter.check().is_err() {
            <span class="cmt">// Backpressure: Shed load immediately before processing the request</span>
            <span class="kw">return</span> <span class="type">Poll</span>::<span class="type">Ready</span>(<span class="type">Err</span>(Error::TooManyRequests));
        }
        <span class="kw">self</span>.inner.poll_ready(cx)
    }
}</pre></div>
</section>""",

    "config": """<section class="chapter" id="config">
    <div class="chapter-label">Chapter 04</div>
    <h1>Zero-Trust Configuration: HashiCorp Vault</h1>
    
    <h2>The Fatal Flaw of Environment Variables</h2>
    <p>For decades, the industry standard for configuration management has been the "Twelve-Factor App" methodology, which dictates storing configuration in Environment Variables. In modern cloud architectures, this is a fatal security flaw. Environment variables are inherited by child processes, logged by default crash reporters, and easily dumped by an attacker who gains minimal execution rights by simply reading <code>/proc/pid/environ</code>.</p>
    
    <h2>Zero-Trust Architecture</h2>
    <p>In a Zero-Trust Architecture, we assume the network is already compromised. No secret is permanent, and no secret is stored in plain text. We utilize the <code>figment</code> crate for robust, layered configuration merging (combining base YAML files with environment-specific overrides), but we strictly exclude sensitive secrets from these files.</p>
    <p>Instead, our application retrieves short-lived, dynamically generated database credentials and API keys directly from an encrypted secret store like <strong>HashiCorp Vault</strong> or <strong>AWS KMS</strong> at boot time. Vault uses a Shamir's Secret Sharing algorithm to protect its master key, and issues credentials with strict Time-To-Live (TTL) leases. If a key is leaked, it is mathematically guaranteed to expire and become useless within minutes.</p>
    
    <h2>Memory Safety and the Secrecy Crate</h2>
    <p>Even if you securely fetch a key from Vault, it must exist in your server's RAM. If an attacker triggers a buffer over-read (similar to the Heartbleed vulnerability) or dumps the core memory of the process, they can extract the secret. To mitigate this, we wrap all sensitive configuration values in the <code>secrecy::Secret</code> type.</p>
    <p>The <code>Secret</code> type prevents accidental logging by overriding the <code>Debug</code> formatter to display "[REDACTED]". More importantly, it utilizes the <code>Zeroize</code> trait. When the <code>Secret</code> goes out of scope and is dropped, the Rust compiler injects a volatile write instruction to overwrite the memory address with zeroes. This prevents the compiler from optimizing away the memory wipe, ensuring that the secret is cryptographically erased from RAM the instant it is no longer needed.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/config.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">figment</span>::{<span class="type">Figment</span>, <span class="type">providers</span>::{<span class="type">Env</span>, <span class="type">Format</span>, <span class="type">Yaml</span>}};
<span class="kw">use</span> <span class="type">secrecy</span>::<span class="type">Secret</span>;

<span class="attr">#[derive(Deserialize)]</span>
<span class="kw">pub struct</span> <span class="type">Settings</span> {
    <span class="cmt">// Memory zeroing on drop guarantees the secret is wiped from RAM</span>
    <span class="kw">pub</span> database_url: <span class="type">Secret</span>&lt;<span class="type">String</span>&gt;,
}</pre></div>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to Unit 1 (Chapters 01-04).")
