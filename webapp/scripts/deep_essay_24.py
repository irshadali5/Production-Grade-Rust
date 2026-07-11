import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="wasm">
    <div class="chapter-label">Chapter 24</div>
    <h1>Intensive Deep Dive: WASI & Capability-Based Virtual Machines</h1>

    <h2>1. The Danger of Untrusted Plugin Architectures</h2>
    <p>If you build an extensible platform (like an API Gateway or a Serverless edge router) that allows third-party developers to upload custom logic, executing that logic natively is a massive security vulnerability. If you execute a user's Python or Lua script directly, they can use <code>os.system('cat /etc/passwd')</code> to steal system configuration, or they can open a raw TCP socket and exfiltrate your internal database credentials.</p>
    <p>Using Docker containers for these plugins is too slow and heavy, requiring hundreds of megabytes of RAM and seconds to boot.</p>

    <h2>2. WebAssembly System Interface (WASI)</h2>
    <p>We solve this by requiring users to upload WebAssembly (WASM) modules. We execute these modules directly inside our Rust server using the <code>wasmtime</code> runtime. A raw WASM module is a pure mathematical sandbox. It has absolutely zero ability to interact with the outside world; it cannot read files, open network sockets, or even read the system clock.</p>
    <p>To allow the plugin to perform useful work, we implement the <strong>WebAssembly System Interface (WASI)</strong>. WASI defines a standardized set of system calls (like <code>fd_read</code> or <code>random_get</code>) that the WASM module can call. However, when the WASM module executes these calls, they do not hit the Linux OS kernel. They are intercepted by the <code>wasmtime</code> runtime running securely in our Rust host.</p>

    <h2>3. Capability-Based Sandboxing</h2>
    <p>This interception layer allows us to implement <strong>Capability-Based Security</strong>. By default, the WASM plugin has zero capabilities. If the plugin attempts to open <code>/etc/passwd</code>, the <code>wasmtime</code> interceptor instantly denies the request and returns an error.</p>
    <p>The Rust host must explicitly grant the WASM module a specific "Capability." For example, the Rust host can grant a file descriptor pointing <em>only</em> to a specific virtual directory like <code>/tmp/plugin_123_data/</code>. When the WASM module calls <code>fd_read("/")</code>, it believes it is reading the root of the operating system, but it is actually trapped inside a virtualized, chroot-like filesystem mapped to that specific temporary folder.</p>
    <p>If the plugin suffers a memory corruption bug (like a buffer overflow) due to poorly written C++ code, the damage is strictly confined to the WASM Linear Memory. The Rust host memory remains completely untouched. This mathematically proven isolation allows us to safely execute untrusted third-party code directly within our core API at near-native speeds, achieving a level of security that Linux containers can never match.</p>
</section>"""

pattern = r'<section class="chapter" id="wasm">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 24 applied.")
