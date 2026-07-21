from __future__ import annotations

import io
import zipfile

import docx
from pypdf import PdfReader

from instream_shared.types import RawContent

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


class PdfExtractor:
    def extract(self, filename: str, content: bytes) -> RawContent:
        reader = PdfReader(io.BytesIO(content))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages_text).strip()
        if text:
            return RawContent(text=text, needs_ocr=False)
        # No extractable text layer — likely a scanned PDF. Rendering pages
        # to images requires a system PDF renderer (Phase 1 doesn't ship
        # one); downstream OCR providers get an empty page image list and
        # fall back to whatever they can do with the raw bytes.
        return RawContent(text="", needs_ocr=True, page_images=[content])


class DocxExtractor:
    def extract(self, filename: str, content: bytes) -> RawContent:
        document = docx.Document(io.BytesIO(content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
        return RawContent(text=text, needs_ocr=False)


class ImageExtractor:
    def extract(self, filename: str, content: bytes) -> RawContent:
        return RawContent(text="", needs_ocr=True, page_images=[content])


class ZipExtractor:
    """Recurses into archive members using the shared registry, concatenating
    each member's extracted text under a filename header."""

    def extract(self, filename: str, content: bytes) -> RawContent:
        chunks: list[str] = []
        needs_ocr = False
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                member_bytes = archive.read(member.filename)
                extractor = get_extractor(member.filename)
                if extractor is None:
                    continue
                result = extractor.extract(member.filename, member_bytes)
                needs_ocr = needs_ocr or result.needs_ocr
                if result.text:
                    chunks.append(f"--- {member.filename} ---\n{result.text}")
        return RawContent(text="\n\n".join(chunks), needs_ocr=needs_ocr)


def get_extractor(filename: str):
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == ".pdf":
        return PdfExtractor()
    if suffix == ".docx":
        return DocxExtractor()
    if suffix in IMAGE_SUFFIXES:
        return ImageExtractor()
    if suffix == ".zip":
        return ZipExtractor()
    return None


def extract_attachment(filename: str, content: bytes) -> RawContent:
    extractor = get_extractor(filename)
    if extractor is None:
        return RawContent(text="", needs_ocr=False)
    return extractor.extract(filename, content)
