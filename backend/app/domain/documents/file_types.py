from app.domain.documents.models import SupportedFileType

GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
PDF_MIME_TYPE = "application/pdf"
TEXT_MIME_TYPE = "text/plain"
MARKDOWN_MIME_TYPE = "text/markdown"
MARKDOWN_EXTENSIONS = (".md", ".markdown")


def get_supported_file_type(
    mime_type: str,
    name: str,
) -> SupportedFileType | None:
    normalized_mime_type = mime_type.strip().lower()
    normalized_name = name.strip().lower()

    if normalized_mime_type == GOOGLE_DOC_MIME_TYPE:
        return SupportedFileType.GOOGLE_DOC

    if normalized_mime_type == PDF_MIME_TYPE:
        return SupportedFileType.PDF

    if normalized_mime_type == TEXT_MIME_TYPE:
        return SupportedFileType.TEXT

    if normalized_mime_type == MARKDOWN_MIME_TYPE:
        return SupportedFileType.MARKDOWN

    if normalized_name.endswith(MARKDOWN_EXTENSIONS):
        return SupportedFileType.MARKDOWN

    return None
