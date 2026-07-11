import fs from 'node:fs';
import path from 'node:path';

const dir = path.join(process.cwd(), 'src', 'content', 'chapters');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md') || f.endsWith('.mdx'));

const languages = ['rust', 'toml', 'json', 'bash', 'sh', 'yaml', 'sql', 'nix', 'yml', 'js', 'javascript', 'ts', 'typescript'];

for (const file of files) {
  const filePath = path.join(dir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let lines = content.split('\n');
  let newLines = [];
  let inCodeBlock = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    if (!inCodeBlock) {
      // Check if line looks like "src/main.rsrust" or "rust"
      let isCodeHeader = false;
      let langMatch = '';
      let fileMatch = '';

      // Skip lines that are too long to be a header or look like normal text (contain spaces, unless it's just spaces at end)
      const trimmed = line.trim();
      if (trimmed.length > 0 && trimmed.length < 100 && !trimmed.includes(' ')) {
        for (const lang of languages) {
          if (trimmed.endsWith(lang)) {
            langMatch = lang;
            fileMatch = trimmed.slice(0, -lang.length);
            isCodeHeader = true;
            break;
          }
        }
      }

      if (isCodeHeader) {
        inCodeBlock = true;
        // Output the start of the code block
        const filePart = fileMatch ? ` ${fileMatch}` : '';
        newLines.push(`\`\`\`${langMatch}${filePart}`);
      } else {
        newLines.push(line);
      }
    } else {
      // We are inside a code block.
      // A code block ends if we encounter a markdown header (##) or 
      // if there are multiple consecutive blank lines and the next non-blank line is not indented code and not ending in a bracket.
      // But looking at 04-chapter.md, there's `}` at the end of the code, then a newline, then `## 3. The Flaw...`
      // Let's use a simpler heuristic: if the line starts with `#` or if it's normal markdown text
      // Wait, normal markdown text is hard to detect. Let's look ahead.
      // Actually, if we see a line starting with `#` (a heading) or a line like `In standard web applications...`, we know it's not code.
      // What if we just look for a completely blank line followed by a non-blank line that does not look like code (e.g. starts with capital letter, no special characters)?
      // This is risky. Let's just restore from git? No, let's fix it by regex or let's write a smarter script.
      
      // Let's check if the line starts with a heading or if it's a known markdown paragraph start.
      // For the scope of this task, I'll close the code block if we hit a line that starts with `#` or starts with `By ` or `We ` or `This ` (common paragraph starters) preceded by a blank line.
      // Let's just use empty line followed by a line starting with a capital letter or `#`.
      
      // But wait! If we just write a script that adds ``` at the end of the file if still open, and closes it when it sees `##`, that might be enough for this particular broken format.
      // Actually, let's look at how the code ends in `04-chapter.md`:
      /*
      118: Ok((response.data, response.lease_duration))
      119: }
      120: 
      121: 
      122: 
      123: By combining LLVM-level memory zeroization...
      */
      
      if (line.trim() === '' && i + 1 < lines.length && lines[i+1].trim() === '' && i + 2 < lines.length && lines[i+2].trim() === '' && i + 3 < lines.length && lines[i+3].match(/^[A-Z#]/)) {
        // We found 3 blank lines followed by text starting with a capital letter or #
        newLines.push('```');
        newLines.push(line);
        inCodeBlock = false;
      } else if (line.match(/^#{1,6}\s/) || line.match(/^[A-Z][a-z]+ [a-z]+/)) {
          // Wait, if it's the very first blank line and we hit a capital letter right away, maybe it's text.
          // In 04-chapter.md, there are 3 blank lines.
          // Let's just check if the current line starts with `## ` or `### `
          if (line.match(/^#{1,6}\s/)) {
            // we missed the end, let's put it before the heading
            newLines.push('```');
            newLines.push('');
            newLines.push(line);
            inCodeBlock = false;
          } else {
             newLines.push(line);
          }
      } else {
        newLines.push(line);
      }
    }
  }

  if (inCodeBlock) {
    newLines.push('```');
  }

  fs.writeFileSync(filePath, newLines.join('\n'));
}

console.log('Fixed code blocks');
