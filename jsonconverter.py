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
        self.jsonstring = ''
        

    def _get_header(self):
        self._keys = []
        try:
            with open(self.csvfile, 'r') as f:
                self._keys = f.readline().rstrip().split(sep=',')
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
                    line = line.rstrip()
                    if self._i == 0:
                        self._i += 1
                        continue
                    line_to_add = "{\n"
                    _temp = line.split(",") #List of csv line elements
                    for i, item in enumerate(_temp, 0):

                        if not item.strip().isdigit():
                                line_to_add += '\t"' + self._header[i] + '":"' + item + '",\n'
                        elif not item:
                                line_to_add += '\t"' + self._header[i] + '":" ",\n'
                        else:
                                line_to_add += '\t"' + self._header[i] + '":' + item + ",\n"
                    line_to_add += "\t},\n"        
                    self.list_of_strings_to_add.append(line_to_add)
                return self.list_of_strings_to_add
        except FileNotFoundError:
            print("The file doesn't exist")

    # use RE here
    def parse(self):
        try:
            with open(self.jsonfile, 'x') as f:
                self.jsonstring += '{\n'
                for line in self._get_values():
                    self.jsonstring += "\t" + line
                self.jsonstring.rstrip(",\n")
                self.jsonstring += "}\n"
                f.write(self.jsonstring)
                return True
        except FileExistsError:
            print("File is already exist, enter other name")
            self.parse()


if __name__ == "__main__":
    k = CsvToJson()
    k._get_header()
    k.parse()
    
