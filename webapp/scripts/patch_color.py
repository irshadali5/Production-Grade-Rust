import sys

with open('src/pages/index.astro', 'r') as f:
    content = f.read()

highlight_fn = """
function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {
        let cls = 'num';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'type';
            } else {
                cls = 'str';
            }
        } else if (/true|false/.test(match)) {
            cls = 'kw';
        } else if (/null/.test(match)) {
            cls = 'cmt';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}
async function loadMore() {
"""

old_code = """async function loadMore() {"""

content = content.replace(old_code, highlight_fn)

old_loop = """    json.data.forEach(item => {
      const div = document.createElement('div');
      div.textContent = JSON.stringify(item, null, 2) + ',';
      container.appendChild(div);
    });"""

new_loop = """    json.data.forEach(item => {
      const div = document.createElement('div');
      div.innerHTML = syntaxHighlight(item) + ',';
      container.appendChild(div);
    });"""

content = content.replace(old_loop, new_loop)

with open('src/pages/index.astro', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
