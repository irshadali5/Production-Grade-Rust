import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="config">
    <div class="chapter-label">Chapter 04</div>
    <h1>Intensive Deep Dive: Secrets, Zeroization, & Vault</h1>

    <h2>1. The Heartbleed Catastrophe & Memory Forensics</h2>
    <p>In standard web applications, developers load database passwords and API keys from a <code>.env</code> file into a standard <code>String</code> type. This is a catastrophic vulnerability. When a standard <code>String</code> in Rust (or any language) is dropped or reallocated, the memory it occupied is not explicitly erased; it is merely marked as "available" by the OS allocator. The plain-text password remains fully intact in the physical RAM chips.</p>
    <p>If an attacker leverages a memory-disclosure vulnerability (exactly like the infamous 2014 OpenSSL <strong>Heartbleed</strong> bug), they can send a malformed packet that forces your server to return 64 kilobytes of uninitialized heap memory. The attacker will instantly read the ghost echoes of your un-erased strings, stealing your master Postgres password in plain text. Furthermore, if the Linux kernel swaps memory to disk during high load, your un-erased passwords are written directly to the hard drive, completely bypassing filesystem encryption.</p>

    <h2>2. Cryptographic Zeroization via the `secrecy` Crate</h2>
    <p>To operate at a production-grade level, we must mathematically guarantee that secrets are destroyed at the hardware level the exact microsecond they are no longer needed. We achieve this using the <code>secrecy</code> crate.</p>
    <p>Instead of <code>String</code>, we load passwords into a <code>Secret&lt;String&gt;</code>. This wrapper acts as a cryptographic black hole. First, it prevents accidental logging; if you attempt to <code>println!("{:?}", secret)</code>, it will output <code>[REDACTED]</code>, preventing keys from leaking into Datadog or AWS CloudWatch. More importantly, the <code>secrecy</code> crate implements the <code>Zeroize</code> trait. When the <code>Secret</code> falls out of scope, the `Drop` implementation executes a specialized LLVM intrinsic that physically overwrites the specific RAM addresses with zeros before returning the memory to the allocator. It uses <code>std::sync::atomic::compiler_fence</code> to mathematically guarantee that the LLVM optimizer cannot "optimize away" the zeroing operation.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/config.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">secrecy</span>::{<span class="type">Secret</span>, <span class="type">ExposeSecret</span>};
<span class="kw">use</span> <span class="type">serde</span>::<span class="type">Deserialize</span>;

<span class="attr">#[derive(Deserialize, Debug)]</span>
<span class="kw">pub struct</span> <span class="type">DatabaseConfig</span> {
    <span class="kw">pub</span> host: <span class="type">String</span>,
    <span class="kw">pub</span> port: <span class="type">u16</span>,
    <span class="kw">pub</span> username: <span class="type">String</span>,
    <span class="cmt">// Secret&lt;T&gt; prevents logging and physically zeroizes RAM on Drop</span>
    <span class="kw">pub</span> password: <span class="type">Secret</span>&lt;<span class="type">String</span>&gt;,
}

<span class="kw">impl</span> <span class="type">DatabaseConfig</span> {
    <span class="kw">pub fn</span> <span class="fn">connection_string</span>(&amp;<span class="kw">self</span>) -&gt; <span class="type">Secret</span>&lt;<span class="type">String</span>&gt; {
        <span class="cmt">// To use the password, we must explicitly call expose_secret().</span>
        <span class="cmt">// This acts as an architectural tripwire, forcing the developer</span>
        <span class="cmt">// to acknowledge they are handling raw cryptographic material.</span>
        <span class="type">Secret</span>::<span class="fn">new</span>(<span class="mac">format!</span>(
            <span class="str">"postgres://{}:{}@{}:{}"</span>,
            <span class="kw">self</span>.username,
            <span class="kw">self</span>.password.<span class="fn">expose_secret</span>(),
            <span class="kw">self</span>.host,
            <span class="kw">self</span>.port
        ))
    }
}</pre></div>

    <h2>3. The Flaw of Static `.env` Files</h2>
    <p>Even with memory zeroization, relying on <code>.env</code> files or Kubernetes Secrets (which are just Base64 encoded) is unacceptable for a hyperscale architecture. Static secrets do not expire. If a disgruntled employee leaves the company, or an API key is accidentally committed to GitHub, the credentials remain valid indefinitely until manually rotated. Manual rotation requires restarting the entire Kubernetes cluster, resulting in production downtime.</p>

    <h2>4. HashiCorp Vault & Shamir's Secret Sharing</h2>
    <p>We replace static files with <strong>HashiCorp Vault</strong>, an identity-based secrets and encryption management system. Vault does not just store passwords; it acts as a dynamic cryptographic authority.</p>
    
    <h3>4.1 Shamir's Secret Sharing (Unsealing the Vault)</h3>
    <p>When Vault is deployed, it starts in a "Sealed" state, meaning it cannot read its own encrypted hard drive. The master decryption key is mathematically split into 5 pieces using an advanced polynomial interpolation algorithm known as <strong>Shamir's Secret Sharing</strong>. These 5 pieces are given to 5 different human executives in the company.</p>
    <p>To unseal Vault, the algorithm dictates that any 3 of the 5 keys must be provided. This mathematically prevents any single rogue employee from accessing the master cryptographic keys, enforcing absolute physical security.</p>

    <h3>4.2 Dynamic Secret Generation</h3>
    <p>Once unsealed, our Rust application authenticates with Vault using its Kubernetes Service Account token. Instead of asking Vault for "the Postgres password," it asks Vault for a "Database Lease." Vault connects to Postgres via a root account, generates a brand new, highly randomized Postgres user and password, and returns these ephemeral credentials to our Rust app with a <strong>Time-To-Live (TTL)</strong> of exactly 1 hour.</p>
    <p>Every hour, a background Tokio task in our Rust application seamlessly contacts Vault to renew the lease or generate a new one. If an attacker manages to steal the Postgres password from our Rust server, the password will mathematically self-destruct in the Postgres database 60 minutes later, completely locking the attacker out without any human intervention or server restarts.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/vault_client.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">reqwest</span>::<span class="type">Client</span>;
<span class="kw">use</span> <span class="type">secrecy</span>::{<span class="type">Secret</span>, <span class="type">ExposeSecret</span>};
<span class="kw">use</span> <span class="type">serde</span>::<span class="type">Deserialize</span>;

<span class="attr">#[derive(Deserialize)]</span>
<span class="kw">struct</span> <span class="type">VaultResponse</span> {
    lease_duration: <span class="type">u64</span>,
    data: <span class="type">VaultCredentials</span>,
}

<span class="attr">#[derive(Deserialize)]</span>
<span class="kw">struct</span> <span class="type">VaultCredentials</span> {
    username: <span class="type">String</span>,
    password: <span class="type">Secret</span>&lt;<span class="type">String</span>&gt;,
}

<span class="kw">pub async fn</span> <span class="fn">fetch_dynamic_postgres_creds</span>(
    client: &amp;<span class="type">Client</span>, 
    vault_addr: &amp;str, 
    vault_token: &amp;<span class="type">Secret</span>&lt;<span class="type">String</span>&gt;
) -&gt; <span class="type">Result</span>&lt;(<span class="type">VaultCredentials</span>, <span class="type">u64</span>), <span class="type">reqwest</span>::<span class="type">Error</span>&gt; {
    <span class="kw">let</span> url = <span class="mac">format!</span>(<span class="str">"{}/v1/database/creds/my-role"</span>, vault_addr);
    
    <span class="kw">let</span> response = client.<span class="fn">get</span>(&amp;url)
        .header(<span class="str">"X-Vault-Token"</span>, vault_token.<span class="fn">expose_secret</span>())
        .<span class="fn">send</span>()
        .<span class="kw">await</span>?
        .<span class="fn">json</span>::&lt;<span class="type">VaultResponse</span>&gt;()
        .<span class="kw">await</span>?;

    <span class="cmt">// Returns the ephemeral credentials and the TTL in seconds.</span>
    <span class="cmt">// The caller must spawn a Tokio background task to sleep for (TTL - 60) seconds</span>
    <span class="cmt">// and then rotate the connection pool with new credentials.</span>
    <span class="type">Ok</span>((response.data, response.lease_duration))
}</pre></div>

    <p>By combining LLVM-level memory zeroization with the mathematically sound polynomial interpolation of Shamir's Secret Sharing and dynamic lease generation, we construct an impenetrable cryptographic fortress for our hyperscale application.</p>
</section>"""

pattern = r'<section class="chapter" id="config">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 04.")
