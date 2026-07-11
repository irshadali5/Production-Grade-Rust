import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

# Replace main title in <title> tag
content = content.replace('<title>Zero to Production in Rust — 2026 Edition</title>', '<title>Production-Grade Rust — 2026 Edition</title>')

# Replace main H1 heading
content = content.replace('<h1>Zero to Production in Rust</h1>', '<h1>Production-Grade Rust</h1>')

with open(filepath, 'w') as f:
    f.write(content)

print("Title replaced successfully.")
