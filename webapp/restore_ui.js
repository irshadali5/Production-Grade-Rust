const fs = require('fs');

const oldHtml = fs.readFileSync('old_ui.html', 'utf8');

// Extract CSS
const styleMatch = oldHtml.match(/<style is:global>([\s\S]*?)<\/style>/);
const css = styleMatch ? styleMatch[1] : '';

// Extract JS
// The last script block is the Single Chapter View Logic
const scripts = oldHtml.match(/<script>([\s\S]*?)<\/script>/g);
const navigationScript = scripts ? scripts[scripts.length - 1] : '';

const newAstroContent = `---
import { getCollection, render } from 'astro:content';

const allChapters = await getCollection('chapters');
const sortedChapters = allChapters.sort((a, b) => a.data.order - b.data.order);
---

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Production-Grade Rust — 2026 Edition</title>
    <style is:global>${css}</style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>Production-Grade Rust</h1>
            <div class="version">Hyperscale Architecture</div>
            <div class="rust-badge">2026 Edition</div>
        </div>
        <div class="nav-section">
            <div class="nav-section-title">Chapters</div>
            {sortedChapters.map(chapter => (
                <a href={\`#chapter-\${chapter.data.order}\`} class="nav-item">
                    <span class="chapter-num">{chapter.data.order.toString().padStart(2, '0')}</span>
                    {chapter.data.title}
                </a>
            ))}
        </div>
    </div>

    <div class="main">
        {sortedChapters.map(async (chapter) => {
            const { Content } = await render(chapter);
            return (
                <section class="chapter" id={\`chapter-\${chapter.data.order}\`}>
                    <div class="chapter-label">Chapter {chapter.data.order.toString().padStart(2, '0')}</div>
                    <Content />
                </section>
            );
        })}
    </div>

${navigationScript}
</body>
</html>
`;

fs.writeFileSync('src/pages/index.astro', newAstroContent);
console.log('Restored old UI design to index.astro');
