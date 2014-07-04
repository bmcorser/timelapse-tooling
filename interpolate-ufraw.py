import os
import pandas
from lxml import etree
from decimal import Decimal

from utils import files, int_file, pairs


_keys = map(int_file, files('ufrawkey'))
_frames = dict(map(int_file, files('cr2')))

exposure_keys = list()
basemanualcurve_keys = list()
manualcurve_keys = list()


def curve_anchors(tree, curve_name):
    anchors = list()
    for anchorxy in tree.find(curve_name).iterchildren():
        X, Y = anchorxy.text.split()
        anchors.extend([Decimal(X), Decimal(Y)])
    return anchors

for int_, filename in sorted(_keys):
    with open(filename) as keyframe_file:
        contents = keyframe_file.read()
        parser = etree.XMLParser()
        parser.feed(contents)
        tree = parser.close()
        exposure_keys.append(
            (int(int_), Decimal(tree.find('Exposure').text)))
        basemanualcurve_keys.append(
            (int(int_), curve_anchors(tree, 'BaseManualCurve')))
        manualcurve_keys.append(
            (int(int_), curve_anchors(tree, 'ManualCurve')))


exposure_series = pandas.Series([None for _ in range(len(_frames))], dtype=float)
for exposure_idx, exposure in exposure_keys:
    exposure_series[exposure_idx] = exposure
interpolated_exposure = exposure_series.interpolate(method='spline', order=4)


def interpolate_curve(curve_keys):
    width = max([len(x[1]) for x in basemanualcurve_keys])
    columns = [chr(65+x) for x in range(width)]
    keys_data = [x[1] for x in basemanualcurve_keys]
    df_keys = pandas.DataFrame(index=[x[0] for x in basemanualcurve_keys],
                               columns=columns,
                               data=keys_data)
    frames_data = len(_frames) * [[None for _ in range(width)]]
    df_frames = pandas.DataFrame(index=map(int, sorted(_frames.keys())),
                                 columns=columns,
                                 data=frames_data)
    for keyframe_idx in df_keys.index:
        df_frames.ix[keyframe_idx] = df_keys.ix[keyframe_idx]
    return df_frames

interpolated_basemanualcurve = interpolate_curve(basemanualcurve_keys)
interpolated_manualcurve = interpolate_curve(manualcurve_keys)
def element_anchors(curve_element, anchors):
    curve_element.clear()
    for x, y in anchors:
        anchor_element = etree.Element('AnchorXY')
        anchor_element.text = "{0} {1}".format(x, y)
        curve_element.append(anchor_element)


for frame_idx, filename in _frames.iteritems():
    with open(filename.replace('cr2', 'ufraw'), 'w') as file_:
        exposure = interpolated_exposure.ix[frame_idx]
        basemanualcurve_anchors = pairs(interpolated_basemanualcurve.ix[frame_idx])
        manualcurve_anchors = pairs(interpolated_manualcurve.ix[frame_idx])
        basemanualcurve_element = tree.find('BaseManualCurve')
        element_anchors(basemanualcurve_element, basemanualcurve_anchors)
        manualcurve_element = tree.find('ManualCurve')
        element_anchors(manualcurve_element, manualcurve_anchors)
        tree.find('Exposure').text = str(exposure)
        tree.find('InputFilename').text = os.path.abspath(filename)
        tree.find('OutputFilename').text = os.path.abspath(filename).replace('cr2', 'jpg')
        out_string = etree.tostring(tree, pretty_print=True)
        file_.write(out_string)
