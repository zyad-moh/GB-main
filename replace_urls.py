import os
import re

d = r'g:/RAG-rag-v16-010/original_stable_project/frontend/src'

for r, _, fs in os.walk(d):
    for f in fs:
        if f.endswith('.js'):
            filepath = os.path.join(r, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace occurrences
            # Pattern: "https://rag-rag-v16-010-production-1b78.up.railway.app"
            # We want to replace it with process.env.NEXT_PUBLIC_API_URL
            content = re.sub(r'\"https://rag-rag-v16-010-production[^\"\']*?\.up\.railway\.app(?:/api/v1)?\"', 'process.env.NEXT_PUBLIC_API_URL', content)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
