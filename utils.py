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
    '''
    Is there enough space on the destination drive for the target? Target can
    be a file or a directory.
    '''
    if os.path.isfile(target):
        target_size = os.stat(target).st_size
    elif os.path.isdir(target):
        target_size = dir_size(target)
    fs = os.statvfs(mount_of(destination))
    avail = (fs.f_bavail * fs.f_frsize) / 1024
    return avail > ((target_size / 1024) + 102400)


def dir_size(directory):
    'Return the sum of the sizes of all files in a directory'
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, filename))
    return total_size
