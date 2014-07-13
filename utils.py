import os


def files(type_):
    return sorted(filter(lambda x: x.endswith(type_), os.listdir('.')))


def int_file(filename):
    return (int(filename.split('.')[0].replace('capt', '')), filename)


def pairs(iterable):
    return zip(iterable[0::2], iterable[1::2])


def mount_of(path):
    'Return the mountpoint for a given path.'
    path = os.path.realpath(os.path.abspath(path))
    while path != os.path.sep:
        if os.path.ismount(path):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    return path


def enough_space(target, destination):
    'Is there enough space on the destination drive for the target file?'
    avail = os.statvfs(mount_of(destination)).f_bavail - (4096 * 500)
    return avail > os.stat(target).st_size
