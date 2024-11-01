import json
from pathlib import Path
import hashlib
import os
from typing import TextIO


class WikiCrawlerPipeline:
    def process_item(self, item, spider):
        result = {
            "wikitext": item['wikitext'],
            "meta": item['meta']
        }

        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        # Создаем хеш от заголовка и используем первые два символа для подпапки
        title_hash = hashlib.md5(item['meta']['title'].encode()).hexdigest()
        subfolder = title_hash[:2]

        file_path = output_dir / subfolder
        file_path.mkdir(exist_ok=True)

        # Сохранение файла
        filename = file_path / f"{item['meta']['title']}.json"

        with filename.open('w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return item
