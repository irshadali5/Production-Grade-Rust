import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="testing">
    <div class="chapter-label">Chapter 07</div>
    <h1>Intensive Deep Dive: The Fallacy of Mocks & Testcontainers</h1>

    <h2>1. The Catastrophe of In-Memory Mocks</h2>
    <p>In standard software development, engineers are taught to write Unit Tests by aggressively mocking the infrastructure layer. If a function saves a user to Postgres, the developer will use a framework to create a Mock Database that merely records that the <code>save()</code> function was called. Alternatively, they might swap Postgres for an in-memory SQLite database during the CI/CD pipeline to achieve faster test execution times.</p>
    <p>This is a catastrophic testing anti-pattern. <strong>SQLite is not Postgres.</strong> SQLite does not enforce strict foreign key constraints by default, it does not support advanced JSONB indexing, and it handles concurrent transaction locking entirely differently than Postgres. If you run your tests against SQLite (or a Mock), your tests will pass with a 100% success rate, but your code will instantly crash in production when it encounters a Postgres-specific syntax error or a real-world transaction deadlock. Mocks do not verify that your system works; they only verify that your system works against a hallucinatory simulation of reality.</p>

    <h2>2. Ephemeral Docker Sockets (Testcontainers)</h2>
    <p>To achieve absolute mathematical confidence in our CI/CD pipeline, we must test against the exact binary image that will run in production. We achieve this using <strong>Testcontainers</strong>.</p>
    <p>Testcontainers is a library that communicates directly with the Docker Daemon via the Unix Socket (<code>/var/run/docker.sock</code>). When you execute <code>cargo test</code>, the Testcontainers Rust crate intercepts the test runner. Before executing the test logic, it sends an HTTP command to the Docker socket, instructing Docker to physically download and boot a pristine, completely isolated Postgres container (e.g., <code>postgres:16-alpine</code>). It maps a randomized ephemeral port to the container, and returns the dynamic connection string to your Rust test.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/tests/integration.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">testcontainers_modules</span>::<span class="type">postgres</span>::<span class="type">Postgres</span>;
<span class="kw">use</span> <span class="type">testcontainers</span>::<span class="type">runners</span>::<span class="type">AsyncRunner</span>;
<span class="kw">use</span> <span class="type">sqlx</span>::<span class="type">PgPool</span>;

<span class="attr">#[tokio::test]</span>
<span class="kw">async fn</span> <span class="fn">test_user_insertion_violates_unique_constraint</span>() {
    <span class="cmt">// 1. The test runner halts and physically boots a Docker container</span>
    <span class="kw">let</span> node = <span class="type">Postgres</span>::<span class="fn">default</span>().<span class="fn">start</span>().<span class="kw">await</span>.unwrap();
    
    <span class="cmt">// 2. We extract the dynamic connection string mapped by Docker</span>
    <span class="kw">let</span> connection_string = <span class="mac">format!</span>(
        <span class="str">"postgres://postgres:postgres@127.0.0.1:{}/postgres"</span>,
        node.<span class="fn">get_host_port_ipv4</span>(<span class="num">5432</span>).<span class="kw">await</span>.unwrap()
    );
    
    <span class="cmt">// 3. We connect sqlx directly to the real, isolated Postgres instance</span>
    <span class="kw">let</span> pool = <span class="type">PgPool</span>::<span class="fn">connect</span>(&amp;connection_string).<span class="kw">await</span>.unwrap();
    
    <span class="cmt">// 4. We run our strict migrations against the ephemeral database</span>
    <span class="mac">sqlx::migrate!</span>(<span class="str">"./migrations"</span>).<span class="fn">run</span>(&amp;pool).<span class="kw">await</span>.unwrap();
    
    <span class="cmt">// 5. We execute the test logic. If it passes, we have 100% mathematical</span>
    <span class="cmt">// certainty that it will pass in production.</span>
    <span class="kw">let</span> result = <span class="fn">insert_duplicate_user</span>(&amp;pool).<span class="kw">await</span>;
    <span class="mac">assert!</span>(result.<span class="fn">is_err</span>());
    
    <span class="cmt">// 6. When the `node` variable drops out of scope, the Drop implementation</span>
    <span class="cmt">// triggers the Ryuk container to brutally assassinate the Postgres container,</span>
    <span class="cmt">// wiping all state from RAM.</span>
}</pre></div>

    <h2>3. The Ryuk Reaper & Deterministic Isolation</h2>
    <p>A major challenge with integration testing is "State Bleed." If Test A modifies the database, and Test B reads the database expecting it to be empty, Test B will randomly fail (a "flaky test"). With Testcontainers, every single <code>#[tokio::test]</code> function boots its own completely isolated Postgres container.</p>
    <p>To prevent these thousands of containers from overwhelming the host machine's RAM, Testcontainers utilizes a specialized sidecar container named <strong>Ryuk</strong>. Ryuk maintains a TCP heartbeat connection with the Rust test runner. The absolute instant the <code>node</code> variable falls out of scope at the end of the test function, the TCP connection drops. Ryuk detects this drop and instantly sends a <code>SIGKILL</code> to the Docker daemon, violently terminating the Postgres container and wiping its state from memory. This guarantees flawless deterministic isolation without manual teardown scripts.</p>

    <h2>4. Testing the Boundary (HTTP & Axum)</h2>
    <p>We do not stop at testing the database; we must test the entire HTTP boundary. However, actually binding an Axum server to a real TCP port (like <code>127.0.0.1:8080</code>) during tests is prone to "Port Already in Use" errors when running tests in parallel across 16 CPU cores.</p>
    <p>Because Axum is built on the <code>tower::Service</code> trait, we bypass the TCP layer entirely. We can mathematically construct an HTTP <code>Request</code> in memory, and pass it directly into the Axum Router's <code>call</code> method. The router processes the request identically to a real network call, executing all middleware, and returns an HTTP <code>Response</code> entirely in RAM. This allows us to run thousands of full-stack integration tests in parallel with zero network latency and zero port collisions.</p>
</section>"""

pattern = r'<section class="chapter" id="testing">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 07.")
