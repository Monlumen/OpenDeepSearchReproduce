import re

pattern = r"```(?:py|python)\n((?:.*\n)*?)```"

text = '''```py
answer = web_search(query="current US President")
print(answer)
```<end_code>'''

print(re.match(pattern, text, re.DOTALL))