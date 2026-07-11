import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="graphql">
    <div class="chapter-label">Chapter 27</div>
    <h1>Intensive Deep Dive: The N+1 Problem & Asynchronous Dataloaders</h1>

    <h2>1. The Physics of Graph Traversal</h2>
    <p>GraphQL is profoundly misunderstood as a simple alternative to REST. It is actually a powerful AST execution engine. When a client sends a query like <code>query { users(limit: 100) { id, posts { title } } }</code>, the server parses this string into an Abstract Syntax Tree (AST). The GraphQL execution engine then traverses this tree recursively, invoking specific Rust functions (Resolvers) at every node.</p>

    <h2>2. The N+1 Catastrophe</h2>
    <p>This recursive traversal introduces the most devastating performance bottleneck in web architecture: <strong>The N+1 Query Problem</strong>. The engine first executes the <code>users</code> resolver, which executes 1 SQL query to fetch 100 users. The engine then iterates over those 100 users. For <em>every single user</em>, it invokes the <code>posts</code> resolver.</p>
    <p>If the <code>posts</code> resolver executes a standard SQL query (<code>SELECT * FROM posts WHERE user_id = $1</code>), the server will execute 100 separate, sequential SQL queries. If the query requested comments on those posts, it would trigger 10,000 queries. A single HTTP request will instantly exhaust the Postgres connection pool and crash the database.</p>

    <h2>3. The Dataloader Batching Algorithm</h2>
    <p>We eliminate the N+1 problem mathematically using the <strong>Dataloader Pattern</strong>. A Dataloader acts as an asynchronous queue and deduplicator. When the 100 <code>posts</code> resolvers are invoked, they do <strong>not</strong> execute SQL queries. Instead, each resolver pushes its <code>user_id</code> into the Dataloader's memory queue and immediately returns a <code>Future</code>.</p>
    <p>Because Rust is asynchronous, the Tokio executor pauses all 100 resolvers. At the end of the current micro-task tick (when the executor runs out of immediate work), the Dataloader looks at its queue. It finds 100 <code>user_id</code>s. It deduplicates them, and executes a <strong>single</strong> batch SQL query: <code>SELECT * FROM posts WHERE user_id = ANY($1)</code>.</p>
    <p>When Postgres returns the massive array of posts, the Dataloader sorts them into memory and pushes the results back into the 100 paused Futures, waking them up. By exploiting the mechanics of the Tokio event loop, we compress 10,000 recursive database queries into exactly 3 batch queries, achieving O(1) performance scalability regardless of graph depth.</p>
</section>"""

pattern = r'<section class="chapter" id="graphql">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 27 applied.")
