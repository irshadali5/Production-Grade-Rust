import re

filepath = 'src/pages/index.astro'

new_sidebar = """<aside class="sidebar">
  <div class="sidebar-header">
    <h1>⚡ PRODUCTION-GRADE RUST</h1>
    <div class="version">2026 Edition • v1.0</div>
    <span class="rust-badge">RUST 1.96.0</span>
    <div class="progress"><div class="progress-fill"></div></div>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 1: Foundations</div>
    <a href="#intro" class="nav-item active"><span class="chapter-num">00</span>Introduction</a>
    <a href="#setup" class="nav-item"><span class="chapter-num">01</span>Toolchain & Setup</a>
    <a href="#project" class="nav-item"><span class="chapter-num">02</span>Project Structure</a>
    <a href="#axum" class="nav-item"><span class="chapter-num">03</span>Axum Web Framework</a>
    <a href="#config" class="nav-item"><span class="chapter-num">04</span>Configuration</a>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 2: Core Engineering</div>
    <a href="#database" class="nav-item"><span class="chapter-num">05</span>SQLx & Postgres</a>
    <a href="#telemetry" class="nav-item"><span class="chapter-num">06</span>Telemetry & Tracing</a>
    <a href="#errors" class="nav-item"><span class="chapter-num">07</span>Error Handling</a>
    <a href="#validation" class="nav-item"><span class="chapter-num">08</span>Validation & Types</a>
    <a href="#email" class="nav-item"><span class="chapter-num">09</span>Email Client</a>
    <a href="#testing" class="nav-item"><span class="chapter-num">10</span>Testing Strategies</a>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 3: Production Systems</div>
    <a href="#auth" class="nav-item"><span class="chapter-num">11</span>Authentication</a>
    <a href="#workers" class="nav-item"><span class="chapter-num">12</span>Background Workers</a>
    <a href="#deploy" class="nav-item"><span class="chapter-num">13</span>Deployment</a>
    <a href="#stack" class="nav-item"><span class="chapter-num">14</span>Full Stack Reference</a>
    <a href="#reliability" class="nav-item"><span class="chapter-num">16</span>Reliability & Limits</a>
    <a href="#caching" class="nav-item"><span class="chapter-num">17</span>Caching & HA</a>
    <a href="#websockets" class="nav-item"><span class="chapter-num">18</span>Real-time WebSockets</a>
    <a href="#qol" class="nav-item"><span class="chapter-num">19</span>Quality of Life</a>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 4: AI & Applied Data</div>
    <a href="#ai" class="nav-item"><span class="chapter-num">15</span>AI Integration</a>
    <a href="#llm-gateway" class="nav-item"><span class="chapter-num">20</span>LLM Gateway</a>
    <a href="#rag" class="nav-item"><span class="chapter-num">21</span>RAG & pgvector</a>
    <a href="#async-internals" class="nav-item"><span class="chapter-num">22</span>GATs & Async</a>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 5: Advanced Interfaces</div>
    <a href="#security" class="nav-item"><span class="chapter-num">23</span>Security & PKCE</a>
    <a href="#wasm" class="nav-item"><span class="chapter-num">24</span>Frontend & WASM</a>
    <a href="#openapi" class="nav-item"><span class="chapter-num">26</span>OpenAPI Spec</a>
    <a href="#graphql" class="nav-item"><span class="chapter-num">27</span>GraphQL</a>
  </div>

  <div class="nav-section">
    <div class="nav-section-title">Unit 6: Hyperscale Operations</div>
    <a href="#infrastructure" class="nav-item"><span class="chapter-num">25</span>Infrastructure (IaC)</a>
    <a href="#kubernetes" class="nav-item"><span class="chapter-num">28</span>Kubernetes Helm</a>
    <a href="#benchmarking" class="nav-item"><span class="chapter-num">29</span>Load Testing</a>
    <a href="#ebpf" class="nav-item"><span class="chapter-num">30</span>eBPF Profiling</a>
    <a href="#firecracker" class="nav-item"><span class="chapter-num">31</span>Firecracker VMs</a>
    <a href="#io-uring" class="nav-item"><span class="chapter-num">32</span>io_uring</a>
  </div>
</aside>"""

with open(filepath, 'r') as f:
    content = f.read()

# Replace the entire sidebar block
pattern = r'<aside class="sidebar">.*?</aside>'
content = re.sub(pattern, new_sidebar, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Sidebar reorganized into official Units.")
