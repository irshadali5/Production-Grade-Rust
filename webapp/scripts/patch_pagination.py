import sys

with open('src/pages/index.astro', 'r') as f:
    content = f.read()

# Extract the old script block starting from "// Sidebar active state based on scroll"
start_marker = "// Sidebar active state based on scroll"
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find the script block to replace.")
    sys.exit(1)

# Find the end of the script tag
end_idx = content.find("</script>", start_idx)
if end_idx == -1:
    print("Could not find the end of the script tag.")
    sys.exit(1)

old_script = content[start_idx:end_idx]

new_script = """// Single Chapter View Logic
const sections = Array.from(document.querySelectorAll('.chapter'));
const navItems = Array.from(document.querySelectorAll('.nav-item'));

// Dynamic Navigation container
const navContainer = document.createElement('div');
navContainer.style.display = 'flex';
navContainer.style.justifyContent = 'space-between';
navContainer.style.marginTop = '60px';
navContainer.style.paddingTop = '24px';
navContainer.style.borderTop = '1px solid var(--border)';

const prevBtn = document.createElement('a');
prevBtn.style.cursor = 'pointer';
prevBtn.style.color = 'var(--accent-2)';
prevBtn.style.textDecoration = 'none';
prevBtn.style.fontWeight = '600';
prevBtn.style.fontSize = '14px';

const nextBtn = document.createElement('a');
nextBtn.style.cursor = 'pointer';
nextBtn.style.color = 'var(--accent-2)';
nextBtn.style.textDecoration = 'none';
nextBtn.style.textAlign = 'right';
nextBtn.style.fontWeight = '600';
nextBtn.style.fontSize = '14px';

navContainer.appendChild(prevBtn);
navContainer.appendChild(nextBtn);

function getNavText(navItem) {
  if (!navItem) return '';
  const clone = navItem.cloneNode(true);
  const num = clone.querySelector('.chapter-num');
  if (num) num.remove();
  return clone.textContent.trim();
}

function navigateTo(id) {
  const currentIndex = sections.findIndex(sec => sec.id === id);
  if (currentIndex === -1) return;

  history.pushState(null, '', '#' + id);

  sections.forEach(sec => sec.style.display = 'none');
  sections[currentIndex].style.display = 'block';
  sections[currentIndex].appendChild(navContainer);

  if (currentIndex > 0) {
    const prevSection = sections[currentIndex - 1];
    const prevNav = navItems.find(nav => nav.getAttribute('href') === '#' + prevSection.id);
    prevBtn.innerHTML = '&larr; ' + (prevNav ? getNavText(prevNav) : prevSection.id);
    prevBtn.onclick = () => { navigateTo(prevSection.id); window.scrollTo(0,0); };
    prevBtn.style.visibility = 'visible';
  } else {
    prevBtn.style.visibility = 'hidden';
  }

  if (currentIndex < sections.length - 1) {
    const nextSection = sections[currentIndex + 1];
    const nextNav = navItems.find(nav => nav.getAttribute('href') === '#' + nextSection.id);
    nextBtn.innerHTML = (nextNav ? getNavText(nextNav) : nextSection.id) + ' &rarr;';
    nextBtn.onclick = () => { navigateTo(nextSection.id); window.scrollTo(0,0); };
    nextBtn.style.visibility = 'visible';
  } else {
    nextBtn.style.visibility = 'hidden';
  }

  navItems.forEach(item => item.classList.remove('active'));
  const activeNav = navItems.find(nav => nav.getAttribute('href') === '#' + id);
  if (activeNav) activeNav.classList.add('active');
  
  window.scrollTo(0,0);
}

const hash = window.location.hash.substring(1);
if (hash && sections.some(sec => sec.id === hash)) {
  navigateTo(hash);
} else {
  navigateTo(sections[0].id);
}

navItems.forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    const id = item.getAttribute('href').substring(1);
    navigateTo(id);
  });
});
"""

content = content.replace(old_script, new_script)

with open('src/pages/index.astro', 'w') as f:
    f.write(content)

print("Pagination logic applied successfully.")
