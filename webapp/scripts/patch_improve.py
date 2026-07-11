import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

# 1. Strip the exhaustive appendix from all chapters
content = re.sub(r'<div class="exhaustive-appendix".*?(</section>)', r'\1', content, flags=re.DOTALL)

# 2. Add Summary & Next Steps to Chapter 00
summary_html = """
    <h2>Summary & Next Steps</h2>
    <p>By now, you should have a firm understanding of <em>why</em> we are building this project and the high-level architecture we will employ.</p>
    <div class="callout info">
      <div class="callout-title">The Journey Ahead</div>
      <p>In the next chapter, we will roll up our sleeves and prepare our development environment. We will install the latest Rust compiler, set up our database tooling, and configure our IDEs for maximum productivity. Brace yourself—production Rust is demanding, but incredibly rewarding.</p>
    </div>
"""

# Insert right before the first </section> which belongs to Chapter 00
first_section_end = content.find('</section>')
if first_section_end != -1:
    content = content[:first_section_end] + summary_html + content[first_section_end:]

with open(filepath, 'w') as f:
    f.write(content)

print("Content improvement patch applied successfully.")
