from subprocess import check_call
import os, shutil
from celery import Celery
from utils import enough_space
from render import render_jpg


queue_opts = {
    'backend': 'redis://localhost',
    'broker': 'amqp://guest@localhost//',
}

queue = Celery('queue', **queue_opts)


@queue.task(bind=True)
def copy(self, R):
    target = os.path.join(R['targetdir'], R['file_'])
    destination = R['copydir']
    while not enough_space(target, destination):
        self.retry(countdown=10)
    check_call(['cp', target, destination])
    return R


@queue.task
def render(R):
    render_jpg(R)
    return R


@queue.task
def rm_internal(R):
    os.remove(os.path.join(R['copydir'], R['file_']))
    return R


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
    shutil.rmtree(R['targetdir'])
    shutil.rmtree(R['copydir'])
    return R
