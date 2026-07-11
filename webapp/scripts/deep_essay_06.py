import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="migrations">
    <div class="chapter-label">Chapter 06</div>
    <h1>Intensive Deep Dive: Schema Evolution & Type-Driven Design</h1>

    <h2>1. The Danger of Schema Drift</h2>
    <p>In a production system, the database schema is not static; it is a living entity that evolves alongside the business requirements. A catastrophic error committed by junior teams is manually executing <code>ALTER TABLE</code> statements in the production database console. This guarantees <strong>Schema Drift</strong>—a state where the production database schema diverges from the staging database, and neither matches the Rust code's structs. When this happens, a deployment that passes all tests in staging will instantly crash in production because a required column is missing.</p>
    <p>We eliminate this mathematically using <strong>Strict Migrations</strong>. Every single alteration to the database schema must be codified as a deterministic, sequential SQL file (e.g., <code>20240101000000_create_users_table.sql</code>) and committed to Git. During CI/CD deployment, our Rust application binary itself acts as the migration engine. Before binding to the TCP port to accept HTTP traffic, the Rust application queries a special <code>_sqlx_migrations</code> tracking table to determine which migrations have already been applied. It then sequentially executes only the missing migrations, utilizing Postgres' transactional DDL to guarantee that if a migration fails halfway through, the entire schema change is cleanly rolled back.</p>

    <h2>2. Primitive Obsession and Domain Integrity</h2>
    <p>Once the database schema is sound, we must map it to Rust. A common anti-pattern is <strong>Primitive Obsession</strong>. Suppose you have a function that transfers funds: <code>fn transfer(from_account: String, to_account: String, amount: f64)</code>. Because both account IDs are standard <code>String</code> types, there is absolutely nothing stopping a developer from accidentally passing the <code>to_account</code> into the <code>from_account</code> parameter, or worse, passing a user's email address instead of their account ID. The compiler will happily compile this logical error, resulting in financial catastrophe in production.</p>

    <h2>3. The Newtype Pattern: Zero-Cost Domain Types</h2>
    <p>To operate at the highest level of software engineering, we utilize <strong>Type-Driven Design</strong> via the <strong>Newtype Pattern</strong>. We wrap our primitive types inside a Tuple Struct. We define <code>struct AccountId(String);</code> and <code>struct Email(String);</code>. Now, our function signature becomes <code>fn transfer(from_account: AccountId, to_account: AccountId, amount: f64)</code>.</p>
    <p>If a developer attempts to pass an <code>Email</code> into the <code>from_account</code> parameter, the Rust compiler will throw a fatal type error and halt the build. We have mathematically elevated a runtime logic error into a compile-time syntax error.</p>

    <h3>3.1 Memory Layout and Zero-Cost Abstractions</h3>
    <p>A critical question arises: does wrapping a <code>String</code> inside a <code>struct AccountId(String)</code> consume extra memory or introduce CPU overhead? The answer is a resounding <strong>no</strong>. In Rust, a single-element Tuple Struct is a <strong>Zero-Cost Abstraction</strong>. During compilation, the LLVM optimizer mathematically proves that the struct wrapper has no behavioral overhead, and it physically strips the struct wrapper away. The resulting machine code uses the exact same memory layout (a pointer, length, and capacity) as a raw <code>String</code>. You achieve absolute compile-time domain safety with zero runtime penalty.</p>

    <h2>4. Parsing, Not Validating</h2>
    <p>The true power of the Newtype Pattern is unlocked when we restrict its instantiation. We do not make the inner <code>String</code> public. Instead, we implement a <code>parse</code> method that performs rigorous domain validation (e.g., checking that the Email contains an '@' symbol and a valid domain). This method returns a <code>Result&lt;Email, ParseError&gt;</code>.</p>
    <p>This enforces the architectural principle of <strong>"Parse, Don't Validate."</strong> Once a raw <code>String</code> has been successfully parsed into an <code>Email</code> struct at the outermost edge of our API (e.g., during the Axum JSON deserialization), the rest of our inner domain logic never has to check if the email is valid again. If a function requires an <code>Email</code> struct, the very existence of the struct in memory is mathematical proof that the data has already been validated.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/domain/email.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">serde</span>::{<span class="type">Deserialize</span>, <span class="type">Serialize</span>};
<span class="kw">use</span> <span class="type">validator</span>::<span class="type">validate_email</span>;

<span class="attr">#[derive(Debug, Clone, Serialize)]</span>
<span class="cmt">// The Newtype wrapper. The inner String is private.</span>
<span class="kw">pub struct</span> <span class="type">Email</span>(<span class="type">String</span>);

<span class="kw">impl</span> <span class="type">Email</span> {
    <span class="cmt">// The sole entry point for creating an Email struct.</span>
    <span class="kw">pub fn</span> <span class="fn">parse</span>(s: <span class="type">String</span>) -&gt; <span class="type">Result</span>&lt;<span class="type">Email</span>, <span class="type">String</span>&gt; {
        <span class="kw">if</span> <span class="fn">validate_email</span>(&amp;s) {
            <span class="type">Ok</span>(<span class="kw">Self</span>(s))
        } <span class="kw">else</span> {
            <span class="type">Err</span>(<span class="mac">format!</span>(<span class="str">"{} is not a valid email address."</span>, s))
        }
    }
    
    <span class="kw">pub fn</span> <span class="fn">as_ref</span>(&amp;<span class="kw">self</span>) -&gt; &amp;str {
        &amp;<span class="kw">self</span>.<span class="num">0</span>
    }
}

<span class="cmt">// Implementing Deserialize to enforce parsing at the API boundary (Axum)</span>
<span class="kw">impl</span>&lt;<span class="lifetime">'de</span>&gt; <span class="type">Deserialize</span>&lt;<span class="lifetime">'de</span>&gt; <span class="kw">for</span> <span class="type">Email</span> {
    <span class="kw">fn</span> <span class="fn">deserialize</span>&lt;D&gt;(deserializer: D) -&gt; <span class="type">Result</span>&lt;<span class="kw">Self</span>, D::<span class="type">Error</span>&gt;
    <span class="kw">where</span>
        D: <span class="type">serde</span>::<span class="type">Deserializer</span>&lt;<span class="lifetime">'de</span>&gt;,
    {
        <span class="kw">let</span> s = <span class="type">String</span>::<span class="fn">deserialize</span>(deserializer)?;
        <span class="type">Email</span>::<span class="fn">parse</span>(s).<span class="fn">map_err</span>(<span class="type">serde</span>::<span class="type">de</span>::<span class="type">Error</span>::<span class="type">custom</span>)
    }
}</pre></div>

    <p>By defining our <code>sqlx</code> database models using these Newtypes, we guarantee that invalid data can never be read from or written to the database. The Rust compiler becomes an impenetrable fortress around our core business logic.</p>
</section>"""

pattern = r'<section class="chapter" id="migrations">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 06.")
