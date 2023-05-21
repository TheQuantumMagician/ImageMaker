#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3
#
# cli_sobel.py
#
# A program to apply sobel filter generated edges and custom color palette
# the input image. Optionally apply a watermark.
#
# Based on cli_edges.py
#
# 20230509 smb  @TheQuantumMagician - Started
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
    # 0.3r + 0.59g + 0.11b

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

    pix_count = 9
    return((int(r / pix_count), int(g / pix_count), int(b / pix_count)))


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
        newIm.save(name, format="JPEG", quality=95)

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
        im = processImage(npa,
                          name,
                          palette,
                          save,
                          bord
                          )

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
        newIm.save(name, format="JPEG", quality=95)

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
        sIm = smoothImage(im,
                         name,
                         save,
                         border
                         )

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
#     [-1, -0,  1]
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
def edgesImage(edges, name, palette, display=False, save=False, border=0):
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
        newIm.save(name, format="JPEG", quality=95)

    return(newIm)


def applyEdges(im, edges, name, th, display=False, save=False, border=0):
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

    if display:
        newIm.show()

    if save:
        newIm.save(name, format="JPEG", quality=95)

    return(newIm)


if __name__ == '__main__':
    print("Start now:",  str(datetime.now()))

    # Instantiate the command line parser
    parser = argparse.ArgumentParser(description="cli_sobel: sobel edge-enhancement")

    # Add in all the command line arguments the program recognizes
    # Optional argument for filename (defaults to 'test.jpg')
    parser.add_argument('--fn',
                        action="store",
                        dest="fn",
                        help="image filename",
                        default="test.jpg"
                        )

    # Optional argument for posterization palette (defaults to hsv)
    parser.add_argument('--pn',
                        action="store",
                        dest="pn",
                        help="posterization palette name",
                        default="hsv"
                        )

    # Optional argument for edge threshhold (defaults to 8)
    parser.add_argument('--th',
                        type=int,
                        help="edge threshhold",
                        default = 8
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

    # Optional argument to display weighted palette eedges image
    parser.add_argument('--dw', action='store_true', help="display weighted palette")

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

    # Optional argument to autosave the weighted palette edges image
    parser.add_argument('--sw', action='store_true', help="autosave edges image")

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

    # Get the actual values of the command line arguments.
    args = parser.parse_args()
    print("fn\t", args.fn)
    print("pn\t", args.pn)
    print("th\t", args.th)
    print("da\t", args.da)
    print("do\t", args.do)
    print("dgs\t", args.dgs)
    print("dp\t", args.dp)
    print("ds\t", args.da)
    print("dsgs\t", args.dsgs)
    print("sa\t", args.sa)
    print("se\t", args.se)
    print("sp\t", args.sp)
    print("spe\t", args.spe)
    print("ci\t", args.ci)
    print("wm\t", args.wm)
    print("wmfn\t", args.wmfn)

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

    # Grayscale, and if necessary, inverted color palette creation
    # Create generic grayscale palette
    grays = [(x, x, x) for x in range(len(colors))]

    anticolors = []
    if args.ci:
        # create the inverse of the color palette
        for color in colors:
            anticolors.append(invert(color))

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
    im.paste(oIm, (1, 1))

    # load watermark image, if needed
    wmIm = None
    wmLoc = (0, 0)
    if args.wm:
        wmIm = Image.open(args.wmfn)
        wmLoc = ((oIm.size[0] - wmIm.size[0]), (oIm.size[1] - wmIm.size[1]))

    lums = lumData(im, saveBase + "luminosity.npy", bord=BORDER) 
    print(str(datetime.now()), "Original luminosity array done.")

    # Grayscale image
    gsIm = getImage(lums,
                    saveBase + "gs.jpg",
                    grays,
                    (args.da or args.dgs),
                    True,
                    BORDER
                    )
    print(str(datetime.now()), "Grayscale image done.")

    # Generate posterized and poster-invereted images
    pIm = getImage(lums,
                   savePalBase + "p.jpg",
                   colors,
                   (args.da or args.dp),
                   (args.sa or args.sp),
                   BORDER
                   )
    print(str(datetime.now()), "Posterized image gone.")

    if args.ci:
        piIm = getImage(lums,
                        savePalBase + "pi.jpg",
                        anticolors,
                        (args.da or args.dp),
                        (args.sa or args.sp),
                        BORDER
                        )
        print(str(datetime.now()), "Posterized invert image done.")

    # Generate a smoothed (averaged) version of the input image.
    sIm = getSmoothImage(im,
                         saveBase + "a.jpg",
                         args.da,
                         True,
                         border=BORDER
                         )
    print(str(datetime.now()), "Smoothed image done.")

    # Calculate smoothed image pixel luminosities
    sLums = lumData(sIm, saveBase + "smoothLum.npy", BORDER)
    print(str(datetime.now()), "Smoothed luminosity array done.")

    # Generatee smoothed grayscale image
    sGsIm = getImage(sLums,
                     saveBase + "sgs.jpg",
                     grays,
                     (args.da or args.dgs),
                     True,
                     BORDER
                     )
    print(str(datetime.now()), "Smoothed grayscale image done.")

    # Generate posterized and poster-invereted images
    sPIm = getImage(sLums,
                    savePalBase + "sp.jpg",
                    colors,
                    (args.da or args.dp),
                    (args.sa or args.sp),
                    BORDER
                    )
    print(str(datetime.now()), "Smoothed posterized image done.")

    if args.ci:
        sPiIm = getImage(sLums,
                         savePalBase + "spi.jpg",
                         anticolors,
                         (args.da or args.dp),
                         (args.sa or args.sp),
                         BORDER
                         )
        print(str(datetime.now()), "Smoothed posterized invert image done.")

    edges = getEdges(sIm, saveBase + "sobel.npy", BORDER)
    eIm = createSobelEdges(sIm, edges, BORDER)
    print(str(datetime.now()), "Edge gradients calculated.")

    normEdges = normalizeEdges(edges)
    print(str(datetime.now()), "Edge gradients normalized.")

    edgePal = list()
    for i in range(MAX_PLEN):
        if i < args.th:
            edgePal.append(BLACK)
        else:
            edgePal.append(WHITE)

    # NOTE: Add args.th for filname because edgePal created using args.th
    edgesIm = edgesImage(normEdges,
                         saveThBase + "e.jpg",
                         edgePal,
                         args.da,
                         (args.sa or args.spe),
                         border=BORDER
                         )

    print(str(datetime.now()), "Edges image done.")

    colEdges = edgesImage(normEdges,
                          savePalBase + "ep.jpg",
                          colors,
                          args.da,
                          (args.sa or args.spe),
                          border=BORDER
                          )

    print(str(datetime.now()), "Posterized edges image done.")

    if args.ci:
        antiEdges = edgesImage(normEdges,
                               savePalBase + "epi.jpg",
                               anticolors,
                               args.da,
                               (args.sa or args.spe),
                               border=BORDER
                               )

    print(str(datetime.now()), "Posterized invert edges image done.")

    esPIm = applyEdges(sPIm,
                       normEdges,
                       savePalThBase + "esp.jpg",
                       args.th,
                       args.da,
                       (args.sa or args.spe),
                       border=BORDER
                       )

    print(str(datetime.now()), "Edged smoothed posterized image done.")

    if args.ci:
        sPiIm = applyEdges(sPiIm,
                           normEdges,
                           savePalThBase + "espi.jpg",
                           args.th,
                           args.da,
                           (args.sa or args.spee),
                           border=BORDER
                           )

        print(str(datetime.now()), "Edged smoothed posterized invert image done.")

#    print("sIm:", str(sIm.size), " normEdges:", normEdges.shape)
    esIm = applyEdges(sIm,
                      normEdges,
                      saveThBase + "es.jpg",
                      args.th,
                      args.da,
                      True,
                      border=BORDER
                      )

    print(str(datetime.now()), "Edged smoothed image done.")

    # Experimental code: trying to create a weighted palettee
    
    weighted = []
    minE = np.min(edges)
    maxE = np.max(edges)
    histo, bins = np.histogram(edges, bins=maxE + 1)
    totalEdges = histo.sum()
    print("len(histo):", len(histo), "totalEdges", totalEdges)
    runningTotal = 0
    for i in range(len(histo)):
        weight = int((runningTotal / totalEdges) * MAX_COLOR)
        weighted.append(weight)
        runningTotal += histo[i]

    print("len(weighted):", len(weighted))
    print(im.size, edges.shape)

#            wImPixels[x, y] = colors[weighted[edges[x, y]]]

    wIm = Image.new("RGB", edges.shape, BACKGROUND)
    wImPixels = wIm.load()
    for x in range(edges.shape[0]):
        for y in range(edges.shape[1]):
            # Actually edge gradient
            ed = edges[x, y]
            # get the weighted index value
            try:
                ind = weighted[ed]
            except:
                print(x, y)
                print("ed:", ed)
            # get the palette color for the pixel
            wImPixels[x, y] = colors[ind]

    if (args.da or args.dw):
        wIm.show()
        print(str(datetime.now()), "Weighted palette image done.")

    if (args.sa or args.sw):
        wIm.save(savePalBase + "w.jpg", format="JPEG", quality=95)
