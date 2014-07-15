from copy import deepcopy
import os
import click
from celery import chain, group

from queue import setup_task, copy_render_rm, ffmpeg

EXTPATH = os.environ.get('TL_EXTPATH',
                         '/home/ben/external/video/timelapse')
INTPATH = os.environ.get('TL_INTPATH',
                         '/home/ben/timelapse')


def send_messages(R, cr2_list):
    render_tasks = list()
    for cr2 in cr2_list:
        R_ = deepcopy(R)
        R_.update({'file_': cr2})
        render_tasks.append(copy_render_rm.si(R_))

    click.echo(chain(setup_task.s(R), group(render_tasks), ffmpeg.s())())


def run_test(R, cr2_list):
    setup_task(R)
    render_tasks = list()
    for cr2 in cr2_list:
        R_ = deepcopy(R)
        R_.update({'file_': cr2})
        render_tasks.append(copy_render_rm(R_))
    ffmpeg(render_tasks)


@click.command()
@click.argument('date')
@click.option('--test', is_flag=True)
def cli(date, test):
    targetdir = os.path.join(EXTPATH, date)
    output = os.path.join(EXTPATH, "{0}-prores-qscale5-full.mov".format(date))
    copydir = os.path.join(INTPATH, date)
    renderdir = os.path.join(copydir, 'jpg')
    try:
        os.makedirs(renderdir)
    except OSError as exc:
        if exc.errno != 17:
            raise
    cr2_list = filter(lambda f: f.endswith('cr2'), os.listdir(targetdir))[:30]
    click.echo("Processing {0} images for {1}".format(len(cr2_list), date))

    R = {
        'date': date,
        'targetdir': targetdir,
        'copydir': copydir,
        'renderdir': renderdir,
        'output': output,
    }
    if test is False:
        send_messages(R, cr2_list)
    elif test is True:
        run_test(R, cr2_list)


if __name__ == '__main__':
    cli()
