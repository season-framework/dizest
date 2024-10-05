import string as _string
import random as _random
import datetime

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

def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d %H:%M:%S') 
    return str(value)