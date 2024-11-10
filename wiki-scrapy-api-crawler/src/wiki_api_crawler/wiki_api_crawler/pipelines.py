import hashlib
import json
from datetime import datetime
from pathlib import Path


class WikiCrawlerFilePipeline:
    """Запись в файлы"""

    def process_item(self, item, spider):
        result = dict(item)
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        # Создаем хеш от заголовка и используем первые два символа для подпапки
        title_hash = hashlib.md5(item['title'].encode()).hexdigest()
        subfolder = title_hash[:2]

        file_path = output_dir / subfolder
        file_path.mkdir(exist_ok=True)

        filename = file_path / f"{item['title']}.json"

        with filename.open('w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return item


class AddTimes:
    def process_item(self, item, spider):
        current_time = datetime.now().isoformat()

        item["time_request"] = current_time
        item["created_at"] = current_time
        item["updated_at"] = current_time
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
