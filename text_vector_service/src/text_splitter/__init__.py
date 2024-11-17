from sentence_transformers import SentenceTransformer


class TextSplitter:
    def __init__(self, model: SentenceTransformer, chunk_size: int = 512, overlap_percentage: int = 15):
        """
                Инициализация сплиттера текста

                Args:
                    model (SentenceTransformer): модель
                    chunk_size (int): Максимальный размер чанка в токенах
                    overlap_percentage (int): Процент пересечения между чанками (0-100)
                """
        self.model = model
        self.tokenizer = self.model.tokenizer
        self.tokenizer.model_max_length = int(1e30)
        self.chunk_size = min(chunk_size, self.tokenizer.model_max_length)
        self.overlap_size = int(self.chunk_size * (overlap_percentage / 100))

    def split_text(self, title: str, text: str) -> list[str]:
        """
                Разбивает текст на чанки с заданным пересечением

                Args:
                    title (str): Заголовок страницы
                    text (str): Входной текст для разбиения

                Returns:
                    List[str]: Список строк-чанков
                """
        title_tokens = self.tokenizer.encode(title + "\n\n", add_special_tokens=False, truncation=False)
        title_length = len(title_tokens)

        # Уменьшаем размер чанка на длину заголовка
        adjusted_chunk_size = self.chunk_size - title_length

        tokens = self.tokenizer.encode(text, add_special_tokens=False, truncation=False)

        if len(tokens) <= adjusted_chunk_size:
            return [title + "\n\n" + text]

        chunks_tokens = []
        start = 0

        while start < len(tokens):
            end = min(start + adjusted_chunk_size, len(tokens))
            chunks_tokens.append(tokens[start:end])
            if end == len(tokens):
                break
            start = end - self.overlap_size

        chunks = []
        for chunk_tokens in chunks_tokens:
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(title + "\n\n" + chunk_text)

        return chunks

    def get_tokens_count(self, text: str) -> int:
        """
            Подсчитывает количество токенов в тексте

            Args:
                text (str): Входной текст

            Returns:
                int: Количество токенов
                """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)
