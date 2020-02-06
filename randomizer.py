from random import randrange

random_elements = {1:"a", 2:"b", 3:"c", 4:"d", 5:"e",
                   6:"Q", 7:"D", 8:"P", 9:"Zz", 10:"Op",
                   11:"`", 12:"?", 13:"=", 14:"-", 15:"!"}
    

def get_random_key(number=3):
    key = ""
    for i in range(number):
       key += random_elements[randrange(1, 16)]
    return key

