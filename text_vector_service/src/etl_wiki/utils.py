from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size:int=1000, chunk_overlap:int=100) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                   chunk_overlap=chunk_overlap,
                                                   length_function=len)
    return text_splitter.split_text(text)
