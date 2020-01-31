import os
from abc import abstractmethod, ABC


class FileExtensionError(Exception):
    def __init__(self, text):
        self.text = text


class FileIsAlreadyExistError(Exception):
    def __init__(self, text):
        self.text = text


class FileIsEmptyError(Exception):
    def __init__(self, text):
        self.text = text


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


#VVESTI DELIMETR, ZAMENIT' V SPLITAH , AND ; NA DELIMETR
class Converter:

    file = ''

    def __new__(cls, file):
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
        raise NotImplementedError

    @classmethod
    def _get_values(cls):
        raise NotImplementedError

    @classmethod
    def parse(cls):
        raise NotImplementedError

    @classmethod    #Fixup re-writing cls.file if it's scv and user wrote json 
    def _try_to_get_file(cls, file):
        try:
            if not os.path.exists(file):
                raise FileExistsError("File doesn't exist")
            elif os.stat(file).st_size == 0:
                raise FileIsEmptyError("File is empty")
            else:
                return True
        except FileExistsError:
            cls.file = input("File doesn't exist. Choose another file : ")
            cls._try_to_get_file(cls.file)

            return True  

        except FileIsEmptyError:
            cls.file = input("File is empty. Choose another file : ")
            cls._try_to_get_file(cls.file)

            return True


class CsvToJson(Converter):
    def __new__(cls):
        return cls

    @classmethod
    def _get_header(cls):
        with FileManager(cls.file, 'r') as f:
            _headers = f.readline().rstrip().split(sep=',')
            return _headers

    @classmethod
    def _get_values(cls):
        pass

    @classmethod
    def parse(cls):
        cls._try_to_get_file(cls.file)
        return cls._get_header()


class JsonToCsv(Converter):
    def __new__(cls):
        return cls

    @classmethod
    def _get_header(cls):
        _non_validate = ['{\n', '}\n']
        _headers = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _non_validate):
                    _headers.append(line.split(':')[0].strip('\t"'))
                elif '}' in line:
                    break
        return _headers
    
    @classmethod
    def _get_values(cls):
        _non_validate = ['{\n', '},\n,' ,'}']
        _header_len = len(cls._get_header())
        _values = []
        with FileManager(cls.file, 'r') as f:
            for line in f.readlines():
                if not any(item in line for item in _non_validate) and not line == ',\n':
                    _values.append([line.split(':')[-1].strip('\t\n,')])
        return _values
    
    @classmethod
    def _write_to_file(cls):
        _len_of_headers = len(cls._get_header())
        _values = cls._get_values()
        result = []

        file = input("Enter name of .csv file ")
        with FileManager(file, 'x') as f:
            f.write(','.join(_header) + '\n')
            _i = 0 
            for value in _values:
                if not _i == 0 and (_i+1) % _len_of_headers == 0:
                    result.append(value[0][1:-1] + '\n')
                else: 
                    result.append(value[0][1:-1] + ';')
                _i += 1
            f.write(''.join(result))
        return True



    @classmethod
    def parse(cls):
        cls._try_to_get_file(cls.file)
        cls._write_to_file()
        return True


if __name__ == "__main__":
    k = Converter('finally.json')
    print(k.parse())
