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
        raise FileNotFoundError(f'file not found: {json_path}  <func: load_json>')
    for book in catalog.values():
        for key in ['img_src', 'book_path']:
            book.update({key: '../../' + book[key].replace('\\', '/')})
    return catalog


def create_link(page_number):
    return f'../../{LIB_DIR}/{PAGES_SUBDIR}/index{page_number}.html'


def make_paginator(current_page_num, last_page_num):
    if last_page_num == 1:
        return []
    frame_length = min(last_page_num, PAGINATOR_LEN)
    first_frame_num = min(max(1, current_page_num - frame_length // 2), last_page_num - frame_length + 1)
    paginator = []
    for page_num in range(first_frame_num, first_frame_num + frame_length):
        paginator.append([str(page_num), '#' if page_num == current_page_num else create_link(page_num)])
    paginator.insert(0, ['<<', create_link(current_page_num - 1) if current_page_num > 1 else ''])
    paginator.append(['>>', create_link(current_page_num + 1) if current_page_num < last_page_num else ''])
    if frame_length < last_page_num:
        paginator.insert(0, ['первая', create_link(1) if current_page_num != 1 else ''])
        paginator.append(['последняя', create_link(last_page_num) if current_page_num != last_page_num else ''])
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
    try:
        on_reload()
    except FileNotFoundError as e:
        print(f'работа программы остановлена, ошибка: {str(e)}', file=sys.stdout)
        print(str(e), file=sys.stderr)
        return
    server = Server()
    server.watch('template.html', on_reload)
    webbrowser.open('http://localhost:5500', new=0, autoraise=True)
    server.serve(root=f'.', default_filename='index.html')


if __name__ == '__main__':
    main()
