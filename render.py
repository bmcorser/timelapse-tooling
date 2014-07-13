import os
from multiprocessing import Pool
from subprocess import check_call

from utils import files


def render_jpg(R):
    cmd = [
        'ufraw-batch',
        '--out-type=jpg',
        '--compression=100',
        "--out-path={0}".format(R['renderdir']),
        # "--conf={0}".format(file_.replace('cr2', 'ufraw')),
        '--clip=film',
        os.path.join(R['copydir'], R['file_']),
        '--silent',
        '--overwrite',
    ]
    check_call(cmd)
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
