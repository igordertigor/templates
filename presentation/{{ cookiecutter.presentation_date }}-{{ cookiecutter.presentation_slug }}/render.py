from datetime import datetime
from jinja2 import Template


with open('resources/index.j2.html') as f:
    templ = Template(f.read())

with open('content.md') as f:
    markdown = f.read()

with open('style.css') as f:
    style = f.read()

with open('index.html', 'w') as f:
    f.write(templ.render(style=style, markdown=markdown))

print(f'{datetime.now().isoformat()} wrote file index.html')
