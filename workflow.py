from copy import deepcopy
import os
import click
from celery import chain, chord

from queue import copy, render, ffmpeg, rm_internal

EXTPATH = os.environ.get('TL_EXTPATH',
                         '/home/ben/external/video/timelapse')
INTPATH = os.environ.get('TL_INTPATH',
                         '/home/ben/timelapse')

def _target(date, file_):
    return os.path.join(INTPATH, file_)

@click.command()
@click.argument('date')
def cli(date):
    targetdir = os.path.join(EXTPATH, date)
    output = os.path.join(EXTPATH, "{0}-prores-qscale5-full.mov".format(date))
    copydir = os.path.join(INTPATH, date)
    renderdir = os.path.join(copydir, 'jpg')
    try:
        os.makedirs(renderdir)
    except OSError as exc:
        if exc.errno != 17:
            raise
    cr2_list = filter(lambda f: f.endswith('cr2'), os.listdir(targetdir))
    click.echo("Processing {0} images for {1}".format(len(cr2_list), date))

    R = {
        'date': date,
        'targetdir': targetdir,
        'copydir': copydir,
        'renderdir': renderdir,
        'output': output,
    }

    render_tasks = list()
    for cr2 in cr2_list:
        R_ = deepcopy(R)
        R_.update({'file_': cr2})
        render_tasks.append(chain(copy.s(R_), render.s(), rm_internal.s()))

    click.echo(chord(render_tasks)(ffmpeg.s()))


if __name__ == '__main__':
    cli()
