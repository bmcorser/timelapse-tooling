import os
from multiprocessing import Pool
from subprocess import call
import stopwatch

from utils import files


def render_jpg(file_):
    outdir = 'jpg'
    jpg_path = os.path.join(outdir, file_.replace('cr2', 'jpg'))
    cmd = [
        'ufraw-batch',
        '--out-type=jpg',
        '--compression=100',
        "--out-path={0}".format(outdir),
        # "--conf={0}".format(file_.replace('cr2', 'ufraw')),
        '--clip=film',
        "./{0}".format(file_),
        '--silent',
        '--overwrite',
    ]
    returncode = call(cmd)
    if returncode == 0 and os.path.exists(jpg_path):
        os.remove(file_)
    return "{0} written".format(jpg_path)


if __name__ == '__main__':
    t = stopwatch.Timer()
    pool = Pool(8)
    raw_files = files('cr2')
    num = len(raw_files)
    for pos, ret in enumerate(pool.imap_unordered(render_jpg, raw_files)):
        pos += 1
        fmt_string = "{0}/{1} ({2:.3f}%) done"
        print(fmt_string.format(pos + 1, num, ((pos + 1) / float(num)) * 100))
    pool.close()
    pool.join()
    print t.elapsed
