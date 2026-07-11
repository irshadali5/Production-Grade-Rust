import sys

with open('src/pages/index.astro', 'r') as f:
    content = f.read()

old_text = """<h1>Introduction</h1>

    <p>This book teaches you how to build <strong>production-grade backend services</strong> in Rust. Not toy examples. Not "Hello World." Real systems with databases, authentication, background workers, telemetry, and deployment pipelines.</p>"""

new_text = """<h1>Introduction</h1>

    <p>This book teaches you how to build <strong>production-grade backend services</strong> in Rust. Not toy examples. Not "Hello World." Real systems with databases, authentication, background workers, telemetry, and deployment pipelines.</p>

    <h2>About This Book</h2>
    <p><strong>What is this book?</strong> This is a comprehensive, hands-on guide that takes you from a blank directory to a fully deployed, production-ready Rust backend. We cover the entire lifecycle: local development, testing, architecture, deployment, and observability.</p>
    <p><strong>Why does this exist?</strong> While Rust has fantastic introductory material, there is often a gap when it comes to connecting all the pieces for a real-world web service. Many tutorials stop at "Hello World," leaving you to figure out how to structure a large project, handle database migrations, and trace distributed requests. This book bridges that gap by focusing purely on modern best practices and the 2026 crate ecosystem.</p>

    <h2>Prerequisites & Requirements</h2>
    <p><strong>What is required?</strong></p>
    <ul>
      <li>A basic understanding of Rust syntax (ownership, borrowing, enums, pattern matching).</li>
      <li>Familiarity with fundamental web concepts (HTTP APIs, REST).</li>
      <li>A working installation of <code>Rust (1.96+)</code>, <code>Docker</code>, and <code>PostgreSQL</code>.</li>
    </ul>
    <p><strong>Why are these required?</strong> We will not spend time explaining fundamental Rust concepts like the borrow checker or how lifetimes work. Our focus is squarely on architecture, scaling, and production patterns. Docker and PostgreSQL are required because we build a realistic data-driven service that accurately mirrors how modern tech companies deploy their infrastructure.</p>"""

content = content.replace(old_text, new_text)

with open('src/pages/index.astro', 'w') as f:
    f.write(content)

print("Added About and Requirements sections successfully.")
