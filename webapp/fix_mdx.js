const fs = require('fs');
const glob = require('fs').readdirSync;
const path = require('path');

const dir = path.join(__dirname, 'src', 'content', 'chapters');
const files = glob(dir).filter(f => f.endsWith('.mdx'));

for (const file of files) {
    if (file.includes('01-') || file.includes('02-') || file.includes('03-')) continue;
    
    const filePath = path.join(dir, file);
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Save frontmatter
    const fmMatch = content.match(/---[\s\S]*?---/);
    const fm = fmMatch ? fmMatch[0] : '';
    let body = content.replace(/---[\s\S]*?---/, '');
    
    // Remove span tags completely
    body = body.replace(/<span[^>]*>|<\/span>/g, '');
    
    // Convert strong, code, em
    body = body.replace(/<strong>/g, '**').replace(/<\/strong>/g, '**');
    body = body.replace(/<code>/g, '`').replace(/<\/code>/g, '`');
    body = body.replace(/<em>/g, '*').replace(/<\/em>/g, '*');
    
    // Convert headings
    body = body.replace(/<h1>(.*?)<\/h1>/g, '# $1\n');
    body = body.replace(/<h2>(.*?)<\/h2>/g, '## $1\n');
    body = body.replace(/<h3>(.*?)<\/h3>/g, '### $1\n');
    
    // Convert paragraphs
    body = body.replace(/<p>/g, '\n\n').replace(/<\/p>/g, '');
    
    // Convert ul/li
    body = body.replace(/<ul>/g, '\n').replace(/<\/ul>/g, '\n');
    body = body.replace(/<li>(.*?)<\/li>/g, '- $1');
    
    // Convert blockquotes (if any)
    body = body.replace(/<blockquote>/g, '\n> ').replace(/<\/blockquote>/g, '\n');
    
    // Remove any leftover div/pre (since we converted code blocks in the previous step!)
    // Wait, the previous step converted them to ```rust ... ```, so there shouldn't be <div class="code-block"> anymore.
    body = body.replace(/<\/?div[^>]*>/g, '');
    body = body.replace(/<\/?pre[^>]*>/g, '');
    
    // Fix escaped chars inside markdown
    body = body.replace(/&#123;/g, '{').replace(/&#125;/g, '}');
    body = body.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');

    // Re-write file
    fs.writeFileSync(filePath, fm + '\n' + body);
}
console.log('Conversion complete.');
