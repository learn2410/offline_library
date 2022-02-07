from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import json
import webbrowser

LIB_DIR = 'library'
TEXTS_SUBDIR = 'books'
IMAGES_SUBDIR = 'images'

def load_json(json_path):
    if os.path.exists(json_path) and os.path.isfile(json_path):
        with open(json_path, 'r') as file:
            catalog = json.load(file)
    else:
        catalog = {}
    for v in catalog.values():
        for key in ['img_src','book_path']:
            v.update({key:v[key].replace('\\','/')})
    return catalog

def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    json_path=os.path.join(LIB_DIR, 'catalog.json')
    catalog=load_json(json_path)

    template = env.get_template('template.html')
    rendered_page = template.render(catalog=catalog )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    webbrowser.open('http://127.0.0.1:8000', new=0, autoraise=True)
    server.serve_forever()


if __name__ == '__main__':
    main()