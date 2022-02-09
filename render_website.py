import glob
import json
import os
import webbrowser

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

LIB_DIR = 'library'
TEXTS_SUBDIR = 'books'
IMAGES_SUBDIR = 'images'
PAGES_SUBDIR = 'pages'
STATIC_SUBDIR = 'static'
BOOKS_PER_PAGE = 10
PAGINATOR_LEN = 9


def load_json(json_path):
    if os.path.exists(json_path) and os.path.isfile(json_path):
        with open(json_path, 'r') as file:
            catalog = json.load(file)
    else:
        catalog = {}
    for book in catalog.values():
        for key in ['img_src', 'book_path']:
            book.update({key: '../../' + book[key].replace('\\', '/')})
    return catalog


def make_paginator(page, max_page):
    link_template = f'../../{LIB_DIR}/{PAGES_SUBDIR}/index*.html'
    xxx = []
    if max_page == 1:
        return xxx
    frame_length = min(max_page, PAGINATOR_LEN)
    if frame_length < max_page:
        xxx.append(['первая', ''] if page == 1 else ['первая', link_template.replace('*', '1')])
    xxx.append(['<<', ''] if page <= 1 else ['<<', link_template.replace('*', str(page - 1))])
    frame = [page - frame_length // 2, page - frame_length // 2 + frame_length]
    offset = 1 - frame[0] if frame[0] < 1 else max_page - frame[1] + 1 if frame[1] > max_page else 0
    if offset != 0:
        frame = [x + offset for x in frame]
    for i in range(*frame):
        xxx.append([str(i), '#'] if i == page else [str(i), link_template.replace('*', str(i))])
    xxx.append(['>>', ''] if page >= max_page else ['>>', link_template.replace('*', str(page + 1))])
    if frame_length < max_page:
        xxx.append(['последняя', ''] if page == max_page else ['последняя', link_template.replace('*', str(max_page))])
    return xxx


def on_reload():
    json_path = os.path.join(LIB_DIR, 'catalog.json')
    catalog = load_json(json_path)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    end_page = (len(catalog) - 1) // BOOKS_PER_PAGE + 1
    for page_num, books in enumerate(list(chunked(catalog.values(), BOOKS_PER_PAGE)), 1):
        paginator = make_paginator(page_num, end_page)
        rendered_page = template.render(
            catalog=chunked(books, 2),
            paginator=paginator,
            static_url=f'../../{LIB_DIR}/{STATIC_SUBDIR}'
        )
        with open(f'{LIB_DIR}/{PAGES_SUBDIR}/index{page_num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
    template = env.get_template('start_template.html')
    with open('./index.html', 'w', encoding="utf8") as file:
        file.write(template.render(start_link=f'./{LIB_DIR}/{PAGES_SUBDIR}/index1.html'))


def main():
    os.makedirs(f'{LIB_DIR}/{PAGES_SUBDIR}', exist_ok=True)
    for file in glob.glob(f'{LIB_DIR}/{PAGES_SUBDIR}/index*.html'):
        os.remove(file)
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    webbrowser.open('http://localhost:5500', new=0, autoraise=True)
    server.serve(root=f'.', default_filename='index.html')


if __name__ == '__main__':
    main()
