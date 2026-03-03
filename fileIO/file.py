import os


class FileIO:
    @classmethod
    def copy_file(cls, path1, file_name):
        content = cls.get_content(path1)
        file_path = "static/" + file_name
        f = open(file_path, "w")
        f.write(content)
        f.close()
        return file_path

    @classmethod
    def save_bpmn_file(cls, xml_file_link, file):
        if os.path.splitext(file.filename)[1] != ".bpmn":
            raise Exception("File format is not supported")
        # if file.size > 10*1024*1024:
        #     raise Exception('File size is larger than 10MB are not allowed')
        file.save(xml_file_link)

    @classmethod
    def create_bpmn_file(cls, file, file_name):
        if os.path.splitext(file.filename)[1] != ".bpmn":
            raise Exception("File format is not supported")
        # if file.size > 10*1024*1024:
        #     raise Exception('File size is larger than 10MB are not allowed')
        file_path = "static/" + file_name
        file.save(file_path)
        return file_path

    @classmethod
    def delete(cls, link):
        os.remove(link)

    @classmethod
    def bulk_delete(cls, links):
        for link in links:
            os.remove(link[0])

    @classmethod
    def save_img_file(cls, file, file_name):
        if os.path.splitext(file.filename)[1] not in [".jpg", ".png", ".jpeg", ".gif"]:
            raise Exception("Image file format is not supported")
        # if file.size > 10*1024*1024:
        #     raise Exception('File size is larger than 10MB are not allowed')
        file_path = "static/" + file_name
        file.save(file_path)
        return file_path

    @classmethod
    def create_default_md_file(cls, file_name):
        file_path = "static/" + file_name
        f = open(file_path, "w")
        f.close()
        return file_path

    @classmethod
    def save_md_file(cls, file_link, new_file):
        if os.path.splitext(new_file.filename)[1] not in [".md"]:
            raise Exception("Markdown file format is not supported")
        # if new_file.size > 10*1024*1024:
        #     raise Exception('File size is larger than 10MB are not allowed')
        new_file.save(file_link)

    @classmethod
    def get_content(cls, file_link):
        f = open(file_link, "r")
        content = f.read()
        f.close()
        return content
