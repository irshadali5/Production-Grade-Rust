import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="project">
    <div class="chapter-label">Chapter 02</div>
    <h1>Hexagonal Architecture & Cargo Workspaces</h1>

    <h2>1. The Monolith vs. Microservices Paradigm</h2>
    <p>The architectural foundation of an application dictates its maximum theoretical scale. When starting a new project, technical leads inevitably face the industry's most fiercely debated dichotomy: the Monolith versus the Microservices Architecture.</p>
    <p>A Microservices architecture offers isolated deployments, fault domains, and the freedom to mix programming languages (e.g., Python for data science, Rust for performance). However, it introduces catastrophic distributed systems complexity. You are forced to deal with network latency, asynchronous eventual consistency, the Saga pattern for distributed transactions, and the impossibility of a true, global database join. If Service A needs data from Service B, it must execute an HTTP request, wait for TLS negotiation, parse JSON, and handle network timeouts.</p>
    <p>Conversely, a standard Monolith is incredibly fast. A function call between the "Billing" module and the "User" module takes nanoseconds because it happens in the same memory space. There is no network overhead, and database transactions guarantee ACID properties across the entire system. However, standard monoliths almost inevitably devolve into a "Big Ball of Mud." Because there are no physical boundaries between modules, developers accidentally (or intentionally) couple the modules together. The "Billing" module starts reading directly from the "User" database table. Eventually, the codebase becomes so entangled that changing a single line of code in the Auth system breaks the Billing system, rendering the monolith impossible to maintain.</p>

    <h2>2. The Modular Monolith</h2>
    <p>We reject both the Big Ball of Mud and the Distributed Microservices nightmare. We build a <strong>Modular Monolith</strong>. A Modular Monolith executes as a single, highly optimized binary process (retaining nanosecond function calls and global ACID transactions), but its internal modules are strictly, mathematically isolated from one another by the compiler.</p>
    <p>In Rust, we enforce this isolation using <strong>Cargo Workspaces</strong>. A workspace allows us to split our codebase into multiple independent Crates (packages) within a single Git repository. Each Crate is compiled independently. If the <code>billing</code> crate does not explicitly declare the <code>user</code> crate as a dependency in its <code>Cargo.toml</code>, the Rust compiler will instantly reject any attempt by the <code>billing</code> crate to import code from the <code>user</code> crate. We achieve the strict boundaries of Microservices with the performance of a Monolith.</p>

    <h2>3. Hexagonal Architecture (Ports and Adapters)</h2>
    <p>Within our workspace, we must structure the crates themselves using <strong>Hexagonal Architecture</strong>, originally formalized by Alistair Cockburn (also known as the Ports and Adapters pattern).</p>
    <p>The fundamental, unbreakable law of Hexagonal Architecture is the <strong>Dependency Rule</strong>: Source code dependencies must only point inward toward the core domain logic. Outer layers can depend on inner layers, but inner layers can <em>never</em> depend on outer layers.</p>

    <h3>3.1 The Domain Layer (The Core)</h3>
    <p>The <strong>Domain</strong> is the absolute center of the hexagon. It contains the core business logic, the Entities (e.g., <code>User</code>, <code>Subscription</code>), and the mathematical rules that govern your application (e.g., "A subscription cannot be active if the user is banned").</p>
    <p>The Domain must have <strong>zero</strong> dependencies on external frameworks, databases, or HTTP protocols. It cannot depend on `axum`, it cannot depend on `sqlx`, and it cannot depend on `reqwest`. It is pure, uncontaminated Rust logic. If you decide to migrate your application from an HTTP server to a CLI tool, or from Postgres to MongoDB, your Domain layer does not change by a single line of code.</p>

    <h3>3.2 Ports (The Interfaces)</h3>
    <p>If the Domain cannot depend on a database crate, how does it save a User to the database? It uses <strong>Ports</strong>. A Port is an abstract interface (in Rust, a <code>Trait</code>) defined <em>inside</em> the Domain layer. It dictates how the Domain wishes to communicate with the outside world.</p>
    <p>For example, the Domain might define a <code>UserRepository</code> trait with a method <code>fn save(&self, user: User) -> Result<(), DomainError></code>. The Domain knows that <em>something</em> will save the user, but it has no idea whether it is saving to Postgres, Redis, or a mocked hash map in memory.</p>

    <h3>3.3 Adapters (The Infrastructure)</h3>
    <p>On the outer edge of the hexagon are the <strong>Adapters</strong>. Adapters implement the Ports using specific, real-world technologies. You create an <code>adapters/postgres</code> crate that depends on <code>sqlx</code>. This crate imports the <code>UserRepository</code> trait from the Domain crate and implements it. The Adapter translates the Domain's pure request into raw SQL, executes it against Postgres, and translates the result back into Domain entities.</p>

    <h2>4. Implementing the Workspace</h2>
    <p>To implement this in Rust, we create a root <code>Cargo.toml</code> that defines the workspace members. We separate our application into three primary crates: <code>domain</code>, <code>infrastructure</code> (Adapters), and <code>api</code> (the composition root and HTTP server).</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">Cargo.toml (Workspace Root)</span><span class="code-lang">toml</span></div>
    <pre><span class="cmt"># Cargo.toml at the root of the repository</span>
[workspace]
members = [
    "crates/domain",
    "crates/infrastructure",
    "crates/api"
]
resolver = "2"

<span class="cmt"># Workspace dependencies ensure all crates use the exact same version of third-party libraries</span>
[workspace.dependencies]
tokio = { version = "1.37", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
uuid = { version = "1.8", features = ["v4"] }</pre></div>

    <h3>4.1 The Domain Port Definition</h3>
    <p>Inside the <code>crates/domain</code> folder, we define our pure business logic and our Ports (Traits). Notice that this file has absolutely no concept of SQL or HTTP.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">crates/domain/src/repository.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">async_trait</span>::<span class="type">async_trait</span>;
<span class="kw">use</span> <span class="kw">crate</span>::<span class="type">user</span>::<span class="type">User</span>;
<span class="kw">use</span> <span class="kw">crate</span>::<span class="type">error</span>::<span class="type">DomainError</span>;

<span class="cmt">// This is the "Port". The domain defines what it needs, but not how it happens.</span>
<span class="attr">#[async_trait]</span>
<span class="kw">pub trait</span> <span class="type">UserRepository</span>: <span class="type">Send</span> + <span class="type">Sync</span> {
    <span class="kw">async fn</span> <span class="fn">save</span>(&amp;<span class="kw">self</span>, user: &amp;<span class="type">User</span>) -&gt; <span class="type">Result</span>&lt;(), <span class="type">DomainError</span>&gt;;
    <span class="kw">async fn</span> <span class="fn">find_by_id</span>(&amp;<span class="kw">self</span>, id: <span class="type">uuid</span>::<span class="type">Uuid</span>) -&gt; <span class="type">Result</span>&lt;<span class="type">Option</span>&lt;<span class="type">User</span>&gt;, <span class="type">DomainError</span>&gt;;
}</pre></div>

    <h3>4.2 The Infrastructure Adapter Implementation</h3>
    <p>Inside the <code>crates/infrastructure</code> folder, we implement the Port using Postgres. This crate explicitly depends on the <code>domain</code> crate in its <code>Cargo.toml</code>, satisfying the Dependency Rule (dependencies point inward). If you ever want to migrate to MongoDB, you simply write a new <code>MongoUserRepository</code> struct in this crate, implementing the exact same trait.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">crates/infrastructure/src/postgres_user_repo.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">domain</span>::{<span class="type">UserRepository</span>, <span class="type">User</span>, <span class="type">DomainError</span>};
<span class="kw">use</span> <span class="type">sqlx</span>::<span class="type">PgPool</span>;
<span class="kw">use</span> <span class="type">async_trait</span>::<span class="type">async_trait</span>;

<span class="cmt">// This is the "Adapter". It translates between Domain and Postgres.</span>
<span class="kw">pub struct</span> <span class="type">PostgresUserRepository</span> {
    pool: <span class="type">PgPool</span>,
}

<span class="kw">impl</span> <span class="type">PostgresUserRepository</span> {
    <span class="kw">pub fn</span> <span class="fn">new</span>(pool: <span class="type">PgPool</span>) -&gt; <span class="kw">Self</span> { <span class="kw">Self</span> { pool } }
}

<span class="attr">#[async_trait]</span>
<span class="kw">impl</span> <span class="type">UserRepository</span> <span class="kw">for</span> <span class="type">PostgresUserRepository</span> {
    <span class="kw">async fn</span> <span class="fn">save</span>(&amp;<span class="kw">self</span>, user: &amp;<span class="type">User</span>) -&gt; <span class="type">Result</span>&lt;(), <span class="type">DomainError</span>&gt; {
        <span class="mac">sqlx::query!</span>(
            <span class="str">"INSERT INTO users (id, email) VALUES ($1, $2)"</span>,
            user.id,
            user.email.as_str()
        )
        .<span class="fn">execute</span>(&amp;<span class="kw">self</span>.pool)
        .<span class="kw">await</span>
        .<span class="fn">map_err</span>(|e| <span class="type">DomainError</span>::<span class="type">Database</span>(e.<span class="fn">to_string</span>()))?;
        
        <span class="type">Ok</span>(())
    }
    
    <span class="cmt">// ... find_by_id implementation ...</span>
}</pre></div>

    <h2>5. The Composition Root</h2>
    <p>The final component of this architecture is the <strong>Composition Root</strong>. This is typically your <code>api</code> crate or the <code>main.rs</code> binary file. The Composition Root is the only layer of the application that is allowed to depend on <em>everything</em>. Its sole responsibility is to instantiate the specific Adapters (e.g., connecting to Postgres to create a <code>PostgresUserRepository</code>), instantiate the Domain services, and wire them together. It then mounts the HTTP routes in Axum and starts the server.</p>
    <p>By enforcing this strict Hexagonal Workspace structure, you guarantee that your application can scale to hundreds of developers. Domain logic remains pristine and fully testable in isolation (via mock adapters), while infrastructure remains entirely modular and swappable.</p>
</section>"""

pattern = r'<section class="chapter" id="project">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Deep Essay expansion applied to Chapter 02.")
