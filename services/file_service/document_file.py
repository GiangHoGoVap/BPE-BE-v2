from data.repositories.document_file import DocumentFile
from fileIO.file import FileIO


class DocumentFileService:
    @classmethod
    def create_default(cls, project_id):
        document_link = FileIO.create_default_md_file(f"{project_id}/readme.md")
        DocumentFile.create(document_link, project_id)

    @classmethod
    def save(cls, document_link, file):
        FileIO.save_md_file(document_link, file)
        DocumentFile.update(document_link)

    @classmethod
    def get(cls, project_id):
        return DocumentFile.get(project_id)
