import os
from abc import abstractmethod, ABC


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


class Converter:

    def _try_to_get_csv_file(file):
        try:
            if not os.path.exists(file):
                raise FileExistsError  # Написать, что файл не существует
            elif os.stat(file).st_size == 0:
                raise FileIsEmptyError  # Создать Exception
            elif not file.endswith(".csv"):
                raise FileExtensionError  # Создать Exception
        except FileExistsError:
            print("File is not exist")
        except FileIsEmptyError:
            print("File is empty")
        except FileExtensionError:
            print("Wrong extencion. It must be .csv")
        else:
            return file

    def _try_to_get_json_file(file):
        try:
            if not file.endswith(".json"):
                raise FileExtensionError  # Создать Exception
            elif os.path.exists(file):
                raise FileExistsError  # Написать, что файл уже существует
        except FileExtensionError:
            print("Wrong extencion. It must be .json")
        except FileExistsError:
            print("File is already exist")
        else:
            return file

    def __new__(cls, file):
        if file.endswith(".csv"):
            return CsvToJson(_try_to_get_csv_file(file))
        elif file.endswith(".json"):
            return JsonToCsv(_try_to_get_json_file(file))

    def _get_headers(self):
        raise NotImplementedError("_get_headers is not implemented")

    def parse(self):
        pass


class CsvToJson(Converter):
    def __init__(self, filename):
        self.file = filename

    def _get_headers(self):
        '''
        Takes the very first line of .csv doc and split it up to take
        all headers.
        '''
        with FileManager(self.csvfile, 'r') as f:
            self._headers = f.readline().rstrip().split(sep=',')
            return self._headers,

    def _get_values(self):
        self._headers = self._get_headers()
        self._i = 0
        self.list_of_strings_to_add = []

        with FileManager(self.csvfile, 'r') as f:
            _temp = line.split(",")  # List of csv line elements
            for i, item in enumerate(_temp, 0):

                if not item.strip().isdigit():
                    line_to_add += '\t"' + \
                        self._headers[i] + '":"' + item + '",\n'
                elif not item:
                    line_to_add += '\t"' + self._headers[i] + '":" ",\n'
                else:
                    line_to_add += '\t"' + \
                        self._headers[i] + '":' + item + ",\n"
            line_to_add += "\t},\n"
            self.list_of_strings_to_add.append(line_to_add)
        return self.list_of_strings_to_add

        # headers = get_headers
        # line = get_line()
        # objects.append(create_object(line))
        # write_to_new_file(objects, type=JSON)
    # use RE here

    def parse(self):
        self.jsonstring = ''
        try:
            with FileManager(self.jsonfile, 'x') as f:
                self.jsonstring += '[\n'
                for line in self._get_values():
                    self.jsonstring += "\t" + line
                self.jsonstring.rstrip(",\n")
                self.jsonstring += "]\n"
                f.write(self.jsonstring)
                return True
        except FileExistsError:
            print("File is already exist, enter other name")
            self.parse()


class JsonToCsv:
    pass


if __name__ == "__main__":
    k = Converter('file.csv')
