from subprocess import check_call
import os
import shutil
from celery import Celery
from utils import enough_space
from render import render_jpg


queue_opts = {
    'backend': 'redis://localhost',
    'broker': 'amqp://guest@localhost//',
}

queue = Celery('queue', **queue_opts)


@queue.task
def copy_render_rm(R):
    check_call(['cp', os.path.join(R['targetdir'], R['file_']), R['copydir']])
    render_jpg(R)
    os.remove(os.path.join(R['copydir'], R['file_']))
    return R


@queue.task(bind=True)
def setup_task(self, R):
    while not enough_space(R['targetdir'], R['copydir']):
        self.retry(countdown=30, max_retries=None)
    return True


@queue.task
def ffmpeg(Rs):
    R = Rs[0]
    cmd = ('/home/ben/bin/ffmpeg',
           '-threads', '8',
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
    # shutil.rmtree(R['copydir'])
    return R
