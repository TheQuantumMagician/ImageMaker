#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3
#
# cli_thinner.py
#
# A program to apply Guo-Hall thinning to a gradient file.
#
# Based on cli_sobel.py
#
# 20230602 smb  @TheQuantumMagician - Started
# 20230603 smb  @THeQuantumMagician - Added display and file save functionality.
# 20230604 smb  @THeQuantumMagician - Added thinning pass display.
#

import argparse
import json

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from datetime import date
from pathlib import Path
from PIL import Image
from os.path import exists

from matplotlib.colors import LinearSegmentedColormap

# Constants
# maximum color brightness
MAX_COLOR = 255
# maximum palette length
MAX_PLEN = 256
# default background
BACKGROUND = (0, 0, 0, 255)
# useful colors
BLACK = (0, 0, 0)
WHITE = (MAX_COLOR, MAX_COLOR, MAX_COLOR)


def palette(cm):
    # Create a MAX_PLEN length palette from a colormap
    ncColors = []

    for c in range(MAX_PLEN):
        color = cm(c / MAX_COLOR)
        r = int(color[0] * MAX_COLOR)
        g = int(color[1] * MAX_COLOR)
        b = int(color[2] * MAX_COLOR)
        ncColors.append((r, g, b))

    return(ncColors)


def thinningGuoHallIteration(gradients, passNumber):
    # Do a thinning pass on a gradients matrix
    # gradients is a ndarray of booleans
    # passNumber = 0 for first pass, 1 for second pass
    print("passNumber:", passNumber)
    marker = np.zeros(gradients.shape).astype(bool)

    for x in range(1, gradients.shape[0] - 1):
        for y in range(1, gradients.shape[1] - 1):
            p2 = gradients[x, y - 1]
            p3 = gradients[x + 1, y - 1]
            p4 = gradients[x + 1, y]
            p5 = gradients[x + 1, y + 1]
            p6 = gradients[x, y + 1]
            p7 = gradients[x - 1, y + 1]
            p8 = gradients[x - 1, y]
            p9 = gradients[x - 1, y - 1]

            ca = 1 if ((not p2) and (p3 or p4)) else 0
            cb = 1 if ((not p4) and (p5 or p6)) else 0
            cc = 1 if ((not p6) and (p7 or p8)) else 0
            cd = 1 if ((not p8) and (p9 or p2)) else 0
            c = ca + cb + cc + cd

            n1a = 1 if (p9 or p2) else 0
            n1b = 1 if (p3 or p4) else 0
            n1c = 1 if (p5 or p6) else 0
            n1d = 1 if (p7 or p8) else 0
            n1 = n1a + n1b + n1c + n1d

            n2a = 1 if (p2 or p3) else 0
            n2b = 1 if (p4 or p5) else 0
            n2c = 1 if (p6 or p7) else 0
            n2d = 1 if (p8 or p9) else 0
            n2 = n2a + n2b + n2c + n2d

            n = min(n1, n2)

            if passNumber == 0:
                m = (p6 or p7 or (not p9)) and p8
            else:
                m = (p2 or p3 or (not p5)) and p4

            if (c == 1) and (n == 2 or n == 3) and (not m):
                # clear the gradient at this location
                marker[x, y] = False
            else:
                # keep the gradient at this location
                marker[x, y] = True

    masked = np.logical_and(gradients, marker)

    return masked


def thinningGuoHall(gradients, th, saveBase, displayPasses):
    # gradients is an ndarray of gradient values
    # th is the threshhold above which to use
    def dump(bArray, name, saveFile):

        im = Image.new('RGB', bArray.shape, BACKGROUND)
        pixels = im.load()
        for x in range(im.size[0]):
            for y in range(im.size[1]):
                if bArray[x, y]:
                    pixels[x, y] = WHITE
        im.show()

        if saveFile:
            im.save(saveBase + ".jpg", format="JPEG", quality=95)

            fmFP = open(saveBase + ".npy", "wb")
            np.save(fmFP, bArray)

    shape = gradients.shape
    gradientBools = np.zeros(shape).astype(bool)

    for x in range(shape[0]):
        for y in range(shape[1]):
            if gradients[x, y] > th:
                gradientBools[x, y] = True


    limit = 0
    while True:
        print("limit:", limit)
        pass0 = thinningGuoHallIteration(gradientBools, 0)
        pass1 = thinningGuoHallIteration(pass0, 1)
        diff = np.logical_xor(pass1, gradientBools)
        countTrue = diff.astype(int).sum()

        if displayPasses:
            dump(pass1, saveBase + "_pass_" + str(limit), False) 

        if countTrue == 0:
            break

        if limit > 64:
            break
        else:
            limit += 1

        gradientBools = pass1.copy()

    dump(gradientBools, saveBase + "_" + str(limit), True)

    finalMask = np.zeros(shape).astype(int)
    for x in range(gradientBools.shape[0]):
        for y in range(gradientBools.shape[1]):
            if gradientBools[x, y]:
                finalMask[x, y] = gradients[x, y]

    return(finalMask)

if __name__ == '__main__':
    print("Start now:",  str(datetime.now()))

    # Instantiate the command line parser
    parser = argparse.ArgumentParser(description="cli_thinner: Guo-Hall line thinning")

    # Add in all the command line arguments the program recognizes
    # Optional argument for filename (defaults to 'test.jpg')
    parser.add_argument('--fn',
                        action="store",
                        dest="fn",
                        help="image filename",
                        default="test.npy"
                        )


    # Optional argument for posterization palette (defaults to hsv)
    parser.add_argument('--pn',
                        action="store",
                        dest="pn",
                        help="line display palette name",
                        default="hsv"
                        )

    # Optional argument for edge threshhold (defaults to 8)
    parser.add_argument('--th',
                        type=int,
                        help="gradient threshhold",
                        default = 8
                        )

    # Optional argument to display each thining pass
    parser.add_argument('--dt', action='store_true', help="display each thinning pass")

    args = parser.parse_args()
    print("fn\t", args.fn)
    print("pn\t", args.pn)
    print("th\t", args.th)
    print("dt\t", args.dt)

    # Build image save filename strings
    # All files saved into a directory named from today's date (YYYYMMDD)
    today = date.today()
    saveDirStr = "./" + today.__format__("%Y%m%d")
    saveDir = Path(saveDirStr)

    # Create the save directory if it doesn't exist
    if not saveDir.exists():
        print("The save directory:", saveDirStr, "does not exist.")
        print("Creating save directory.")
        # NOTE: not doing this in a try/except block, because w/o save directory,
        #       it's not worth doing all the calculations for the images
        saveDir.mkdir()

    # Build the base file name strings (YYYYMMDD_FN_, and YYYYMMDD_FN_PN_TH_)
    fn = args.fn.split(".")
    saveBase = saveDirStr + "/"
    saveBase += today.__format__("%Y%m%d") + "_"
    saveBase += fn[0]
    saveThBase = saveBase  + str(args.th) + "_"
    savePalBase = saveBase  + args.pn + "_"
    savePalThBase = savePalBase  + str(args.th) + "_"

    gPath = Path(args.fn)
    gradients = None
    if gPath.exists():
        # Create the working palette(s)
        colors = []

        # Test for custom palette
        cpPath = Path(args.pn)
        if cpPath.exists():
            # It's a file,read in the JSONized palette
            cpFP = open(args.pn)
            pData = json.load(cpFP)

            # convert JSON lists to tuples for the palette
            for d in pData:
                colors.append(tuple(d))

            # strip .json extension from palette name
            args.pn = args.pn.split('.')[0]
        else:
            # Use MatPlotLib colormap to query colormap for colors, save in look up tables
            cm = plt.cm.get_cmap(args.pn)

            # poster and grayscale lookup tables
            colors = palette(cm)

        # Drop all zero value pixels
        colors[0] = BLACK

        gpFP = open(args.fn, "rb")
        gradients = np.load(gpFP)
        print(str(datetime.now()), "Using gradient file:", args.fn)

# experimental -- normalize the gradients
        maxR = np.max(gradients)
        norm = np.zeros(gradients.shape).astype(int)
        normIm = Image.new("RGB", gradients.shape, BACKGROUND)
        normPixels = normIm.load()

        for x in range(gradients.shape[0]):
            for y in range(gradients.shape[1]):
                norm[x, y] = int((gradients[x, y] / maxR) * MAX_COLOR)
                normPixels[x, y] = colors[norm[x, y]]

        normIm.show()
        normIm.save(savePalBase + "norm.jpg", "JPEG", quality=95)

        finalMask = thinningGuoHall(norm, args.th, saveBase, args.dt)

        maxFM = np.max(finalMask)
        minFM = np.min(finalMask)
        print(minFM, maxFM)
# end experimental
#        finalMask = thinningGuoHall(gradients, args.th, saveBase, args.dt)
        fmFP = open(saveBase + ".npy", "wb")
        np.save(fmFP, finalMask)


        # Now, use the palette, and the the thinned gradients to make an image
        im = Image.new("RGB", finalMask.shape, BACKGROUND)
        pixels = im.load()

        for x in range(finalMask.shape[0]):
            for y in range(finalMask.shape[1]):
                pixels[x, y] = colors[finalMask[x, y]]

        im.show()
        im.save(savePalThBase + "thin.jpg", "JPEG", quality=95)                

    else:
        print("The gradient file", args.fn, "does not exist.")
