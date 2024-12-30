#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3
#
# ImageMaker.py
#
# A program to generate multiple new images from an existing image by, among
# other things, applying sobel filter generated edges and custom color palettes
# to the input image. Optionally apply a watermark.
#
# Based on cli_soble.py
#
# 20231216 smb  @TheQuantumMagician - Started
#


import argparse
import json

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from datetime import date
from pathlib import Path
from PIL import Image
from PIL import ImageColor
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
#BBLACK = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (MAX_COLOR, MAX_COLOR, MAX_COLOR)
# max_cDist is the greatest distance between colors
# (distance between black and white, so sqrt((255 * 255) * 3) + 1))
MAX_CDIST = 443


def nearest(pixel, palette):
    # find the color in the palette closest to the original pixel color
    ncDist = MAX_CDIST
    ncColor = (255, 255, 255)
    for color in palette:
        rDist = abs(pixel[0] - color[0])
        gDist = abs(pixel[1] - color[1])
        bDist = abs(pixel[2] - color[2])
#        tmpDist = ((rDist * rDist) + (gDist * gDist) + (bDist * bDist))**0.5
#        tmpDist = ((rDist * rDist) + (gDist * gDist) + (bDist * bDist))
        tmpDist = rDist + gDist + bDist
        if tmpDist < ncDist:
            ncDist = tmpDist
            ncColor = color
   
    return ncColor


# Create custom matplotlib cdict from a list of colors
def createCDict(colors, cyclical=False):
    # Create an evenly spaced cdict dictionary from a list of colors
    if cyclical:
        # Want the last color to merge to the first color
        colors.append(colors[1])

    clen = len(colors)
    count = clen - 1
    increment = (1 / count)

    cdict = dict()

    # each keyword in cdict points to a list of lists, start with empty lists
    cdict['red'] = list()
    cdict['green'] = list()
    cdict['blue'] = list()

    # Start with x anchor points
    # NOTE: Each anchor point is a separate list, hence the [] wrappers
    for step in range(clen):
        cdict['red'].append([step * increment])
        cdict['green'].append([step * increment])
        cdict['blue'].append([step * increment])

    # now add in the colors
    # NOTE: duplicates because of colormap dict definition needing yleft, and yright
    for color in range(clen):
        cdict['red'][color].append(colors[color][0] / MAX_COLOR)
        cdict['red'][color].append(colors[color][0] / MAX_COLOR)
        cdict['green'][color].append(colors[color][1] / MAX_COLOR)
        cdict['green'][color].append(colors[color][1] / MAX_COLOR)
        cdict['blue'][color].append(colors[color][2] / MAX_COLOR)
        cdict['blue'][color].append(colors[color][2] / MAX_COLOR)

    return(cdict)


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


def invert(pixel):
    # invert (compliment) the provided pixel

    r = MAX_COLOR - pixel[0]
    g = MAX_COLOR - pixel[1]
    b = MAX_COLOR - pixel[2]

    return((r, g, b))


def get_lum(pixel):
    # Calculate luminosity of an (r, g, b) pixel
    # gray level = 0.3r + 0.59g + 0.11b

    lum = int((0.3 * pixel[0]) + (0.59 * pixel[1]) + (0.11 * pixel[2]))

    return(lum)


def get_luminosities(im, lums, border=0):
    # Calculate the luminosity of every pixel in im inside the border area

    for x in range(border, im.size[0] - border):
        for y in range(border, im.size[1] - border):
            lums[x, y] = get_lum(im.getpixel((x, y)))


# Read or generate luminosity data
def lumData(im, name, bord=0):
    lumPath = Path(name)
    lums = None
    if lumPath.exists():
        lpFP = open(name, "rb")
        lums = np.load(lpFP)
        print(str(datetime.now()), "Using saved file:", name)
    else:
        # Calculate input image pixel luminosities
        lums = np.zeros(im.size).astype(int)
        get_luminosities(im, lums, bord)
        lpFP = open(name, "wb")
        np.save(lpFP, lums)
    lpFP.close()

    return(lums)


def get_av(im, x, y):
    # Calculate the average pixel value of a 3x3 square of pixels
    # centered on x, y
    # NOTE: Does no bounds checking

    r, g, b = 0, 0, 0
    x_range = range(x - 1, x + 2)
    y_range = range(y - 1, y + 2)
    for newX in x_range:
        for newY in y_range:
            pixel = im.getpixel((newX, newY))
            r += pixel[0]
            g += pixel[1]
            b += pixel[2]

    return((int(r / 9), int(g / 9), int(b / 9)))


def processImage(npa, name, palette, save=False, border=0):
    # Create, and possibly display, and possibly save, an image
    # using provided lookup values and palette

    # Create canvas for new image
    newIm = Image.new('RGB', npa.shape, BACKGROUND)
    pixels = newIm.load()

    for x in range(border, npa.shape[0] - border):
        for y in range(border, npa.shape[1] - border):
            try:
                pixels[x, y] = palette[npa[x, y]]
            except:
                print("ERROR: npa[", str(x) + ",", str(y) + "] = ", str(npa[x, y]))

    if save:
        newIm.save(name, format="PNG", quality=95)

    # NOTE: crops border from around generated image
    return(newIm.crop((border, border, npa.shape[0] - border, npa.shape[1] - border)))


# Read saved image, or create if it doesn't exist
def getImage(npa, name, palette, display=False, save=False, bord=0):
    imPath = Path(name)
    im = None
    if imPath.exists():
        # read image
        im = Image.open(name)
        print(str(datetime.now()), "Using saved file:", name)
    else:
        # create image
        im = processImage(npa, name, palette, save, bord)

    if display:
        im.show()

    return(im)


def smoothImage(im, name, save=False, border=0):
    # Create, and possibly display, and possibly save, a smoothed image
    # created by averaging the 3x3 box centerd on each input imagee

    # Create canvas for new image
    newIm = Image.new('RGB', im.size, BACKGROUND)
    pixels = newIm.load()

    for x in range(border, im.size[0] - border):
        for y in range(border, im.size[1] - border):
            pixels[x, y] = get_av(im, x, y)

    if save:
        newIm.save(name, format="PNG", quality=95)

    return(newIm.crop((border, border, im.size[0] - border, im.size[1] - border)))


# Either open or generate the smoothed imagee
def getSmoothImage(im, name, display=False, save=False, border=0):
    sImPath = Path(name)
    sIm = None
    if sImPath.exists():
        # read image
        sIm = Image.open(name)
        print(str(datetime.now()), "Using saved file:", name)
    else:
        # create image
        sIm = smoothImage(im, name, save, border)

    if display:
        sIm.show()

    return(sIm)


# Calculate the horizontal portion of a Sobel gradient
#     [ 1,  2,  1]
#     [ 0,  0,  0]
#     [-1, -2, -1] 
def sobel_hPlane(im, x, y):
    # Apply horizontal Sobel mask on a single color plane.
    v = im.getpixel((x - 1, y - 1))[0]
    v += 2 * im.getpixel((x, y - 1))[0]
    v += im.getpixel((x + 1, y - 1))[0]
    v -= im.getpixel((x - 1, y + 1))[0]
    v -= 2 * im.getpixel((x, y + 1))[0]
    v -= im.getpixel((x + 1, y + 1))[0]

    return(v)


# Calculate the vertical portion of a Sobel gradient
#     [-1,  0,  1]
#     [-2,  0,  2]
#     [-1,  0,  1]
def sobel_vPlane(im, x, y):
    # Apply Sobel mask on a single color plane.
    v = 0
    v -= im.getpixel((x - 1, y - 1))[0]
    v += im.getpixel((x + 1, y - 1))[0]
    v -= 2 * im.getpixel((x - 1, y))[0]
    v += 2 * im.getpixel((x + 1, y))[0]
    v -= im.getpixel((x - 1, y + 1))[0]
    v += im.getpixel((x + 1, y + 1))[0]

    return(v)


# Calculate Sobel gradient for a pixel
def sobel(im, x, y):
    r1 = sobel_hPlane(im, x, y)
    r2 = sobel_vPlane(im, x, y)

    # Sobel gradient r = sqrt(r1**2 + r2**2)
    r = int(((r1 * r1) + (r2 * r2))**0.5)

    return(r)


# Fill an edges array with the calculated sobel edge gradient
def createSobelEdges(im, edges, border=0):

    for x in range(border, im.size[0] - (2 * border)):
        for y in range(border, im.size[1] - (2 * border)):
            edges[x, y] = sobel(im, x, y)


# Read gradients file if exists, else calculate gradients.
def getEdges(im, name, bord=0):
    ePath = Path(name)
    edges = None
    if ePath.exists():
        epFP = open(name, "rb")
        edges = np.load(epFP)
        print(str(datetime.now()), "Using saved file:", name)
    else:
        # Calculate input image pixel luminosities
        edges = np.zeros(im.size).astype(int)
        createSobelEdges(im, edges, bord)
        epFP = open(name, "wb")
        np.save(epFP, edges)
    epFP.close()

    return(edges)


# Normalize the edges array to 0<->MAX_COLOR
def normalizeEdges(edges):
    maxR = np.max(edges)

    norm = np.zeros(im.size).astype(int)

    for x in range(edges.shape[0]):
        for y in range(edges.shape[1]):
            norm[x, y] = int((edges[x, y] / maxR) * MAX_COLOR)

    return(norm)


# Create a palettized version of the edge gradients
def edgesImage(edges, name, palette, display=False, save=False):
    # Create, and possibly display, and possibly save, an image
    # by applying the provided sobel edges values to the provide image

    # Create canvas for new image
    newIm = Image.new('RGB', edges.shape, BACKGROUND)
    newPixels = newIm.load()

    max = np.max(edges)

    for x in range(edges.shape[0]):
        for y in range(edges.shape[1]):
            newPixels[x, y] = palette[edges[x, y]]

    if display:
        newIm.show()

    if save:
        newIm.save(name, format="PNG", quality=95)

    return(newIm)


def applyEdges(im, edges, name, th, display=False, save=False):
    # Create, and possibly display, and possibly save, an image
    # by applying the provided sobel edges values to the provide image

    # Create canvas for new image
    newIm = Image.new('RGB', im.size, BACKGROUND)
    newPixels = newIm.load()

    # get the input image
    pixels = im.load()
    
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if edges[x, y] < th:
                newPixels[x, y] = pixels[x, y]
            else:
                newPixels[x, y] = BLACK
#                newPixels[x, y] = BBLACK

    if display:
        newIm.show()

    if save:
        newIm.save(name, format="PNG", quality=95)

    return(newIm)



if __name__ == '__main__':
    print("Start now:",  str(datetime.now()))

    # Instantiate the command line parser
    parser = argparse.ArgumentParser(description="cli_sobel: sobel edge-enhancement")

    # Add in all the command line arguments the program recognizes
    # Optional argument for filename (defaults to 'test.png')
    parser.add_argument('--fn',
                        action="store",
                        dest="fn",
                        help="image filename",
                        default="test.png"
                        )

    # Optional argument for posterization palette (defaults to jet)
    parser.add_argument('--pn',
                        action="store",
                        dest="pn",
                        help="posterization palette name",
                        default="jet"
                        )

    # Optional argument for edge threshhold (defaults to 16)
    parser.add_argument('--th',
                        type=int,
                        help="edge threshhold",
                        default = 16
                        )

    # Optional argument for line art color name
    # NOTE: must be one of the recognized names in the Pillow colormap dictionary
    parser.add_argument('--lac',
                        action="store",
                        dest="lac",
                        help="line art color name",
                        default="white"
                        )

    # Optional argument to display all images
    parser.add_argument('--da', action='store_true', help="display all images")

    # Optional argument to display original image
    parser.add_argument('--do', action='store_true', help="display original")

    # Optional argument to display grayscale image
    parser.add_argument('--dgs', action='store_true', help="display grayscale")

    # Optional argument to display unedged posterized images
    parser.add_argument('--dp', action='store_true', help="display unedged posters")

    # Optional argument to display smoothed image
    parser.add_argument('--ds', action='store_true', help="display smoothed")

    # Optional argument to display grayscale smoothed image
    parser.add_argument('--dsgs', action='store_true', help="display smoothed grayscale")

    # Optional argument to display reversed palette edges image
    parser.add_argument('--dr', action='store_true', help="display reversed palettes")

    # Optional argument to autosave all generated files
    parser.add_argument('--sa', action='store_true', help="autosave all generated images")

    # Optional argument to autosave the edges image
    parser.add_argument('--se', action='store_true', help="autosave edges image")

    # Optional argument to autosave the posterized image(s)
    parser.add_argument('--sp', action='store_true', help="autosave posterized image(s)")

    # Optional argument to autosave the posterized and edged image(s)
    parser.add_argument('--spe',
                        action='store_true',
                        help="autosave edged posterized image(s)")

    # Optional argument to autosave the reversed palette image(s)
    parser.add_argument('--sr', action='store_true', help="autosave posterized image(s)")

    # Optional argument to autosave the reversed and edged image(s)
    parser.add_argument('--sre',
                        action='store_true',
                        help="autosave edged posterized image(s)")

    # Optional argument to also create an inverted palette, too
    parser.add_argument('--ci', action='store_true', help="create inverted palette image, too")

    # Optional argument to create watermarked files, as well
    parser.add_argument('--wm', action='store_true', help="create watermarked files")

    parser.add_argument('--wmfn', 
                        action="store",
                        dest="wmfn",
                        help="watermark filename",
                        default="watermark.png"
                        )

    # Optional argument to create image with max saturation version
    parser.add_argument('--ms', action='store_true', help="create max saturation versions")

    # Optional argument to create image using nearest palette colors to original
    parser.add_argument('--nc', action='store_true', help="create version using nearest color")

    # Optional argument to create image using dominant color per pixel
    parser.add_argument('--pc', action='store_true', help="create version using primary color")

    # Optional argument to create image using averaged colors per pixel
    parser.add_argument('--dc', action='store_true', help="create version using averaged color")

    # Optional argument to create image using tiered edges
    parser.add_argument('--t', action='store_true', help="create version using tiered edges color")

    # Optional argument to create image using tiered edges
    parser.add_argument('--pt', action='store_true', help="create version using palettized tiered edges color")

    # Get the actual values of the command line arguments.
    args = parser.parse_args()
    print("fn\t", args.fn)
    print("pn\t", args.pn)
    print("th\t", args.th)
    print("lac\t", args.lac)
    print("da\t", args.da)
    print("do\t", args.do)
    print("dgs\t", args.dgs)
    print("dp\t", args.dp)
    print("ds\t", args.ds)
    print("dsgs\t", args.dsgs)
    print("dr\t", args.dr)
    print("sa\t", args.sa)
    print("se\t", args.se)
    print("sp\t", args.sp)
    print("spe\t", args.spe)
    print("sr\t", args.sr)
    print("ci\t", args.ci)
    print("wm\t", args.wm)
    print("wmfn\t", args.wmfn)
    print("ms\t", args.ms)
    print("nc\t", args.nc)
    print("pc\t", args.pc)
    print("dc\t", args.dc)
    print("t\t", args.t)
    print("pt\t", args.pt)

    # Create the working palette
    colors = []
    anticolors = []

    # Test for custom palette in file
    cpPath = Path(args.pn)
    if cpPath.exists():
        # It's a file, read in the JSONized palette
        cpFP = open(args.pn)
        pData = json.load(cpFP)

        # convert JSON lists to tuples for the palette
        for d in pData:
            colors.append(tuple(d))

        # strip .json extension from palette name
        args.pn = args.pn.split('.')[0]
    else:
        cpPath = Path(args.pn + ".json")
        if cpPath.exists():
            # It's a file, user just forgot to add ".json" extension.
            cpFP = open(args.pn + ".json")
            pData = json.load(cpFP)

            # convert JSON lists to tuples for the palette
            for d in pData:
                colors.append(tuple(d))
        else:
            # Use MatPlotLib colormap to query colormap for colors, save in look up tables
            cm = plt.colormaps.get_cmap(args.pn)

            # poster lookup table
            colors = palette(cm)

    if args.ci:
        # create the inverse of the color palette
        for color in colors:
            anticolors.append(invert(color))

    # Create the reverse working palette
    r_colors = []
    r_anticolors = []

    # Build reverse palettes (different from inverting)
    for i in range(255, -1, -1):
        r_colors.append(colors[i])

    if args.ci:
        for i in range(255, -1, -1):
            r_anticolors.append(anticolors[i])

    # Create generic grayscale palette
    grays = [(x, x, x) for x in range(len(colors))]

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
    saveBase += fn[0] + "_"
    saveThBase = saveBase + str(args.th) + "_"
    savePalBase = saveBase + args.pn + "_"
    savePalThBase = savePalBase + str(args.th) + "_"

    # Open the input image into an Image object, display if requested
    oIm = Image.open(args.fn)

    if (args.do or args.da):
        oIm.show()
        print(str(datetime.now()), "Original version, for comparisons.")

    # Create a slightly larger canvas for working with, to allow skiping border checks
    # add a pixel to either side, and an extra row top and bottom
    BORDER = 1
    im = Image.new("RGB",
                   ((oIm.size[0] + (2 * BORDER)), (oIm.size[1] + (2 * BORDER))),
                   BACKGROUND
                   )
    im.paste(oIm, (BORDER, BORDER))

    # load watermark image, if needed
    wmIm = None
    wmLoc = (0, 0)
    if args.wm:
        wmIm = Image.open(args.wmfn)
        wmLoc = ((oIm.size[0] - wmIm.size[0]), (oIm.size[1] - wmIm.size[1]))

    # Create an image from the nearest palette colors to the original colors
    if args.nc:
        print(str(datetime.now()), "Nearest colors version started.")
        oImPixels = oIm.load()
        ncIm = Image.new('RGB', oIm.size, BACKGROUND)
        ncImPixels = ncIm.load()

        matchCounter = 0
        mcDict = dict()
        for x in range(ncIm.size[0]):
            for y in range(ncIm.size[1]):
                pixel = oImPixels[x, y]
                if pixel in mcDict:
                    # know closest color to this pixel, use look up to cut down on computation
                    ncImPixels[x, y] = mcDict[pixel]
                    matchCounter += 1
                else:
                    # haven't found closest color to this pixel yet, calculate it
                    color = nearest(pixel, colors)
                    ncImPixels[x, y] = color
                    # and save what we just calculated in a lookup table
                    mcDict[pixel] = color

        print(str(datetime.now()), "entries in mcDict:", len(mcDict))
        print(str(datetime.now()), "color already in mcDict:", matchCounter)
        if args.da:
            ncIm.show()
        ncIm.save(savePalBase + "nc.png", "JPEG", quality=95)
        print(str(datetime.now()), "Nearest colors version done.")

    lums = lumData(im, saveBase + "luminosity.npy", bord=BORDER) 
    print(str(datetime.now()), "Original luminosity array done.")

    # Grayscale image
    gsIm = getImage(lums,
                    saveBase + "gs.png",
                    grays,
                    (args.da or args.dgs),
                    True,
                    BORDER
                    )
    print(str(datetime.now()), "Grayscale image done.")

    # Generate posterized and poster-invereted images
    pIm = getImage(lums,
                   savePalBase + "p.png",
                   colors,
                   (args.da or args.dp),
                   (args.sa or args.sp),
                   BORDER
                   )
    print(str(datetime.now()), "Posterized image done.")

    if args.ci:
        piIm = getImage(lums,
                        savePalBase + "pi.png",
                        anticolors,
                        (args.da or args.dp),
                        (args.sa or args.sp),
                        BORDER
                        )
        print(str(datetime.now()), "Posterized invert image done.")

    # Generate reverse posterized and poster-invereted images
    rpIm = getImage(lums,
                    savePalBase + "pr.png",
                    r_colors,
                    (args.da or args.dr),
                    (args.sa or args.sr),
                    BORDER
                    )
    print(str(datetime.now()), "Reverse posterized image done.")

    if args.ci:
        rpiIm = getImage(lums,
                         savePalBase + "pri.png",
                         r_anticolors,
                         (args.da or args.dp),
                         (args.sa or args.sp),
                         BORDER
                         )
        print(str(datetime.now()), "Reverse posterized invert image done.")

    # Generate a smoothed (averaged) version of the input image.
    sIm = getSmoothImage(im,
                         saveBase + "a.png",
                         args.da,
                         True,
                         border=BORDER
                         )
    print(str(datetime.now()), "Smoothed image done.")

    # Calculate smoothed image pixel luminosities
    sLums = lumData(sIm, saveBase + "smoothLum.npy", BORDER)
    print(str(datetime.now()), "Smoothed luminosity array done.")

    # Generatee smoothed grayscale image
    sgsIm = getImage(sLums,
                     saveBase + "gsa.png",
                     grays,
                     (args.da or args.dgs),
                     True,
                     BORDER
                     )
    print(str(datetime.now()), "Smoothed grayscale image done.")

    # Generate posterized and poster-invereted images
    spIm = getImage(sLums,
                    savePalBase + "sp.png",
                    colors,
                    (args.da or args.dp),
                    (args.sa or args.sp),
                    BORDER
                    )
    print(str(datetime.now()), "Smoothed posterized image done.")

    if args.ci:
        spiIm = getImage(sLums,
                         savePalBase + "spi.png",
                         anticolors,
                         (args.da or args.dp),
                         (args.sa or args.sp),
                         BORDER
                         )
        print(str(datetime.now()), "Smoothed posterized invert image done.")

    # Generate smoothed reverse posterized and poster-invereted images
    sprIm = getImage(sLums,
                    savePalBase + "spr.png",
                    r_colors,
                    (args.da or args.dr),
                    (args.sa or args.sr),
                    BORDER
                    )
    print(str(datetime.now()), "Smoothed reverse posterized image done.")

    if args.ci:
        spriIm = getImage(sLums,
                         savePalBase + "spri.png",
                         r_anticolors,
                         (args.da or args.dp),
                         (args.sa or args.sp),
                         BORDER
                         )
        print(str(datetime.now()), "Smoothed reverse posterized invert image done.")

    edges = getEdges(sIm, saveBase + "sobel.npy", BORDER)
    eIm = createSobelEdges(sIm, edges, BORDER)
    print(str(datetime.now()), "Edge gradients calculated.")

    normEdges = normalizeEdges(edges)
    print(str(datetime.now()), "Edge gradients normalized.")

    edgePal = list()
    lacName = args.lac.lower()
    lineartColor = WHITE
    if lacName in ImageColor.colormap:
        lineartColor = ImageColor.getrgb(ImageColor.colormap[lacName])
    else:
        print(str(datetime.now()), "Requested line color '" + lacName + "' not in ImageColor. Using white.")
        lacName = 'white'
    for i in range(MAX_PLEN):
        if i < args.th:
            edgePal.append(BLACK)
        else:
            edgePal.append(lineartColor)

    # NOTE: Add args.th for filname because edgePal created using args.th
    edgesIm = edgesImage(normEdges,
                         saveThBase + "l_" + lacName + ".png",
                         edgePal,
                         args.da,
                         (args.sa or args.spe)
                         )

    print(str(datetime.now()), "Line art image done.")

    colEdges = edgesImage(normEdges,
                          savePalBase + "lp.png",
                          colors,
                          args.da,
                          (args.sa or args.spe)
                          )

    print(str(datetime.now()), "Posterized line art image done.")

    if args.ci:
        antiEdges = edgesImage(normEdges,
                               savePalBase + "lpi.png",
                               anticolors,
                               args.da,
                               (args.sa or args.spe)
                               )

    print(str(datetime.now()), "Posterized invert line art image done.")

    rcolEdges = edgesImage(normEdges,
                           savePalBase + "lpr.png",
                           r_colors,
                           (args.da or args.dr),
                           (args.sa or args.sr)
                           )

    print(str(datetime.now()), "Reverse posterized line art image done.")

    if args.ci:
        rantiEdges = edgesImage(normEdges,
                                savePalBase + "lpri.png",
                                r_anticolors,
                                (args.da or args.dr),
                                (args.sa or args.sr)
                                )

    print(str(datetime.now()), "Reverse posterized invert line art image done.")

    if args.nc:
        # Apply edges to the nearest color image
        encIM = applyEdges(ncIm,
                           normEdges,
                           savePalThBase + "nc_es.png",
                           args.th,
                           args.da,
                           True
                           )

    # Apply edges to the various posterized images available
    espIm = applyEdges(spIm,
                       normEdges,
                       savePalThBase + "esp.png",
                       args.th,
                       args.da,
                       (args.sa or args.spe)
                       )

    print(str(datetime.now()), "Edged smoothed posterized image done.")

    if args.ci:
        espiIm = applyEdges(spiIm,
                            normEdges,
                            savePalThBase + "espri.png",
                            args.th,
                            args.da,
                            (args.sa or args.spe)
                            )

        print(str(datetime.now()), "Edged smoothed reversed posterized invert image done.")

    esprIm = applyEdges(sprIm,
                       normEdges,
                       savePalThBase + "espr.png",
                       args.th,
                       args.da,
                       (args.sa or args.spe)
                       )

    print(str(datetime.now()), "Edged smoothed reversed posterized image done.")

    if args.ci:
        espriIm = applyEdges(spriIm,
                            normEdges,
                            savePalThBase + "espi.png",
                            args.th,
                            args.da,
                            (args.sa or args.spe)
                            )

        print(str(datetime.now()), "Edged smoothed reversed posterized invert image done.")

    esIm = applyEdges(sIm,
                      normEdges,
                      saveThBase + "es.png",
                      args.th,
                      args.da,
                      True
                      )

    print(str(datetime.now()), "Edged smoothed image done.")

    if args.ms:
        # Create max saturation image
        from colorsys import hsv_to_rgb, rgb_to_hsv
        
        msIm = Image.new("RGB", im.size, BACKGROUND)
        msPixels = msIm.load()
        msOrigImPixels = im.load()
        for x in range(msIm.size[0]):
            for y in range(msIm.size[1]):
                # get original (r,g,b) information -- NOTE: range 0-255
                r, g, b = msOrigImPixels[x, y]
                # convert to (h,s,v) -- NOTE: convert range to 0.0-1.0
#                h, s, v = rgb_to_hsv(r, g, b)
                h, s, v = rgb_to_hsv((r / 255), (g / 255), (b / 255))
                # keep original hue and value, bump saturation to max, get new (r,g,b)
                nr, ng, nb = hsv_to_rgb(h, 1.0, v)
                # write new pixel to new image -- NOTE: convert to range 0-255
#                msPixels[x, y] = (int(nr), int(ng), int(nb))
                msPixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255))

        if args.da:
            msIm.show()

        if args.sa:
            msIm.save(saveBase + "ms.png", format="PNG", quality=95)
            print(str(datetime.now()), "Max saturation image done.")

        msEsIm = applyEdges(msIm,
                            normEdges,
                            saveThBase + "ms_es.png",
                            args.th,
                            args.da,
                            True
                            )

        print(str(datetime.now()), "Edged max saturation image done.")

    if args.pc:
        # Create primary colors image (use largest of r/g/b as index)
        
        pcIm = Image.new("RGB", im.size, BACKGROUND)
        pcPixels = pcIm.load()
        pcOrigImPixels = im.load()
        for x in range(pcIm.size[0]):
            for y in range(pcIm.size[1]):
                # get original (r,g,b) informationcolor
                pcPixels[x, y] = colors[max(pcOrigImPixels[x,y])]

        if args.da:
            pcIm.show()

        if args.sa:
            pcIm.save(savePalBase + "pc.png", format="PNG", quality=95)
            print(str(datetime.now()), "Primary colors image done.")

        pcEsIm = applyEdges(pcIm,
                            normEdges,
                            savePalThBase + "pc_es.png",
                            args.th,
                            args.da,
                            True
                            )

        print(str(datetime.now()), "Edged primary colors image done.")

    if args.dc:
        # Set output pixel based on average of palette values indexed separately
        # by red, green, and blue values of original pixel

        dcIm = Image.new("RGB", im.size, BACKGROUND)
        dcPixels = dcIm.load()
        dcOrigImPixels = im.load()
        for x in range(dcIm.size[0]):
            for y in range(dcIm.size[1]):
                # get separate red, green, and blue values of original pixel
                r, g, b = dcOrigImPixels[x, y]
                # get palette color indexed by each of r, g, and b
                pr = colors[r]
                pg = colors[g]
                pb = colors[b]
                # get average red, green, blue from the three indexed colors
                r = int((pr[0] + pg[0] + pb[0]) / 3)
                g = int((pr[1] + pg[1] + pb[1]) / 3)
                b = int((pr[2] + pg[2] + pb[2]) / 3)
                # set output pixel
                dcPixels[x, y] = (r, g, b)

        if args.da:
            dcIm.show()

        if args.sa:
            dcIm.save(savePalBase + "dc.png", format="PNG", quality=95)
            print(str(datetime.now()), "Difference colors image done.")

        dcEsIm = applyEdges(dcIm,
                            normEdges,
                            savePalThBase + "dc_es.png",
                            args.th,
                            args.da,
                            True
                            )

        print(str(datetime.now()), "Edged difference colors image done.")

    if args.t:
        # Create tiered image from normalized edges
        
        tIm = Image.new("RGB", im.size, BACKGROUND)
        tPixels = tIm.load()
        edgeCounts = {"gray":0,"red":0,"yellow":0,"green":0,"cyan":0,"blue":0,"magenta":0,"white":0}
        for x in range(tIm.size[0]):
            for y in range(tIm.size[1]):
                edge = normEdges[x, y]
                if edge < args.th:
                    # edge value less than threshhold, mark with gray
                    tPixels[x, y] = (64, 64, 64)
                    edgeCounts["gray"] += 1
                else:
                    # adjust for threshhold value
                    edge = edge - args.th
                    # set pixel color based on what tier the edge value is in
                    if edge < 17:
                        # first tier, use red
                        tPixels[x, y] = (247 + edge, 0, 0)
                        edgeCounts["red"] += 1
                    elif edge < 33:
                        # second tier, use yellow
                        tPixels[x, y] = (239 + edge, 239 + edge, 0)
                        edgeCounts["yellow"] += 1
                    elif edge < 49:
                        # third tier, use green
                        tPixels[x, y] = (0, 231 + edge, 0)
                        edgeCounts["green"] += 1
                    elif edge < 65:
                        # fourth tier, use cyan
                        tPixels[x, y] = (0, 223 + edge, 223 + edge)
                        edgeCounts["cyan"] += 1
                    elif edge < 81:
                        # fifth tier, use blue
                        tPixels[x, y] = (0, 0, 215 + edge)
                        edgeCounts["blue"] += 1
                    elif edge < 97:
                        # sixth tier, use magenta
                        tPixels[x, y] = (207 + edge,   0, 207 + edge)
                        edgeCounts["magenta"] += 1
                    else:
                        # outside tiering, use cyan
                        tPixels[x, y] = (255, 255, 255)
                        edgeCounts["white"] += 1

        print(edgeCounts)
        if args.da:
            tIm.show()

        if args.sa:
            tIm.save(saveThBase + "t.png", format="PNG", quality=95)
            print(str(datetime.now()), "Tiered image done.")

    if args.pt:
        # Create palletized ad tiered image from normalized edges
        
        ptIm = Image.new("RGB", im.size, BACKGROUND)
        ptPixels = ptIm.load()
        palDiv = 2
        base = len(colors) - (len(colors) // palDiv)
        for x in range(ptIm.size[0]):
            for y in range(ptIm.size[1]):
                edge = normEdges[x, y]
                if edge < args.th:
                    # edge value less than threshhold, mark with gray
                    ptPixels[x, y] = (64, 64, 64)
                else:
                    # use limited part of the palette
                    edge = (edge // palDiv) + base
                    ptPixels[x, y] = colors[edge]

        if args.da:
            ptIm.show()

        if args.sa:
            ptIm.save(savePalThBase + "pt.png", format="PNG", quality=95)
            print(str(datetime.now()), "Palletized Tiered image done.")

    # Generate saturated palette posterized and poster-invereted images
    def saturatePalette(colors):
        # scale up color saturation by pushing max component to 255,
        # and scaling up the other two components the same amount
        satColors = list()
        for color in colors:
            maxComponent = max(max(color), 1)
#            maxR = int((color[0] / maxComponent) * 255)
#            maxG = int((color[1] / maxComponent) * 255)
#            maxB = int((color[2] / maxComponent) * 255)
            saturator = 255.0 * maxComponent
            maxR = int(color[0] * saturator)
            maxG = int(color[1] * saturator)
            maxB = int(color[2] * saturator)
            satColors.append((maxR, maxG, maxB))

        return(satColors)
    
    satColors = saturatePalette(colors)
    satPIm = getImage(lums,
                   savePalBase + "spp.png",
                   satColors,
                   (args.da or args.dp),
                   (args.sa or args.sp),
                   BORDER
                   )
    print(str(datetime.now()), "Saturated Palette Postermv ized image done.")

    satEIm = applyEdges(satPIm,
                            normEdges,
                            savePalThBase + "espp.png",
                            args.th,
                            args.da,
                            True
                            )

    print(str(datetime.now()), "Edged Saturated Palette Posterized image done.")

    if args.ci:
        satAnticolors = saturatePalette(anticolors)
        satPiIm = getImage(lums,
                        savePalBase + "sppi.png",
                        satAnticolors,
                        (args.da or args.dp),
                        (args.sa or args.sp),
                        BORDER
                        )

        print(str(datetime.now()), "Saturated Palette Posterized invert image done.")

        satEPiIm = applyEdges(satPiIm,
                            normEdges,
                            savePalThBase + "esppi.png",
                            args.th,
                            args.da,
                            True
                            )

        print(str(datetime.now()), "Edged Saturated Palette Posterized invert image done.")

    print(str(datetime.now()), "Run complete.")
