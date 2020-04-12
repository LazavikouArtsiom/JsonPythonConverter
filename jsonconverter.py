import os
from filemanager import FileManager
from converterexceptions import *
import randomizer


class Converter:

    def __new__(cls, file, delimiter=','):
        if file.endswith(".csv"):
            return CsvToJson(file, delimiter)
        elif file.endswith(".json"):
            return JsonToCsv(file, delimiter)
        else:
            raise FileExtensionError(
                'Wrong extension. File must be end with .json or .csv')

    def _get_header(self):
        """
           parse first line of .csv file to list of headers if self.file is .csv
           else parse first json object left part if it's .json file
           input: self.file
           output: list of headers"""
        raise NotImplementedError()

    def _get_values(self):
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()

    def _try_to_get_file(self, file, caused=None):
        """File validation.
           It checks:
           1. is file exist
           2. is file empty
           3. is file has valid extencion
        """
        try:
            if not os.path.exists(file):
                raise FileExistsError("File doesn't exist")
            elif os.stat(file).st_size == 0:
                raise FileIsEmptyError("File is empty")
            elif not file.endswith('.json') and not file.endswith('.csv'):
                raise FileExtensionError("Wrong extension")
            else:
                return True
        except FileExistsError:
            self.file = input("File doesn't exist. Choose another file : ").split(".")[
                            0] + f'.{caused}'
            self._try_to_get_file(self.file, caused)
            return True

        except FileIsEmptyError:
            self.file = input("File is empty. Choose another file : ").split(".")[
                            0] + f'.{caused}'
            self._try_to_get_file(self.file, caused)

        except FileExtensionError:
            self.file = input("File you chose has wrong extension. Choose another file : ").split(
                ".")[0] + f'.{caused}'
            self._try_to_get_file(self.file, caused)
            return True

    def _create_file(self, caused=None):
        """Validate file creation.
           Fixes file extencion if it's wrong."""

        _file = input('Enter name of file to write :').split(".")[0]
        if caused == "csv":
            _file += ".json"
        else:
            _file += ".csv"
        try:
            with FileManager(_file, 'x'):
                pass
        except FileIsAlreadyExistError:
            print('File is already exist. Choose another one')
            self._create_file(caused)
        return _file


class CsvToJson(Converter):

    def __new__(cls, file, delimiter):
        return object.__new__(cls)

    def __init__(self, file, delimiter):
        self.key = randomizer.get_random_key(3)
        self.file = file
        self.delimiter = delimiter

    def _get_header(self):
        with FileManager(self.file, 'r') as f:
            _headers = f.readline().rstrip().split(sep=self.delimiter)
        return _headers

    def _get_values_with_semicolon_delimiter(self):
        _headers = self._get_header()
        _values = []
        with FileManager(self.file, 'r') as f:
            for line in f.readlines()[1:]:
                result = '\n'
                for i, item in enumerate(line.strip("\n").split(self.delimiter), 0):

                    if not item.strip().isdigit():
                        result += '\t"' + _headers[i] + \
                                  '":"' + item.strip() + '",\n'
                    else:
                        result += '\t"' + _headers[i] + \
                                  '":' + item.strip() + ",\n"
                _values.append(result)
        return _values

    def _recursive_filter(self, line, result=None):
        line = line.replace('""', f'{self.key}')
        try:
            if not result:
                result = []
            line = line.strip()
            if line.startswith('"'):
                temp = ''
                i = 0
                while line[i + 1] != '"':
                    temp += line[i]
                    i += 1
                else:
                    temp += f'{line[i]}"'
                    result.append(temp)
                    line = line[len(temp):].strip(', ')
                    self._recursive_filter(line, result)
            else:
                temp = ''
                i = 0
                while line[i] != ',':
                    temp += line[i]
                    i += 1
                temp += ','
                result.append(temp)
                line = line[len(temp):]
                self._recursive_filter(line, result)
            result = [x.replace(f'{self.key}', '\"') for x in result]
            return [x.strip(', "') for x in result]
        except IndexError:
            if temp:
                result.append(temp)

    def _get_values_with_comma_delimiter(self):
        _headers = self._get_header()
        _values = []
        with FileManager(self.file, 'r') as f:
            for line in f.readlines()[1:]:
                result = '\n'
                for i, item in enumerate(self._recursive_filter(line), 0):
                    if not item.strip().isdigit():
                        result += '\t"' + _headers[i] + \
                                  '":"' + item.strip() + '",\n'
                    else:
                        result += '\t"' + _headers[i] + \
                                  '":' + item.strip() + ",\n"
                _values.append(result)
        return _values

    def _get_all_data(self):
        if self.delimiter == ';':
            _values = self._get_values_with_semicolon_delimiter()
        else:
            _values = self._get_values_with_comma_delimiter()
        _result = '[\n'
        _end = '\n]'
        for i in range(len(_values)):
            if i == len(_values) - 1:
                _result += "\t{" + str(_values[i])[:-1] + "\n\t}"
            else:
                _result += "\t{" + str(_values[i])[:-1] + "\n\t},\n"
        _result += _end
        return _result

    def parse(self):
        self._try_to_get_file(self.file, 'csv')
        _data = self._get_all_data()
        with FileManager(self._create_file("csv"), 'w') as f:
            f.write(_data)
        return True


class JsonToCsv(Converter):
    def __new__(cls, file, delimiter):
        return object.__new__(cls)

    def __init__(self, file, delimiter):
        self.file = file
        self.delimiter = delimiter

    def _get_header(self):
        _not_valid = ['{\n', '}\n', '[\n']
        _headers = []
        with FileManager(self.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _not_valid):
                    if '},' in line:
                        return _headers
                    _headers.append(line.split(':')[0].strip('\t"'))
        return _headers

    def _get_values(self):
        _not_valid = ['{\n', '},\n,', '}', '[', ']']
        _header_len = len(self._get_header())
        _values = []
        with FileManager(self.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _not_valid) and not line == ',\n':
                    _values.append([line.split(':')[-1].strip('\t\n, ')])
        return _values

    def _write_to_file(self):
        _header = self._get_header()
        _header_len = len(self._get_header())
        _values = self._get_values()
        result = []

        with FileManager(self._create_file("json"), 'w') as f:
            f.write(self.delimiter.join(_header) + '\n')
            _i = 0
            for value in _values:
                if not _i == 0 and (_i + 1) % _header_len == 0:
                    if value[0].isdigit():
                        result.append(value[0] + '\n')
                    else:
                        result.append(value[0][1:-1] + '\n')
                else:
                    if value[0].isdigit():
                        result.append(value[0] + self.delimiter)
                    else:
                        result.append(value[0][1:-1] + self.delimiter)
                _i += 1
            f.write(''.join(result))
        return True

    def parse(self):
        self._try_to_get_file(self.file, 'json')
        self._write_to_file()
        return True


if __name__ == "__main__":
    converter = Converter('test.csv', ';')
    print(f'file = {converter.file}, delimiter = {converter.delimiter}')
    converter2 = Converter('comma.csv', ',')
    print(f'file = {converter2.file}, delimiter = {converter2.delimiter}')
    converter2.parse()
