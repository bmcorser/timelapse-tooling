import os
from multiprocessing import Pool
from subprocess import check_call

from utils import files


def render_jpg(R):
    return R


if __name__ == '__main__':
    pool = Pool(8)
    raw_files = files('cr2')
    num = len(raw_files)
    for pos, ret in enumerate(pool.imap_unordered(render_jpg, raw_files)):
        pos += 1
        fmt_string = "{0}/{1} ({2:.3f}%) done"
        print(fmt_string.format(pos + 1, num, ((pos + 1) / float(num)) * 100))
    pool.close()
    pool.join()
