from subprocess import check_call
import os
import shutil
from celery import Celery
from utils import enough_space


queue_opts = {
    'backend': 'redis://localhost',
    'broker': 'amqp://guest@localhost//',
}

queue = Celery('queue', **queue_opts)


@queue.task(bind=True)
def copy_render_rm(self, R):
    target = os.path.join(R['targetdir'], R['file_'])
    destination = os.path.join(R['copydir'], R['file_'])
    render = [
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
    while not enough_space(R['targetdir'], R['copydir']):
        self.retry(countdown=30, max_retries=None)
    jpg_filename = R['file_'].replace('cr2', 'jpg')
    if not os.path.exists(os.path.join(R['renderdir'], jpg_filename)):
        check_call(['cp', target, destination])
        check_call(render)
        os.remove(os.path.join(R['copydir'], R['file_']))
        print("{0}/{1} rendered".format(R['date'], R['file_']))
        return R
    print("{0}/{1} found".format(R['date'], R['file_']))
    return R


@queue.task
def ffmpeg(Rs):
    R = Rs[0]
    cmd = ('/home/ben/bin/ffmpeg',
           # '-threads', '8',
           '-r', '48',
           '-y',
           '-pattern_type', 'glob',
           '-i', "{0}/capt*.jpg".format(R['renderdir']),
           '-c:v', 'prores_ks',
           '-profile:v', '3',
           '-qscale:v', '5',
           '-vendor', 'ap10',
           R['output'])
    check_call(cmd)
    # shutil.rmtree(R['targetdir'])
    shutil.rmtree(R['copydir'])
    print("{0} video rendered".format(R['date']))
    return R
