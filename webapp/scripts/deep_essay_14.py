import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="stack">
    <div class="chapter-label">Chapter 14</div>
    <h1>Intensive Deep Dive: V8 JIT Bailouts & WASM Pointer Passing</h1>

    <h2>1. The Catastrophe of JIT De-optimization</h2>
    <p>When building a full-stack architecture using a Node.js rendering layer (like Astro or Next.js), developers often fall into the trap of performing heavy CPU tasks in JavaScript (e.g., parsing massive Markdown files or executing complex cryptographic hashes). This is fundamentally flawed due to the physics of the V8 JavaScript engine.</p>
    <p>Because JavaScript is dynamically typed, V8 utilizes a Just-In-Time (JIT) compiler. When V8 executes a function, it observes the types of the arguments. If it sees that a function is repeatedly called with integers, the TurboFan optimizer generates highly efficient native machine code tailored specifically for integers. However, if the 100,000th request maliciously sends a floating-point number instead, the machine code becomes mathematically invalid. V8 suffers a <strong>Bailout (De-optimization)</strong>. It violently halts execution, discards the machine code, and falls back to the slow interpreter. In a hyperscale API, these unpredictable JIT bailouts cause massive, unacceptable spikes in p99 tail latency.</p>

    <h2>2. Deterministic Execution via WebAssembly (WASM)</h2>
    <p>We eliminate JIT volatility entirely by offloading all intensive computation to <strong>WebAssembly (WASM)</strong>. We compile our core Rust logic (such as our custom Markdown parser) into the <code>wasm32-unknown-unknown</code> target.</p>
    <p>WebAssembly is a statically typed, low-level bytecode. When V8 receives the WASM module, it performs a single, highly efficient streaming compilation pass (Liftoff). It does not guess types. It does not perform speculative profiling. It translates the WASM directly into optimized native machine code. The resulting execution speed is mathematically constant, completely eliminating JIT bailouts and guaranteeing perfectly flat tail latency.</p>

    <h2>3. The Foreign Function Interface (FFI) Bottleneck</h2>
    <p>However, integrating WASM introduces the deadliest bottleneck in frontend engineering: The Foreign Function Interface (FFI) boundary. A WASM module is a complete mathematical sandbox. It executes inside a flat, isolated block of memory known as <strong>Linear Memory</strong>. It has absolutely zero access to the Node.js V8 heap, and Node.js cannot directly read WASM variables.</p>
    <p>The naive approach to passing data (used by 99% of libraries) is disastrous. If Node.js needs the WASM module to parse a 20MB Markdown string, Node.js must allocate 20MB of space inside the WASM Linear Memory, copy the string byte-by-byte across the FFI boundary, execute the parser, allocate another 20MB for the HTML output, and copy it back to the V8 heap. This extreme memory serialization and copying destroys the CPU, making the WASM implementation significantly slower than pure JavaScript.</p>

    <h2>4. Zero-Copy Pointer Arithmetics via `wasm-bindgen`</h2>
    <p>To achieve true expert-level performance, we bypass copying entirely using the <code>wasm-bindgen</code> crate and raw pointer arithmetic. When Node.js has a massive 20MB string, it does not pass the string across the boundary.</p>
    <p>Instead, Node.js calls a Rust WASM function that executes <code>alloc</code> to reserve 20MB of raw bytes inside the Linear Memory. The Rust function returns the <strong>raw memory pointer (<code>*mut u8</code>)</strong> back to Node.js. Node.js then creates a <code>Uint8Array</code> view in JavaScript that perfectly overlaps with that specific physical memory address inside the WASM <code>ArrayBuffer</code>.</p>
    <p>Node.js writes the 20MB string directly into the WASM memory space. When Node.js invokes the WASM parser, it simply passes the memory pointer (a single 32-bit integer). The Rust code instantly executes against the memory with zero serialization, zero copying, and zero GC overhead, achieving C-level execution speeds directly inside the JavaScript runtime.</p>
</section>"""

pattern = r'<section class="chapter" id="stack">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 14 applied.")
