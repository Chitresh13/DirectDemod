"""
merger of NOAA satellite images
"""

import argparse
import os

from osgeo import gdal
from directdemod import constants

"""
This class provides an API for merging multiple images.
It extracts needed information and projects images on mercator
projection.
"""


def build_vrt(vrt, files, resample_name):

    """builds .vrt file which will hold information needed for overlay

    Args:
        vrt (:obj:`string`): name of vrt file, which will be created
        files (:obj:`list`): list of file names for merging
        resample_name (:obj:`string`): name of resampling method
    """

    options = gdal.BuildVRTOptions(srcNodata=0)
    gdal.BuildVRT(destName=vrt, srcDSOrSrcDSTab=files, options=options)
    add_pixel_fn(vrt, resample_name)


def add_pixel_fn(filename, resample_name):

    """inserts pixel-function into filename

    Args:
        filename (:obj:`string`): name of file, into which the function will be inserted
        resample_name (:obj:`string`): name of resampling method
    """

    header = """  <VRTRasterBand dataType="Byte" band="1" subClass="VRTDerivedRasterBand">"""
    contents = """
    <PixelFunctionType>{0}</PixelFunctionType>
    <PixelFunctionLanguage>Python</PixelFunctionLanguage>
    <PixelFunctionCode><![CDATA[{1}]]>
    </PixelFunctionCode>"""

    lines = open(filename, 'r').readlines()
    lines[3] = header  # FIX ME: 3 is a hand constant, if created file doesn't start match it, there will be an error
    lines.insert(4, contents.format(resample_name, get_resample(resample_name)))
    open(filename, 'w').write("".join(lines))


def get_resample(name):

    """retrieves code for resampling method

    Args:
        name (:obj:`string`): name of resampling method

    Returns:
        method :obj:`string`: code of resample method
    """

    methods = {
        "first": None,
        "last": None,
        "min": None,
        "max": None,
        "med": None,
        "average": """
import numpy as np

def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
    div = np.zeros(in_ar[0].shape)
    for i in range(len(in_ar)):
        div += (in_ar[i] != 0)
    div[div == 0] = 1
    
    y = np.sum(in_ar, axis = 0, dtype = 'uint16')
    y = y / div
    
    np.clip(y,0,255, out = out_ar)
"""
    }

    if name not in methods:
        raise ValueError("ERROR: Unrecognized resampling method (see documentation): '{}'.".format(name))

    return methods[name]


def merge(files, output_file, resample="average"):

    """merges list of files using specific resample method for overlapping parts

    Args:
        files (:obj:`string`): list of files to merge
        output_file (:obj:`string`): name of output file
        resample (:obj:`string`): name of resampling method
    """

    build_vrt(constants.TEMP_VRT_FILE, files, resample)

    gdal.SetConfigOption('GDAL_VRT_ENABLE_PYTHON', 'YES')

    gdal.Translate(destName=output_file,
                   srcDS=constants.TEMP_VRT_FILE)

    gdal.SetConfigOption('GDAL_VRT_ENABLE_PYTHON', None)

    if os.path.isfile(constants.TEMP_VRT_FILE):
        os.remove(constants.TEMP_VRT_FILE)


def main():
    """CLI interface for satellite image merger"""

    parser = argparse.ArgumentParser(description="Merger option parser")
    parser.add_argument("-f", "--files", required=True, help="List of files to merge", nargs="+")
    parser.add_argument("-o", "--output", required=True, help="Name of output file")
    parser.add_argument("-r", "--resample", required=False, help="Resample algorithm", default="average")

    args = parser.parse_args()

    if args.files is None:
        raise ValueError("ERROR: No input files passed.")

    if len(args.files) == 1:
        raise ValueError("ERROR: Merger takes at least 2 files, but 1 was given: {0}".format(args.files[0]))

    merge(args.files, output_file=args.output, resample=args.resample)


if __name__ == '__main__':
    main()
