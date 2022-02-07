import json
import os


from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

LIB_DIR = 'library'
TEXTS_SUBDIR = 'books'
IMAGES_SUBDIR = 'images'
PAGES_SUBDIR='pages'

def load_json(json_path):
    if os.path.exists(json_path) and os.path.isfile(json_path):
        with open(json_path, 'r') as file:
            catalog = json.load(file)
    else:
        catalog = {}
    for book in catalog.values():
        for key in ['img_src', 'book_path']:
            book.update({key:'../../'+ book[key].replace('\\', '/')})
    return catalog

def on_reload():
    json_path = os.path.join(LIB_DIR, 'catalog.json')
    catalog = load_json(json_path)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    for page_num,books in enumerate(list(chunked(catalog.values(),20))):
        rendered_page = template.render(catalog=chunked(books,2))
        with open(f'{LIB_DIR}/{PAGES_SUBDIR}/index{page_num+1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    os.makedirs(f'{LIB_DIR}/{PAGES_SUBDIR}', exist_ok=True)
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve()


if __name__ == '__main__':
    main()
