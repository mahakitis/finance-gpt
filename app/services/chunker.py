def chunk_paragraphs(text: str, max_length: int = 500):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buffer = ""

    for para in paragraphs:
        if len(buffer) + len(para) <= max_length:
            buffer += " " + para
        else:
            chunks.append(buffer.strip())
            buffer = para

    if buffer:
        chunks.append(buffer.strip())

    return chunks
