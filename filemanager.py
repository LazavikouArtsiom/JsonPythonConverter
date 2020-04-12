class FileManager:
    def __init__(self, filename, access_mode):
        self.filename = filename
        self.access_mode = access_mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.access_mode)
        return self.file

    def __exit__(self, *args, **kwargs):
        self.file.close()

