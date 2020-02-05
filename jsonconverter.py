import os
from filemanager import FileManager
from converterexceptions import *
import io
import tokenize
from operator import itemgetter


class Converter:

    delimiter = ''
    file = ''

    def __new__(cls, file, delimiter=','):
        cls.delimiter = delimiter
        if file.endswith(".csv"):
            cls.file = file
            return CsvToJson()
        elif file.endswith(".json"):
            cls.file = file
            return JsonToCsv()
        else:
            raise FileExtensionError(
                'Wrong extension. File must be end with .json or .csv')

    @classmethod
    def _get_header(cls):
        """
           parse first line of .csv file to list of headers if cls.file is .csv
           else parse first json object left part if it's .json file
           input: cls.file
           output: list of headers"""

        raise NotImplementedError

    @classmethod
    def _get_values(cls):
        raise NotImplementedError

    @classmethod
    def parse(cls):
        raise NotImplementedError

    @classmethod  # Fix opportunity to change extencion after creating
    def _try_to_get_file(cls, file, caused=None):
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
            cls.file = input("File doesn't exist. Choose another file : ").split(".")[
                0] + f'.{caused}'
            cls._try_to_get_file(cls.file, caused)
            return True

        except FileIsEmptyError:
            cls.file = input("File is empty. Choose another file : ").split(".")[
                0] + f'.{caused}'
            cls._try_to_get_file(cls.file, caused)

        except FileExtensionError:
            cls.file = input("File you chose has wrong extension. Choose another file : ").split(
                ".")[0] + f'.{caused}'
            cls._try_to_get_file(cls.file, caused)
            return True

    @classmethod
    def _create_file(cls, caused=None):
        """Validate file creation. 
           Fixes file extencion if it's wrong."""

        _file = input('Enter name of file to write :').split(".")[0]
        if caused == "csv":  # if it's caused from CsvToJson - create .json file
            _file += ".json"
        else:
            _file += ".csv"
        try:
            with FileManager(_file, 'x'):
                pass
        except FileIsAlreadyExistError:
            print('File is already exist. Choose another one')
            cls._create_file(caused)
        return _file


class CsvToJson(Converter):
    def __new__(cls):
        return cls

    @classmethod
    def _get_header(cls):
        with FileManager(cls.file, 'r') as f:
            _headers = f.readline().rstrip().split(sep=cls.delimiter)
            return _headers

    # @classmethod
    # def _get_line(cls, line):
    #     def tokenize_string(line):
    #         tokens = tokenize.tokenize(io.BytesIO(line.strip().encode()).readline)
    #         next(tokens)  # skip encoding token
    #         return list(filter(None, map(itemgetter(1), tokens)))  # filter ENDMARKER
    #     return [x for x in tokenize_string(line) if x != ',' and x != ';']

    @classmethod
    def _get_values_with_semicolon_delimeter(cls):
        _headers = cls._get_header()
        _values = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines()[1:]:
                result = '\n'
                for i, item in enumerate(line.strip("\n").split(cls.delimiter), 0):

                    if not item.strip().isdigit():
                        result += '\t"' + _headers[i] + \
                            '":"' + item.strip() + '",\n'
                    else:
                        result += '\t"' + _headers[i] + \
                            '":' + item.strip() + ",\n"
                _values.append(result)
            return _values

    
    @classmethod
    def _recursive_filter(cls, line, result=None):
        line = line.replace('""', '')
        try:
            if not result:
                result = []
            line = line.strip()
            if line.startswith('"'):
                temp = ''
                i = 0
                while line[i+1] != '"':
                    temp += line[i]
                    i += 1
                else:
                    temp += f'{line[i]}"'
                    result.append(temp)
                    line = line[len(temp):].strip(', ')
                    cls._recursive_filter(line, result)
            else:
                temp = ''
                i = 0
                while line[i] != ',':
                    temp += line[i]
                    i += 1
                else:
                    temp += ','
                    result.append(temp)
                    line = line[len(temp):]
                    cls._recursive_filter(line, result)
            return [x.strip(', "') for x in result]
        except IndexError:
            if temp:
                result.append(temp)

    @classmethod
    def _get_values_with_comma_delimeter(cls):
        _headers = cls._get_header()
        _values = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines()[1:]:
                result = '\n'
                for i, item in enumerate(cls._recursive_filter(line), 0):
                    if not item.strip().isdigit():
                        result += '\t"' + _headers[i] + \
                            '":"' + item.strip() + '",\n'
                    else:
                        result += '\t"' + _headers[i] + \
                            '":' + item.strip() + ",\n"
                _values.append(result)
            return _values




    @classmethod
    def _get_all_data(cls):
        if cls.delimiter == ';':
            _values = cls._get_values_with_semicolon_delimeter()
        else:
            _values = cls._get_values_with_comma_delimeter()
        _result = '[\n'
        _end = '\n]'
        for i in range(len(_values)):
            if i == len(_values)-1:
                # if it's last value - no need to put comma
                _result += "\t{"+str(_values[i])[:-1]+"\n\t}"
            else:
                # elif it's not - put comma
                _result += "\t{"+str(_values[i])[:-1]+"\n\t},\n"
        _result += _end
        return _result

    @classmethod
    def parse(cls):
        cls._try_to_get_file(cls.file, 'csv')
        _data = cls._get_all_data()
        with FileManager(cls._create_file("csv"), 'w') as f:
            f.write(_data)
        return True


class JsonToCsv(Converter):
    def __new__(cls):
        return cls

    @classmethod
    def _get_header(cls):
        _not_valid = ['{\n', '}\n', '[\n']
        _headers = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _not_valid):
                    if '},' in line:
                        return _headers
                    _headers.append(line.split(':')[0].strip('\t"'))
        return _headers

    @classmethod
    def _get_values(cls):
        _not_valid = ['{\n', '},\n,', '}', '[', ']']
        _header_len = len(cls._get_header())
        _values = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _not_valid) and not line == ',\n':
                    _values.append([line.split(':')[-1].strip('\t\n, ')])
        return _values

    @classmethod
    def _write_to_file(cls):
        _header = cls._get_header()
        _header_len = len(cls._get_header())
        _values = cls._get_values()
        result = []

        with FileManager(cls._create_file("json"), 'w') as f:
            f.write(cls.delimiter.join(_header) + '\n')
            _i = 0
            for value in _values:
                # if element is last in line go next line
                if not _i == 0 and (_i + 1) % _header_len == 0:
                    if value[0].isdigit():
                        result.append(value[0] + '\n')
                    else:
                        result.append(value[0][1:-1] + '\n')
                else:
                    if value[0].isdigit():
                        result.append(value[0] + cls.delimiter)
                    else:
                        result.append(value[0][1:-1] + cls.delimiter)
                _i += 1
            f.write(''.join(result))
        return True

    @classmethod
    def parse(cls):
        cls._try_to_get_file(cls.file, 'json')
        cls._write_to_file()
        return True


if __name__ == "__main__":
    k = Converter('comma.csv', ',')
    k.parse()
