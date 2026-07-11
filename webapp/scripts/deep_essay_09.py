import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="errors">
    <div class="chapter-label">Chapter 09</div>
    <h1>Intensive Deep Dive: Error Trait & Dynamic Dispatch</h1>

    <h2>1. The Catastrophe of Exceptions</h2>
    <p>In languages like Java, Python, and C++, errors are handled using Exceptions (<code>try/catch</code>). Exceptions are fundamentally broken for hyperscale systems. When an exception is thrown, it violently disrupts the Control Flow Graph. The runtime must pause execution, unwind the call stack (which is a massively expensive CPU operation), and search for a matching <code>catch</code> block. Furthermore, exceptions are invisible in the function signature. If you call <code>fetch_user()</code> in Python, you have no mathematical way to know if it will return a user or throw a <code>DatabaseConnectionException</code>. This leads to production crashes when unhandled exceptions bubble up to the main thread.</p>
    <p>Rust eliminates exceptions entirely. Errors in Rust are simply data. The <code>Result&lt;T, E&gt;</code> type is an algebraic enum. If a function can fail, it <em>must</em> return a <code>Result</code>. The compiler forces the caller to explicitly handle both the <code>Ok</code> and the <code>Err</code> variant. Because errors are returned as standard data via the normal CPU registers, there is absolutely zero stack-unwinding overhead.</p>

    <h2>2. The `std::error::Error` Trait</h2>
    <p>While returning <code>Result&lt;T, String&gt;</code> is possible, it is a severe anti-pattern. An error string cannot be pattern-matched by the caller to execute recovery logic. We must return strongly typed error structs. To unify the ecosystem, Rust provides the <code>std::error::Error</code> trait.</p>
    <p>The <code>Error</code> trait is remarkably simple. It requires the struct to implement <code>Display</code> (so it can be printed to the user) and <code>Debug</code> (so it can be printed to the logs). Crucially, it provides a <code>source()</code> method. If a database error causes an HTTP error, the HTTP error struct can hold the database error inside it, forming a <strong>Chain of Errors</strong>.</p>

    <h2>3. Library vs. Application Errors (`thiserror` vs `eyre`)</h2>
    <p>A fatal mistake made by intermediate Rust developers is treating all errors the same. In reality, there is a strict architectural dichotomy between <strong>Library Errors</strong> and <strong>Application Errors</strong>.</p>
    
    <h3>3.1 Library Errors (`thiserror`)</h3>
    <p>If you are writing a reusable library (like the <code>domain</code> crate in our Hexagonal Workspace), you must define exact, exhaustive error enums. The caller needs to know exactly what failed so they can mathematically pattern-match and recover (e.g., <code>DomainError::UserNotFound</code> vs <code>DomainError::DatabaseTimeout</code>).</p>
    <p>We use the <code>thiserror</code> crate to automate the boilerplate of implementing the <code>std::error::Error</code> trait for our enums. <code>thiserror</code> generates purely static, zero-allocation code. It is an absolute requirement for library boundaries.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/domain/error.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">thiserror</span>::<span class="type">Error</span>;

<span class="attr">#[derive(Error, Debug)]</span>
<span class="kw">pub enum</span> <span class="type">DomainError</span> {
    <span class="attr">#[error(<span class="str">"User with ID {0} was not found in the system"</span>)]</span>
    UserNotFound(<span class="type">uuid</span>::<span class="type">Uuid</span>),
    
    <span class="cmt">// Using #[source] automatically links the inner sqlx::Error into the Error chain</span>
    <span class="attr">#[error(<span class="str">"A fatal database timeout occurred"</span>)]</span>
    DatabaseTimeout(<span class="attr">#[from]</span> <span class="attr">#[source]</span> <span class="type">sqlx</span>::<span class="type">Error</span>),
}</pre></div>

    <h3>3.2 Application Errors (`eyre` and Dynamic Dispatch)</h3>
    <p>At the highest level of your application (the Composition Root or the Axum HTTP Handlers), you do not care about pattern matching. If the database times out while processing a web request, there is no "recovery"—you simply need to log the exact line of code that failed and return a 500 Internal Server Error to the user.</p>
    <p>If you try to use enums at the application boundary, you will end up with a massive, 50-variant <code>ApiError</code> enum that encompasses every possible failure in the entire system. This is a maintenance nightmare.</p>
    <p>We solve this using the <strong>`eyre`</strong> crate and <strong>Dynamic Dispatch</strong>. Instead of returning a specific enum, our top-level functions return <code>eyre::Result&lt;T&gt;</code>. Under the hood, this is an alias for <code>Result&lt;T, eyre::Report&gt;</code>.</p>
    
    <h2>4. The Mathematics of Fat Pointers</h2>
    <p>What is an <code>eyre::Report</code>? It is a heap-allocated <strong>Fat Pointer</strong> to any struct that implements <code>std::error::Error</code> (i.e., <code>Box&lt;dyn Error&gt;</code>). When you return a <code>sqlx::Error</code> via the <code>?</code> operator, <code>eyre</code> intercepts it, dynamically allocates it on the heap, and returns a pointer.</p>
    <p>A standard pointer in Rust is 8 bytes (on a 64-bit system). A <em>Fat Pointer</em> is 16 bytes. The first 8 bytes point to the actual error struct on the heap. The second 8 bytes point to the <strong>vtable (Virtual Method Table)</strong>. The vtable is a static array of function pointers generated by the compiler. When you call <code>error.to_string()</code> on a <code>dyn Error</code>, the CPU jumps to the vtable, looks up the specific memory address of the <code>to_string</code> function for that specific underlying struct, and dynamically executes it.</p>
    <p>This dynamic dispatch incurs a microscopic CPU overhead (a pointer indirection), but in the context of an error path (which only happens during a failure), this cost is entirely irrelevant. The tradeoff gives us immense power: <code>eyre</code> automatically captures a full <strong>Stack Trace</strong> at the exact microsecond the error is created. When the error bubbles up to the Axum handler and is logged to our OpenTelemetry pipeline, it includes the exact filename and line number where the database query failed, providing unparalleled debuggability in production.</p>
</section>"""

pattern = r'<section class="chapter" id="errors">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay expansion applied to Chapter 09.")
