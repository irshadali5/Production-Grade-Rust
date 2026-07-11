import re
import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

# 1. Replace DomainStruct with SubscriberEmail
content = content.replace('DomainStruct', 'SubscriberEmail')

# 2. Remove Psychological Warfare sections
content = re.sub(r"<div class='psychological-warfare'>.*?</div>\n*", "", content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Patch applied successfully.")
