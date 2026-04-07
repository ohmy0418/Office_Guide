from app.services.ingestion.chunking import merge_paragraphs_into_chunks


def test_merge_paragraphs_groups_pages() -> None:
    paras = [
        (1, "첫 문단입니다. " * 20),
        (1, "두 번째 문단."),
        (2, "다음 페이지 문단."),
    ]
    chunks = merge_paragraphs_into_chunks(paras)
    assert len(chunks) >= 1
    assert all("content" in c and "page_start" in c for c in chunks)
