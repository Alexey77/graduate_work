import re
import logging
import sqlite3

from datetime import datetime
from typing import Pattern

import xml.etree.ElementTree as ET

# https://dumps.wikimedia.org/ruwiki/20241101/

# Пути к файлам
DUMP_FILE = 'E:\\temp\\wiki\\ruwiki-20241101-pages-meta-current.xml\\ruwiki-20241101-pages-meta-current.xml'
DATABASE_FILE = 'wiki_pages.sqlite'

movie_phrases = {
    "кино", "фильм", "сериал", "телефильм",
    "актер", "актриса",
    "режиссер", "кинорежиссер",
    "оператор", "кинооператор",
    "сценарий", "сценарист",
    "кинопремия", "кинокомпания"
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_database(db_file: str) -> None:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wiki_page (
            page_id INTEGER PRIMARY KEY,
            title TEXT,
            wikitext TEXT,
            url TEXT,
            source TEXT,
            lang TEXT,
            revision_id INTEGER,
            created_at TEXT,
            updated_at TEXT,
            time_request TEXT
        )
    ''')
    conn.commit()
    conn.close()


def compile_phrase_pattern(phrases: set[str]) -> Pattern:
    escaped_phrases = [re.escape(phrase) for phrase in phrases]
    pattern = re.compile(r'\b(' + '|'.join(escaped_phrases) + r')\b', re.IGNORECASE)
    return pattern


def contains_movie_phrase(text: str, pattern: Pattern) -> bool:
    return bool(pattern.search(text))


def get_revision_id(revision: ET.Element, ns: dict[str, str]) -> str | None:
    rev_id_elem = revision.find('ns:id', ns)
    return rev_id_elem.text if rev_id_elem is not None else None


def insert_batch(cursor: sqlite3.Cursor, batch: list[tuple]) -> None:
    cursor.executemany('''
        INSERT OR IGNORE INTO wiki_page 
        (page_id, title, wikitext, url, source, lang, revision_id, created_at, updated_at, time_request)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', batch)


def process_page(elem: ET.Element, pattern: Pattern, ns: dict[str, str]) -> tuple | None:
    ns_text = elem.findtext('ns:ns', namespaces=ns)
    if ns_text != '0':
        return None

    page_id = elem.findtext('ns:id', namespaces=ns)
    title = elem.findtext('ns:title', namespaces=ns)

    if page_id is None or title is None:
        return None

    revision = elem.find('ns:revision', namespaces=ns)
    if revision is None:
        return None

    revision_id = get_revision_id(revision, ns)
    if revision_id is None:
        return None

    text_elem = revision.find('ns:text', namespaces=ns)
    text = text_elem.text if text_elem is not None else ''

    if contains_movie_phrase(text, pattern):
        current_time = datetime.now().isoformat()
        data = (
            int(page_id),
            title,
            text,
            '',
            'ru.wikipedia.org',
            'ru',
            int(revision_id),
            current_time,
            current_time,
            current_time
        )
        return data
    else:
        return None


def process_dump(dump_file: str, db_file: str, movie_phrases: set[str]) -> None:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    batch = []
    batch_size = 100
    page_count = 0
    matched_pages = 0

    pattern = compile_phrase_pattern(movie_phrases)
    ns = {'ns': 'http://www.mediawiki.org/xml/export-0.11/'}

    context = ET.iterparse(dump_file, events=('end',))
    for _, elem in context:
        if elem.tag == '{http://www.mediawiki.org/xml/export-0.11/}page':
            page_count += 1

            data = process_page(elem, pattern, ns)
            if data:
                matched_pages += 1
                batch.append(data)

                if len(batch) >= batch_size:
                    insert_batch(cursor, batch)
                    conn.commit()
                    batch = []
                    logging.info(f'Обработано страниц: {page_count}, найдено совпадений: {matched_pages}')

            elem.clear()  # Очистка элемента для освобождения памяти

    if batch:
        insert_batch(cursor, batch)
        conn.commit()

    conn.close()
    logging.info(f'Завершена обработка. Всего страниц: {page_count}, найдено совпадений: {matched_pages}')


def main() -> None:
    create_database(DATABASE_FILE)
    process_dump(DUMP_FILE, DATABASE_FILE, movie_phrases)


if __name__ == '__main__':
    main()
