import string as _string
import random as _random

def random(length=12):
    string_pool = _string.ascii_letters + _string.digits
    result = ""
    for i in range(length):
        result += _random.choice(string_pool)
    return result

def addtabs(v, size=1):
    for i in range(size):
        v =  "    " + "\n    ".join(v.split("\n"))
    return v