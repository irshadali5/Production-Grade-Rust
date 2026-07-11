import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="ai">
    <div class="chapter-label">Chapter 15</div>
    <h1>Intensive Deep Dive: Logit Masking & AI Structured Generation</h1>

    <h2>1. The Fallacy of Prompt Engineering</h2>
    <p>When integrating Large Language Models (LLMs) into a production system, junior developers attempt to extract structured data (like JSON or CSV) using "Prompt Engineering." They will append strings like <code>"Please return ONLY valid JSON without markdown backticks."</code> to the system prompt. This is a fatal architectural error.</p>
    <p>An LLM is not a deterministic state machine; it is a massive probabilistic neural network. It calculates the statistical likelihood of the next token based on its training weights. There is always a non-zero mathematical probability that the model will output a trailing comma, an unescaped quote, or a hallucinated key. If you pipe this probabilistic text directly into a strict Rust JSON parser like <code>serde_json</code>, your application will violently panic in production.</p>

    <h2>2. Deterministic Structured Generation</h2>
    <p>We eliminate this failure mode entirely using <strong>Structured Generation</strong> (e.g., OpenAI's <code>json_schema</code> or open-source equivalents like Guidance/Outlines). We stop asking the model nicely. Instead, we use mathematical constraints to physically alter the neural network's internal generation engine.</p>
    <p>In Rust, we define the exact desired output format as a struct: <code>struct AiResponse { confidence: f32, entities: Vec&lt;String&gt; }</code>. Using the <code>schemars</code> crate, the Rust compiler analyzes this struct at compile-time and generates a mathematically rigorous JSON Schema. We inject this Schema directly into the LLM API request payload.</p>

    <h2>3. The Physics of Logit Masking</h2>
    <p>When the LLM inference engine receives the JSON Schema, it alters how it calculates token probabilities (logits). As the neural network predicts the next token, the inference engine applies a real-time mathematical mask to the output vector.</p>
    <p>If the JSON Schema dictates that the next character <em>must</em> be a floating-point number (for the <code>confidence</code> field), the inference engine intercepts the probability distribution. It multiplies the logits of every token that represents a letter (A-Z) or a special symbol by negative infinity. The probability of outputting an invalid token is physically crushed to absolute zero.</p>
    <p>Because the invalid tokens are mathematically erased from existence before the sampling phase, the model is physically forced to output a valid number. By utilizing Logit Masking, we guarantee with 100% mathematical certainty that the string returned by the LLM will map flawlessly to our Rust struct via <code>serde_json::from_str</code>. We have successfully converted a probabilistic AI model into a perfectly deterministic, type-safe function.</p>
</section>"""

pattern = r'<section class="chapter" id="ai">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 15 applied.")
