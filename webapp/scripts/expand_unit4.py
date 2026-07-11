import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    "ai": """<section class="chapter" id="ai">
    <div class="chapter-label">Chapter 15</div>
    <h1>AI Agents: Structured Generation (Instructor)</h1>

    <h2>The Fragility of Prompt Engineering</h2>
    <p>The standard approach to building LLM applications is to use Prompt Engineering: instructing the model via natural language to return data in a specific format. You might append "Return only valid JSON" to your prompt. However, LLMs are probabilistic text generators. At any moment, the model might prefix the JSON with "Here is your data:" or hallucinate a trailing comma, instantly crashing your JSON deserializer (like `serde_json`). Relying on probabilistic compliance in a deterministic production pipeline is a catastrophic architectural flaw.</p>

    <h2>Structured Generation via JSON Schema</h2>
    <p>To integrate AI into a production Rust backend, we must force the LLM into deterministic compliance. We achieve this using <strong>Structured Generation</strong>, heavily inspired by the `instructor` library pattern in Python, but implemented securely in Rust.</p>
    <p>Modern LLM APIs (like OpenAI's `gpt-4o`) support a feature called `json_schema` or "Tool Calling". Instead of asking the model nicely to return JSON, we define our Rust data structure (e.g., `pub struct UserProfile`) and use the `schemars` crate to automatically generate a strict JSON Schema at compile time. We pass this mathematical schema directly into the LLM API request.</p>

    <h2>Logit Bias and Token Masking</h2>
    <p>When the LLM receives a strict JSON Schema, it alters its internal generation engine. During the generation of the next token, the API applies a mathematical mask to the output logits (the probabilities of the next word). If the JSON Schema requires an integer, the logits for any token that is a letter (A-Z) are multiplied by negative infinity. The model is literally, mathematically forced to output a number. This guarantees that the string returned by the LLM will map flawlessly to your Rust struct via `serde_json::from_str`, completely eliminating runtime parsing panics.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/ai.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="kw">use</span> <span class="type">schemars</span>::<span class="type">JsonSchema</span>;
<span class="kw">use</span> <span class="type">serde</span>::{<span class="type">Deserialize</span>, <span class="type">Serialize</span>};

<span class="attr">#[derive(Debug, Serialize, Deserialize, JsonSchema)]</span>
<span class="kw">pub struct</span> <span class="type">ExtractionResult</span> {
    <span class="kw">pub</span> confidence_score: <span class="type">f32</span>,
    <span class="kw">pub</span> extracted_entities: <span class="type">Vec</span>&lt;<span class="type">String</span>&gt;,
}
<span class="cmt">// The generated schema is passed to OpenAI, forcing the output</span>
<span class="cmt">// to match this struct with 100% mathematical certainty.</span></pre></div>
</section>""",

    "llm-gateway": """<section class="chapter" id="llm-gateway">
    <div class="chapter-label">Chapter 20</div>
    <h1>LLM Gateway: Semantic Routing & Fallbacks</h1>

    <h2>The Danger of Vendor Lock-in</h2>
    <p>Building an AI product tightly coupled to a single vendor (like OpenAI) is extremely dangerous. If the `gpt-4o` API experiences an outage, your entire application goes down. Furthermore, using a massive, expensive model for simple tasks (like sentiment analysis) rapidly burns through your capital. To build a resilient, cost-effective AI architecture, you must implement an <strong>LLM Gateway</strong>.</p>
    <p>An LLM Gateway is a reverse proxy (built in Rust using Axum and `reqwest`) that sits between your core application and the external AI vendors. Your application sends a generic request to your Gateway. The Gateway is responsible for dynamically routing the request to the optimal model.</p>

    <h2>Semantic Routing</h2>
    <p>Instead of hardcoding route logic, the Gateway performs <strong>Semantic Routing</strong>. When a prompt arrives, the Gateway computes a fast embedding vector (using a small, local model like `all-MiniLM-L6-v2` loaded into memory via `candle` or `ort`). It compares this vector against known semantic clusters.</p>
    <p>If the prompt is mathematically close to the "simple_query" cluster (e.g., "summarize this text"), the Gateway dynamically routes the request to a cheap, fast model like `claude-3-haiku` or an open-source `Llama-3` instance. If the prompt is complex (e.g., "write a Rust macro"), it routes to `gpt-4o`. This dynamic routing can reduce API costs by up to 80% without sacrificing perceived intelligence.</p>

    <h2>Circuit Breaking and Fallbacks</h2>
    <p>Crucially, the LLM Gateway implements the Circuit Breaker pattern (discussed in Chapter 16). If the OpenAI API begins returning 502 Bad Gateway errors, the Circuit Breaker trips open. The Gateway instantly intercepts the failure and silently reroutes the request to Anthropic's `claude-3.5-sonnet` as a fallback. The end-user experiences a slight latency bump instead of a catastrophic failure, guaranteeing 99.99% AI uptime.</p>
</section>""",

    "rag": """<section class="chapter" id="rag">
    <div class="chapter-label">Chapter 21</div>
    <h1>RAG & pgvector: HNSW and SIMD</h1>

    <h2>The Context Window Bottleneck</h2>
    <p>Large Language Models are frozen in time; they cannot access your company's proprietary data. While you could theoretically stuff your entire internal wiki into the prompt's context window, this is prohibitively expensive (costing dollars per query) and severely degrades the model's reasoning capabilities (the "Lost in the Middle" phenomenon). The industry standard solution is Retrieval-Augmented Generation (RAG).</p>
    
    <h2>Vector Embeddings and Cosine Similarity</h2>
    <p>In a RAG architecture, we convert our proprietary documents into <strong>Vector Embeddings</strong>—high-dimensional arrays of floating-point numbers (e.g., 1536 dimensions for OpenAI). These vectors capture the semantic meaning of the text. When a user asks a question, we embed the question into a vector and search our database for the documents with the closest mathematical proximity, typically calculated using <strong>Cosine Similarity</strong>.</p>

    <h2>Postgres as a Vector Database (pgvector)</h2>
    <p>Instead of deploying a dedicated, complex Vector Database (like Pinecone or Milvus), we leverage our existing robust Postgres infrastructure by installing the <strong>pgvector</strong> extension. This allows us to store our 1536-dimensional embeddings directly alongside our relational data in `sqlx`.</p>

    <h2>HNSW Indexes and SIMD Acceleration</h2>
    <p>Performing an exact nearest-neighbor search (comparing the query vector against every single document in a 10-million row table) requires scanning the entire disk, resulting in O(N) complexity and seconds of latency. To achieve millisecond response times, we must build an index.</p>
    <p>We use the <strong>Hierarchical Navigable Small World (HNSW)</strong> index provided by `pgvector`. HNSW is a multi-layered graph algorithm that performs an Approximate Nearest Neighbor (ANN) search. By traversing a mathematical graph structure, it achieves O(log N) lookup times. Furthermore, when the CPU calculates the distance between vectors, it utilizes <strong>SIMD (Single Instruction, Multiple Data)</strong> instructions (like AVX-512). SIMD allows the CPU to calculate the cosine similarity of 16 floating-point dimensions simultaneously in a single clock cycle, providing massive computational acceleration.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">src/rag.rs</span><span class="code-lang">rust</span></div>
    <pre><span class="cmt">// Using sqlx to query the HNSW index in pgvector</span>
<span class="kw">let</span> documents = <span class="mac">sqlx::query!</span>(
    <span class="str">"SELECT content FROM documents ORDER BY embedding &lt;=&gt; $1 LIMIT 5"</span>,
    query_embedding <span class="cmt">// The 1536-dimensional vector</span>
).<span class="fn">fetch_all</span>(&amp;pool).<span class="kw">await</span>?;</pre></div>
</section>""",

    "async-internals": """<section class="chapter" id="async-internals">
    <div class="chapter-label">Chapter 22</div>
    <h1>Async Internals: GATs & State Machines</h1>

    <h2>The Illusion of Asynchronous Code</h2>
    <p>When you write an `async fn` in Rust and use the `.await` keyword, it feels like standard sequential programming. However, at the operating system level, true asynchronous execution does not look like this. The operating system only understands threads, network sockets, and hardware interrupts (like `epoll` or `kqueue`). The `async/await` syntax in Rust is a massive compiler illusion.</p>

    <h2>Desugaring to State Machines</h2>
    <p>Under the hood, the Rust compiler performs an extreme AST transformation. When it encounters an `async fn`, it does not generate a standard function. It generates an anonymous `enum` that represents a <strong>Finite State Machine (FSM)</strong>.</p>
    <p>Every time you write `.await`, the compiler creates a new state (a variant in the enum). All local variables across the `.await` point are aggressively packed into the enum's memory layout. This is why you often see errors about traits not being `Send`: if a variable is held across an `.await` point, it is embedded into the State Machine enum. If that variable cannot be safely sent across threads (like an `Rc`), the entire State Machine becomes `!Send`, and Tokio will refuse to spawn it on a multi-threaded executor.</p>

    <h2>The Executor (Tokio) and the Waker</h2>
    <p>The State Machine implements the `Future` trait, which requires a `poll` method. When you spawn a task on Tokio, Tokio places this State Machine onto a run queue. A worker thread pops the State Machine and calls `poll`. If the network socket is not ready, `poll` returns `Poll::Pending`.</p>
    <p>Crucially, before returning `Pending`, the Future registers a <strong>Waker</strong> with the operating system's `epoll` instance. The Tokio worker thread then immediately grabs the next State Machine from the queue, achieving massive concurrency on a single core. When the network hardware receives the packet, it triggers the Waker, and Tokio puts the State Machine back on the run queue to resume execution from its exact suspended state.</p>

    <h2>Generic Associated Types (GATs)</h2>
    <p>Advanced trait implementations in an asynchronous context often require yielding references tied to the lifetime of the `self` parameter. Prior to Rust 1.65, this was impossible in abstract traits. The introduction of <strong>Generic Associated Types (GATs)</strong> allows us to define associated types with their own lifetimes (e.g., `type Future&lt;'a&gt;: Future&lt;Output = ()&gt; + 'a;`). This breakthrough enables us to write highly zero-cost, zero-allocation asynchronous traits that abstract over network streams without boxing the futures on the heap.</p>
</section>"""
}

for chapter_id, replacement_html in replacements.items():
    pattern = rf'<section class="chapter" id="{chapter_id}">.*?</section>'
    content = re.sub(pattern, replacement_html, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Massive textual expansion applied to Unit 4 (AI & Applied Data).")
