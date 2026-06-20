from pathlib import Path

from docling.document_converter import DocumentConverter

from .models import ParsedSection


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx"}


class DocumentParser:
    def __init__(self) -> None:
        self.converter = DocumentConverter()

    def parse(self, path: Path) -> list[ParsedSection]:
        try:
            import fitz

            doc = fitz.open(str(path))
            text = ""

            for page in doc:
                text += page.get_text()

        # If enough text was extracted, use PyMuPDF
            if len(text.strip()) > 200:
                print("\n===== PDF TEXT =====")
                print(text[:2000])
                print("===== END PDF TEXT =====\n")

                return [
                    ParsedSection(
                        text=text,
                        heading="Document",
                        page=None
                    )
                ]

        except Exception:
            pass

    # Fallback to Docling only if PDF appears scanned
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
