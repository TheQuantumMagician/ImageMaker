#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import argparse

import matplotlib.pyplot as plt

from datetime import datetime
from datetime import date
from pathlib import Path
from PIL import Image

def get_brightness(pixel):
    # Calculate luminosity of an (r, g, b) pixel

    gs = int((0.3 * pixel[0]) + (0.59 * pixel[1]) + (0.11 * pixel[2]))

    return(gs)


def invert(pixel):
    # invert (compliment) the provided pixel

    r = 255 - pixel[0]
    g = 255 - pixel[1]
    b = 255 - pixel[2]

    return((r, g, b))


def getAverage(im, x, y, size):
    # calculate the average pixel value of a sizexsize square of pixels
    # centered on x, y (or slightly off-centered if size is even)
    # NOTE: Does no bounds checkig -- that's handld at the calling level

    r, g, b = 0, 0, 0
    margin = int(size / 2)
    other_margin = (size - margin)
    x_range = range(x - margin, x + other_margin)
    y_range = range(y - margin, y + other_margin)
    for newX in x_range:
        for newY in y_range:
            pixel = im.getpixel((newX, newY))
            r += pixel[0]
            g += pixel[1]
            b += pixel[2]

    pix_count = size * size
    return((int(r / pix_count), int(g / pix_count), int(b / pix_count)))


def getVDiff(im, x, y):
    # Get average intensity difference between pixel at (x,y)
    #     and the three pixels centered on its x in the row below
    # NOTE: making use of the fact that the pixels are all grayscale
    #     which means r and g and b values are all equal, only use r

    diff = 0
    anchor = im.getpixel((x, y))
    for newX in range(x - 1, x + 2):
        diffPix = im.getpixel((newX, y + 1))
        diff += abs(anchor[0] - diffPix[0])

    gs = int(diff / 3)

    return((gs, gs, gs))


def getHDiff(im, x, y):
    # Get average intensity difference between pixel at (x,y)
    #     and the three pixels centered on its y in the column to the right
    # NOTE: making use of the fact that the pixels are all grayscale
    #     which means r and g and b values are all equal, only use r

    diff = 0
    anchor = im.getpixel((x, y))
    for newY in range(y - 1, y + 2):
        diffPix = im.getpixel((x + 1, newY))
        diff += abs(anchor[0] - diffPix[0])

    gs = int(diff / 3)

    return((gs, gs, gs))


def getMaxDiff(im, x, y):
    # Get the maximum intensity difference between pixel at (x,y)
    #     and the eight pixels centered on it
    # NOTE: making use of the fact that the pixels are all grayscale
    #     which means r and g and b values are all equal, only use r

    diff = 0
    anchor = im.getpixel((x, y))
    for newX in range(x - 1, x + 2):
        for newY in range(y - 1, y + 2):
            diffPix = im.getpixel((x + 1, newY))
            tempDiff = abs(anchor[0] - diffPix[0])
            if tempDiff > diff:
                diff = tempDiff

    return((diff, diff, diff))


heatmap = [(0, 0, 0),
           (255, 0, 0),
           (255, 0, 0),
           (255, 255, 0),
           (255, 255, 0),
           (0, 255, 0),
           (0, 255, 0),
           (0, 255, 255),
           (0, 255, 255),
           (0, 0, 255),
           (0, 0, 255),
           (255, 0, 255),
           (255, 0, 255),
           (255, 255, 255),
           ]
hm_len = len(heatmap)


print("Starting processing now:",  str(datetime.now()))

# background default
background = (0, 0, 0, 255)

# Instantiate the command line parser
parser = argparse.ArgumentParser(description="edges: edge-enhancement and posterization application")

# Optional argument for filename (defaults to 'test.jpg')
parser.add_argument('--fn',
                    action="store",
                    dest="fn",
                    help="override default filename",
                    default="test.jpg"
                    )

# Optional argument for posterization palette (defaults to gist_rainbow)
parser.add_argument('--pn',
                    action="store",
                    dest="pn",
                    help="override default posterization palette",
                    default="gist_rainbow"
                    )

# Optional argument for edge threshhold (defaults to 16)
parser.add_argument('--th',
                    type=int,
                    help="override default edge threshhold",
                    default = 8
                    )

# Optional argument for edge threshhold (defaults to 16)
parser.add_argument('--bs',
                    type=int,
                    help="override default averaging box edge size",
                    default = 3
                    )

# Optional argument to display original image
parser.add_argument('--da', action='store_true', help="display all images")

# Optional argument to display original image
parser.add_argument('--do', action='store_true', help="display original")

# Optional argument to compute and display grayscale image
parser.add_argument('--dgs', action='store_true', help="compute and display grayscale")

# Optional argument to display unedged posterized images
parser.add_argument('--dp', action='store_true', help="compute and display plain posters")

# Optional argument to display averaged image
parser.add_argument('--ds', action='store_true', help="display smoothed")

# Optional argument to display grayscale averaged image
parser.add_argument('--dsgs', action='store_true', help="display smoothed grayscale")

# Optional argument to display vertical differences image
parser.add_argument('--dv', action='store_true', help="display vertical differences")

# Optional argument to display horizontal differences image
parser.add_argument('--dh', action='store_true', help="display horizontal differences")

# Optional argument to autosave all generated files
parser.add_argument('--sv', action='store_true', help="autosave displayed intermediate images")

# Optional argument to autosave the edges image
parser.add_argument('--se', action='store_true', help="autosave edges image")

# Optional argument to display the maxDiffs histogram
parser.add_argument('--hi', action='store_true', help="display histogram")

args = parser.parse_args()
print("fn\t", args.fn)
print("pn\t", args.pn)
print("th\t", args.th)
print("bs\t", args.bs)
print("da\t", args.da)
print("do\t", args.do)
print("dgs\t", args.dgs)
print("dp\t", args.dp)
print("ds\t", args.da)
print("dsgs\t", args.dsgs)
print("dv\t", args.dv)
print("dh\t", args.dh)
print("sv\t", args.sv)
print("se\t", args.se)
print("hi\t", args.hi)
threshhold = args.th

# open the file into an image object.
im = Image.open(args.fn)
pixels = im.load()

# palettes
palette_length = 256
colors = []
anticolors = []

cm = plt.cm.get_cmap(args.pn)
pl_max = palette_length - 1
for c in range(palette_length):
    color = cm(c / pl_max)
    r = int(color[0] * 255)
    g = int(color[1] * 255)
    b = int(color[2] * 255)
    colors.append((r, g, b))

for color in colors:
    anticolors.append(invert(color))

# Create a grayscale lookup table
grays = [(x, x, x) for x in range(palette_length)]

if args.do or args.da:
    im.show()
    print("Original version, for comparisons.",  str(datetime.now()))

# Set up for image file saves.
today = date.today()
saveDirStr = "./" + today.__format__("%Y%m%d")
saveDir = Path(saveDirStr)

if not saveDir.exists():
    print("The save directory:", saveDirStr, "does not exist.")
    print("Creating save directory.")
    # NOTE: not doing this in a try/except block, because w/o save directory,
    #       it's not worth doing all the calculations for the images
    saveDir.mkdir()

# Build the base file name string
fn = im.filename.split(".")
saveBase = saveDirStr + "/"
saveBase += today.__format__("%Y%m%d") + "_"
saveBase += fn[0] + "_"
saveBase += args.pn + "_"

# create a canvas to posterize into
pIm = Image.new('RGB', im.size, background)
pPixels = pIm.load()

# creat a canvas to invert posterized version into
iIm = Image.new('RGB', im.size, background)
iPixels = iIm.load()

# creat a canvas for grayscale version
gIm = Image.new('RGB', im.size, background)
gPixels = gIm.load()

for x in range(0, im.size[0]):
    for y in range(0, im.size[1]):
        bright = get_brightness(im.getpixel((x, y)))
        pPixels[x, y] = colors[bright]
        iPixels[x, y] = anticolors[bright]
        gPixels[x, y] = grays[bright]

if args.dp or args.da:
    pIm.show()
    iIm.show()

if args.sv:
    pIm.save(saveBase + "p.jpg", format="JPEG", quality=95)
    iIm.save(saveBase + "pi.jpg", format="JPEG", quality=95)

print("Posterized version done.",  str(datetime.now()))
print("Anti-posterized version done.")

if args.dgs or args.da:
    gIm.show()

if args.sv:
    gIm.save(saveBase + "gs.jpg", format="JPEG", quality=95)

print("Grayscale version done.")

# get averaged values
# NOTE: margin/other_margin are used to allow average generation w/o bounds checking
#       which speeds the whole process up considerably

# create a canvas for the smoothed [averaged] version
avgIm = Image.new('RGB', im.size, background)
aPixels = avgIm.load()

# create a canvas for the averaged grayscale version
gAvgIm = Image.new('RGB', im.size, background)
gaPixels = gAvgIm.load()

margin = int(args.bs / 2)
other_margin = args.bs - margin
for x in range(margin, im.size[0] - other_margin):
    for y in range(margin, im.size[1] - other_margin):
        pixel = getAverage(im, x, y, args.bs)
        aPixels[x, y] = pixel
        gaPixels[x, y] = grays[get_brightness(pixel)]
        
if args.ds or args.da:
    avgIm.show()

if args.sv:
    avgIm.save(saveBase + "a.jpg", format="JPEG", quality=95)

print("Averaged version done.",  str(datetime.now()))

if args.dsgs or args.da:
    gAvgIm.show()

if args.sv:
    gAvgIm.save(saveBase + "ags.jpg", format="JPEG", quality=95)

print("Grayscale averaged version done.")

vDiffIm = Image.new('RGB', im.size, background)
vPixels = vDiffIm.load()

# Get vertical intensity differences
max_vDiff = 0
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        vPixels[x, y] = getVDiff(gAvgIm, x, y)
        if vPixels[x, y][0] > max_vDiff:
            max_vDiff = vPixels[x, y][0]

if args.dv or args.da:
    vDiffIm.show()

if args.sv:
    vDiffIm.save(saveBase + "av.jpg", format="JPEG", quality=95)

print("Vertical edges version done.", max_vDiff,  str(datetime.now()))

hDiffIm = Image.new('RGB', im.size, background)
hPixels = hDiffIm.load()

# Get horizontal intensity differences
max_hDiff = 0
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        hPixels[x, y] = getHDiff(gAvgIm, x, y)
        if hPixels[x, y][0] > max_hDiff:
            max_hDiff = hPixels[x, y][0]

if args.dh or args.da:
    hDiffIm.show()

if args.sv:
    hDiffIm.save(saveBase + "ah.jpg", format="JPEG", quality=95)

print("Horizontal edges version done.", max_hDiff,  str(datetime.now()))

#
# Generate a heat map of the maxium pixel differences.
#
mDiffIm = Image.new('RGB', im.size, background)
mdPixels = mDiffIm.load()

# list to allow histogram generation of differences
mdHisto = []

# Get maxium intensity differences between pixel and all eight neighbors
max_mDiff = 0
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        mdPixels[x, y] = getMaxDiff(gAvgIm, x, y)
        mdp0 = mdPixels[x, y][0]
        mdHisto.append(mdp0)
        if mdp0 > max_mDiff:
            max_mDiff = mdp0

mDiffIm.show()

mDiffIm.save(saveBase + "amd.jpg", format="JPEG", quality=95)

print("MaxDiff version done.", max_mDiff,  str(datetime.now()))

# Use matplotlib to plot the same data as a histogram.
mdHisto_fig, mdHisto_ax = plt.subplots(1, 1, figsize=(8, 8), tight_layout=True)
mdHisto_ax.hist(mdHisto, bins=256)

for x in range(im.size[0]):
    for y in range(im.size[1]):
#        mdPixels[x, y] = colors[mdPixels[x, y][0]]
        mdPixels[x, y] = heatmap[mdPixels[x, y][0] % hm_len]

mDiffIm.show()

mDiffIm.save(saveBase + "ahm.jpg", format="JPEG", quality=95)

print("MaxDiff heatmap version done.", max_mDiff,  str(datetime.now()))

# Apply calculated edges to heat map
for x in range(im.size[0]):
    for y in range(im.size[1]):
        if (vPixels[x, y][0] > threshhold) or (hPixels[x, y][0] > threshhold):
            mdPixels[x, y] = (0,0,0)

mDiffIm.show()

mDiffIm.save(saveBase + "ahme.jpg", format="JPEG", quality=95)

print("MaxDiff edged heatmap version done.", str(datetime.now()))

# match a palette to the maximum edge differences
pal_len = max(max_vDiff, max_hDiff) + 1
cmax = pal_len - 1
print("pal_len, cmax:", pal_len, cmax)

diffColors = []
# Create a separate color for each palette entry from color map calculations.
for c in range(pal_len):
    color = cm(c / cmax)
    r = int(color[0] * 255)
    g = int(color[1] * 255)
    b = int(color[2] * 255)
    diffColors.append((r, g, b))

# Now get funky -- overlay edges on posterized version
funkyIm = Image.new('RGB', im.size, background)
fPixels = funkyIm.load()

afunkyIm = Image.new('RGB', im.size, background)
afPixels = afunkyIm.load()

# NOTE: While overlaying the edges on the posterized versions,
#       also create a maxed edges version, and a colored edges version
for x in range(0, im.size[0]):
    # NOTE: Use the vertical differences image to keep track of edge pixels used
    for y in range(0, im.size[1]):
        if (vPixels[x, y][0] > threshhold) or (hPixels[x, y][0] > threshhold):
            pixel = (0, 0, 0)
            apixel = pixel
            # Mark the edge pixels in the smoothed image, too
            aPixels[x, y] = pixel
            # Edge pixel, colorize based on brightness
            diffColor = max(vPixels[x, y][0], hPixels[x, y][0])
            hPixels[x, y] = diffColors[diffColor]
            # Edge pixel, make white (max)
            vPixels[x, y] = (255, 255, 255)
        else:
            bright = gaPixels[x, y][0]
            pixel = colors[bright]
            apixel = anticolors[bright]
            # Non-edge pixel, make black
            vPixels[x, y] = (0, 0, 0)
            hPixels[x, y] = (0, 0, 0)

        fPixels[x, y] = pixel
        afPixels[x, y] = apixel

# Display and save the representation of the edges.
if args.da:
    hDiffIm.show()
    vDiffIm.show()

if args.se or args.sv:
    vDiffIm.save(saveBase + "ae.jpg", format="JPEG", quality=95)
    hDiffIm.save(saveBase + "aec.jpg", format="JPEG", quality=95)

funkyIm.show()
funkyIm.save(saveBase + "ap.jpg", format="JPEG", quality=95)
print("Posterized and edged version done.",  str(datetime.now()))

afunkyIm.show()
afunkyIm.save(saveBase + "api.jpg", format="JPEG", quality=95)
print("Anti-posterized and edged version done.")

# Display and save the smoothed and edged version of the original image
avgIm.show()
avgIm.save(saveBase + "se.jpg", format="JPEG", quality=95)

# And make the histogram plot visible.
if args.hi:
    plt.show()
    print("Histogram plot generated. Close histogram window to end program.")

