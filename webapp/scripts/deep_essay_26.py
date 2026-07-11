import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="openapi">
    <div class="chapter-label">Chapter 26</div>
    <h1>Intensive Deep Dive: AST Macros & Compile-Time OpenAPI</h1>

    <h2>1. The Disconnect Between Code and Documentation</h2>
    <p>In legacy API development, engineers manually write Swagger (OpenAPI) YAML documentation. This guarantees a fatal desynchronization. A developer will change a database column from a 32-bit integer to a 64-bit integer in the Rust code, but forget to update the YAML file. The iOS and React teams, relying on the Swagger file to generate their SDKs, will compile their clients expecting a 32-bit integer. When the 64-bit payload arrives in production, the iOS app suffers a fatal deserialization panic and crashes.</p>

    <h2>2. AST Reflection via Procedural Macros</h2>
    <p>We eliminate this mathematically by binding the documentation directly to the Rust Abstract Syntax Tree (AST) using the <code>utoipa</code> crate.</p>
    <p>We attach the <code>#[derive(ToSchema)]</code> procedural macro to our Rust structs. During compilation, before the binary is even generated, the macro intercepts the compiler's AST. It recursively analyzes the memory layout and types of the struct. If a field is defined as <code>email: Option&lt;String&gt;</code>, the macro uses Rust's type system to mathematically deduce that the OpenAPI JSON Schema field must be marked as <code>type: "string"</code> and <code>nullable: true</code>.</p>

    <h2>3. The Zero-Maintenance API Contract</h2>
    <p>If a developer changes the <code>email</code> field to a custom <code>EmailAddress</code> Newtype, the compiler automatically updates the generated JSON Schema to reflect the new validation rules. If the developer adds a new route to the Axum router but forgets to add the <code>#[utoipa::path]</code> macro, the compiler throws a warning.</p>
    <p>This creates a mathematically perfect, self-updating API contract. We serve this generated JSON Schema at the <code>/api-docs/openapi.json</code> endpoint. The frontend teams use <code>openapi-generator</code> to pull this JSON and auto-generate type-safe TypeScript and Swift SDKs. By elevating API documentation to a compile-time AST artifact, we guarantee that the frontend and backend are always in perfect cryptographic synchronization.</p>
</section>"""

pattern = r'<section class="chapter" id="openapi">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 26 applied.")
