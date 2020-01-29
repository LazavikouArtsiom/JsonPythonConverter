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


class Converter(ABC):
    @abstractmethod
    def parse(self):
        pass


class CsvToJson(Converter):
    def __init__(self):
        self.csvfile = input("Enter the name of .csv file : ")
        while not os.path.exists(self.csvfile):
            self.csvfile = input("Enter the name of .csv file : ")
        while os.stat(self.csvfile).st_size == 0:
            print("File is empty, choose another one")
            self.csvfile = input("Enter the name of .csv file : ")

        self.jsonfile = input("Enter the name of .json file : ")
        while not self.jsonfile.endswith(".json"):
            self.jsonfile = input(
                "The name must be end with .json, try again : ")
        self.jsonstring = ''

    def _get_headers(self):
        '''
        Takes the very first line of .csv doc and split it up to take
        all headers.
        '''
        self.list_of_headers = []
        with FileManager(self.csvfile, 'r') as f:
            self._keys = f.readline().rstrip().split(sep=',')
            return self.list_of_headers

    def _get_values(self):
        self._headers = self._get_headers()
        self._i = 0
        self.list_of_strings_to_add = []

        with FileManager(self.csvfile, 'r') as f:
            for line in f:
                line = line.rstrip()
                if self._i == 0:
                    self._i += 1
                    continue
                line_to_add = "{\n"
                _temp = line.split(",")  # List of csv line elements
                for i, item in enumerate(_temp, 0):

                    if not item.strip().isdigit():
                        line_to_add += '\t"' + \
                            self._header[i] + '":"' + item + '",\n'
                    elif not item:
                        line_to_add += '\t"' + self._header[i] + '":" ",\n'
                    else:
                        line_to_add += '\t"' + \
                            self._header[i] + '":' + item + ",\n"
                line_to_add += "\t},\n"
                self.list_of_strings_to_add.append(line_to_add)
            return self.list_of_strings_to_add

    # use RE here

    def parse(self):
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


if __name__ == "__main__":
    k = CsvToJson()
    k._get_header()
    k.parse()
