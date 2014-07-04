import os


def files(type_):
    return sorted(filter(lambda x: x.endswith(type_), os.listdir('.')))

def int_file(filename):
    return (int(filename.split('.')[0].replace('capt', '')), filename)

def pairs(iterable):
    return zip(iterable[0::2], iterable[1::2])
