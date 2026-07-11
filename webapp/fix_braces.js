const fs = require('fs');
const path = require('path');
const dir = path.join(process.cwd(), 'src', 'content', 'chapters');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md') || f.endsWith('.mdx'));

for (const file of files) {
  const filePath = path.join(dir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let lines = content.split('\n');
  let newLines = [];
  let inCodeBlock = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    
    // Skip frontmatter
    if (i < 10 && line.startsWith('---')) {
      newLines.push(line);
      continue;
    }
    // We don't want to mess with frontmatter body, but it has no { } usually

    if (line.startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      newLines.push(line);
      continue;
    }

    if (!inCodeBlock) {
      // Very naive: replace { and } with their HTML entities.
      // But we shouldn't replace it if it's already an HTML entity.
      line = line.replace(/\{/g, '&#123;');
      line = line.replace(/\}/g, '&#125;');
    }
    
    newLines.push(line);
  }

  fs.writeFileSync(filePath, newLines.join('\n'));
}
console.log("Fixed braces");
