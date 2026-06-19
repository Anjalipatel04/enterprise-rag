from pathlib import Path

from docling.document_converter import DocumentConverter

from .models import ParsedSection


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx"}


class DocumentParser:
    def __init__(self) -> None:
        self.converter = DocumentConverter()

    def parse(self, path: Path) -> list[ParsedSection]:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        result = self.converter.convert(str(path))
        document = result.document
        markdown = document.export_to_markdown()
        return self._sections_from_markdown(markdown)

    @staticmethod
    def _sections_from_markdown(markdown: str) -> list[ParsedSection]:
        sections: list[ParsedSection] = []
        heading: str | None = None
        buffer: list[str] = []

        for raw_line in markdown.splitlines():
            line = raw_line.rstrip()
            if line.startswith("#"):
                if buffer:
                    sections.append(ParsedSection(text="\n".join(buffer).strip(), heading=heading, page=None))
                    buffer = []
                heading = line.lstrip("#").strip() or heading
                buffer.append(line)
            elif line.strip():
                buffer.append(line)

        if buffer:
            sections.append(ParsedSection(text="\n".join(buffer).strip(), heading=heading, page=None))

        return [section for section in sections if section.text]
