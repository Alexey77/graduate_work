import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .settings import DB_URI


class WikiCrawlerFilePipeline:
    def process_item(self, item, spider):

        result = dict(item)
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        # Создаем хеш от заголовка и используем первые два символа для подпапки
        title_hash = hashlib.md5(item['title'].encode()).hexdigest()
        subfolder = title_hash[:2]

        # file_path = output_dir / subfolder
        file_path = output_dir
        file_path.mkdir(exist_ok=True)

        filename = file_path / f"{item['title']}.json"

        with filename.open('w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return item


class AddTimeRequest:
    def process_item(self, item, spider):
        item["time_request"] = datetime.now().isoformat()
        return item


class AddCreatedAt:
    def process_item(self, item, spider):
        item["created_at"] = datetime.now().isoformat()
        return item


class AddUpdatedAt:
    def process_item(self, item, spider):
        item["updated_at"] = datetime.now().isoformat()
        return item


class AddLanguage:
    def process_item(self, item, spider):
        item["lang"] = spider.language
        return item


class AddSource:
    def process_item(self, item, spider):
        item["source"] = f"{spider.language}.wikipedia.org"
        return item


class WikiSQlitePipeline:
    def process_item(self, item, spider):

        try:
            spider.db.insert_or_update_item(item)
            spider.logger.info(f"Item with page_id {item['page_id']} processed successfully.")
        except Exception as e:
            spider.logger.error(f"Error processing item with page_id {item['page_id']}: {e}")
            raise
        return item


class WikiCrawlerDBPipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect(DB_URI)
        self.cursor = self.connection.cursor()

        # Create table for storing Wikipedia data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wikipedia_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                wikitext TEXT,
                url TEXT,
                revision_id INTEGER,
                page_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        new_revision_id = item.get('revision_id')

        self.cursor.execute("SELECT revision_id FROM wikipedia_pages WHERE page_id = ?", (item['page_id'],))
        existing_revision = self.cursor.fetchone()

        if existing_revision:
            # If the pageid exists, compare revision_id
            current_revision_id = existing_revision[0]

            if new_revision_id and current_revision_id != new_revision_id:
                # If revision_id has changed, update the record
                self.cursor.execute(
                    '''
                        UPDATE wikipedia_pages
                        SET revision_id = ?, title = ?, wikitext = ?, url = ?
                        WHERE page_id = ?
                    ''',
                    (new_revision_id, item['title'], item['wikitext'], item['url'], item['page_id'])
                )
                self.connection.commit()
        else:
            # If the pageid doesn't exist, insert a new record
            self.cursor.execute(
                '''
                    INSERT INTO wikipedia_pages (page_id, title, wikitext, url, revision_id)
                    VALUES (?, ?, ?, ?, ?)
                ''',
                (item.get('page_id'), item['title'], item['wikitext'], item['url'], new_revision_id)
            )
            self.connection.commit()

        return item
