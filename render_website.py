import glob
import json
import os
import sys
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
        print(f'file not found: {json_path}', file=sys.stderr)
        print(f'Ошибка! Файл "{json_path}" не найден', file=sys.stdout)
        sys.exit(1)
    for book in catalog.values():
        for key in ['img_src', 'book_path']:
            book.update({key: '../../' + book[key].replace('\\', '/')})
    return catalog


def make_paginator(current_page, last_page):
    def link(page_number):
        return f'../../{LIB_DIR}/{PAGES_SUBDIR}/index{page_number}.html'

    if last_page == 1:
        return []
    paginator = []
    frame_length = min(last_page, PAGINATOR_LEN)
    page = current_page - frame_length // 2 - 1
    while len(paginator) < frame_length:
        page += 1
        if page < 1:
            continue
        elif page <= last_page:
            paginator.append([str(page), '#' if page == current_page else link(page)])
        else:
            page_before = int(paginator[0][0]) - 1
            paginator.insert(0, [str(page_before), link(page_before)])
    paginator.insert(0, ['<<', link(current_page - 1) if current_page > 1 else ''])
    paginator.append(['>>', link(current_page + 1) if current_page < last_page else ''])
    if frame_length < last_page:
        paginator.insert(0, ['первая', link(1) if current_page != 1 else ''])
        paginator.append(['последняя', link(last_page) if current_page != last_page else ''])
    return paginator


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
