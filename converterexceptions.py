class FileExtensionError(Exception):
    def __init__(self, text):
        self.text = text


class FileIsAlreadyExistError(Exception):
    def __init__(self, text):
        self.text = text


class FileIsEmptyError(Exception):
    def __init__(self, text):
        self.text = text
