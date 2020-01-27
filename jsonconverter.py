import os
from abc import abstractmethod


class Converter:
    @abstractmethod
    def parse(self):
        pass


class CsvToJson(Converter):
    # use RE here
    def __init__(self):
        self.csvfile = input("Enter the name of .csv file : ")
        if not os.path.exists(self.csvfile):
            print("File doesn't exist")
            self.__init__()
        if os.stat(self.csvfile).st_size == 0:
            print("File is empty, choose another one")
            self.__init__()
        self.jsonfile = input("Enter the name of .json file : ")
        

    def _get_header(self):
        self._keys = []
        try:
            with open(self.csvfile, 'r') as f:
                self._keys = f.readline().split(sep=',')
                return self._keys
        except FileNotFoundError:
            print("The file doesn't exist")

    def _get_values(self):
        self._header = self._get_header()
        self._i = 0
        self.list_of_strings_to_add = []
        try:
            with open(self.csvfile, 'r') as f:
                for line in f:
                    if self._i == 0:
                        self._i += 1
                        continue
                    for i, item in enumerate(line.split(",")):
                        line_to_add = ""
                        if not item.isdigit():
                            line_to_add += '"' + self._header[i] + '"' + ":" + '"' + item + '"'
                        else:
                            line_to_add += '"' + self._header[i] + '"' + ":" + item
                        self.list_of_strings_to_add.append(line_to_add)
                return self.list_of_strings_to_add
        except FileNotFoundError:
            print("The file doesn't exist")

    # use RE here
    def parse(self):
        try:
            with open(self.jsonfile, 'x') as f:
                self.jsonstring += '\n + "data":['
                for line in self._get_values():
                    self.jsonstring += "{" + line + "},\n"
                self.jsonstring.rstip(",\n")
                self.jsonstring += "]\n"
                f.write(self.jsonstring)
                return True
        except FileExistsError:
            print("File is already exist, enter other name")
            self.parse()


if __name__ == "__main__":
    k = CsvToJson()
    k.parse()
