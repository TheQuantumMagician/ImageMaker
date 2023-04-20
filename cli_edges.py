#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import argparse

import matplotlib.pyplot as plt

from datetime import datetime
from datetime import date
from pathlib import Path
from PIL import Image
from os.path import exists

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

# Optional argument for posterization palette (defaults to hsv)
parser.add_argument('--pn',
                    action="store",
                    dest="pn",
                    help="override default posterization palette",
                    default="hsv"
                    )

# Optional argument for edge threshhold (defaults to 8)
parser.add_argument('--th',
                    type=int,
                    help="override default edge threshhold",
                    default = 8
                    )

# Optional argument for averaging box edge size (defaults to 3)
parser.add_argument('--bs',
                    type=int,
                    help="override default averaging box edge size",
                    default = 3
                    )

# Optional argument to display all images
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

# Optional argument to quiet all displays
parser.add_argument('--q', action='store_true', help="quiet mode (no displays)")

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
print("q\t", args.q)

# Allows enabled displays if not in quiet mode
loud = not args.q

# open the file into an image object.
im = Image.open(args.fn)
pixels = im.load()

# poster and grayscale lookup tables
palette_length = 256
colors = []
anticolors = []
grays = [(x, x, x) for x in range(palette_length)]

# Use MatPlotLib colormap to query colormap for colors, save in look up tables
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

if (args.do or args.da) and loud:
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
savePalBase = saveBase + args.pn + "_"

# posterized images
# create a canvas to posterize into
pIm = Image.new('RGB', im.size, background)
pPixels = pIm.load()

# creat a canvas for inverted posterized version
iIm = Image.new('RGB', im.size, background)
iPixels = iIm.load()

for x in range(0, im.size[0]):
    for y in range(0, im.size[1]):
        bright = get_brightness(im.getpixel((x, y)))
        pPixels[x, y] = colors[bright]
        iPixels[x, y] = anticolors[bright]

if (args.dp or args.da) and loud:
    pIm.show()
    iIm.show()

if args.sv:
    pIm.save(savePalBase + "p.jpg", format="JPEG", quality=95)
    iIm.save(savePalBase + "pi.jpg", format="JPEG", quality=95)

print("Posterized versions done.",  str(datetime.now()))

# plain grayscale image
gIm = None
genGS = True
if exists(saveBase + "gs.jpg"):
    # already generated a grayscale image and saved it, use it
    gIm = Image.open(saveBase + "gs.jpg")
    genGS = False
    print("Opened saved file:", saveBase + "gs.jpg")
else:
    # creat a canvas for grayscale version
    gIm = Image.new('RGB', im.size, background)

gPixels = gIm.load()

if genGS:
    for x in range(0, im.size[0]):
        for y in range(0, im.size[1]):
            bright = get_brightness(im.getpixel((x, y)))
            gPixels[x, y] = grays[bright]

if (args.dgs or args.da) and loud:
    gIm.show()

if args.sv and genGS:
    gIm.save(saveBase + "gs.jpg", format="JPEG", quality=95)

print("Grayscale version done.")

# average values
avgIm = None
genAvg = True
if exists(saveBase + "a.jpg"):
    # exists, use it
    avgIm = Image.open(saveBase + "a.jpg")
    genAvg = False
    print("Opened saved file:", saveBase + "a.jpg")
else:
    # create a canvas for the smoothed [averaged] version
    avgIm = Image.new('RGB', im.size, background)

aPixels = avgIm.load()

gAvgIm = None
genGAvg = True
if exists(saveBase + "ags.jpg"):
    gAvgIm = Image.open(saveBase + "ags.jpg")
    genGAvg = False
    print("Opened saved file:", saveBase + "ags.jpg")

else:
    # create a canvas for the averaged grayscale version
    gAvgIm = Image.new('RGB', im.size, background)

gaPixels = gAvgIm.load()

# NOTE: margin/other_margin are used to allow average generation w/o bounds checking
#       which speeds the whole process up considerably
margin = int(args.bs / 2)
other_margin = args.bs - margin

if genAvg:
    for x in range(margin, im.size[0] - other_margin):
        for y in range(margin, im.size[1] - other_margin):
            aPixels[x, y] = getAverage(im, x, y, args.bs)

if (args.ds or args.da) and loud:
    avgIm.show()

if args.sv and genAvg:
    avgIm.save(saveBase + "a.jpg", format="JPEG", quality=95)

print("Averaged version done.",  str(datetime.now()))

gAvgIm = None
genGAvg = True
if exists(saveBase + "ags.jpg"):
    gAvgIm = Image.open(saveBase + "ags.jpg")
    genGAvg = False
    print("Opened saved file:", saveBase + "ags.jpg")
else:
    # create a canvas for the averaged grayscale version
    gAvgIm = Image.new('RGB', im.size, background)

gaPixels = gAvgIm.load()

if genGAvg:
    for x in range(margin, im.size[0] - other_margin):
        for y in range(margin, im.size[1] - other_margin):
            gaPixels[x, y] = grays[get_brightness(aPixels[x, y])]
        
if (args.dsgs or args.da) and loud:
    gAvgIm.show()

if args.sv and genGAvg:
    gAvgIm.save(saveBase + "ags.jpg", format="JPEG", quality=95)

print("Grayscale averaged version done.")


# differences images/scratch canvases
vDiffIm = None
genVDiff = True
if exists(saveBase + "av.jpg"):
    vDiffIm = Image.open(saveBase + "av.jpg")
    genVDiff = False
    print("Opened saved file:", saveBase + "av.jpg")
else:
    vDiffIm = Image.new('RGB', im.size, background)

vPixels = vDiffIm.load()

# Get vertical intensity differences
if genVDiff:
    for x in range(1, im.size[0] - 1):
        for y in range(1, im.size[1] - 1):
            vPixels[x, y] = getVDiff(gAvgIm, x, y)

max_vDiff = 0
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        if vPixels[x, y][0] > max_vDiff:
            max_vDiff = vPixels[x, y][0]

if (args.dv or args.da) and loud:
    vDiffIm.show()

if args.sv and genVDiff:
    vDiffIm.save(saveBase + "av.jpg", format="JPEG", quality=95)

print("Vertical edges version done.", max_vDiff,  str(datetime.now()))

hDiffIm = None
genHDiff = True

if exists(saveBase + "ah.jpg"):
    hDiffIm = Image.open(saveBase + "ah.jpg")
    genHDiff = False
    print("Opened saved file:", saveBase + "ah.jpg")
else:
    hDiffIm = Image.new('RGB', im.size, background)

hPixels = hDiffIm.load()

# Get horizontal intensity differences
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        hPixels[x, y] = getHDiff(gAvgIm, x, y)

max_hDiff = 0
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        if hPixels[x, y][0] > max_hDiff:
            max_hDiff = hPixels[x, y][0]

if (args.dh or args.da) and loud:
    hDiffIm.show()

if args.sv and genHDiff:
    hDiffIm.save(saveBase + "ah.jpg", format="JPEG", quality=95)

print("Horizontal edges version done.", max_hDiff,  str(datetime.now()))

#
# Generate a heat map of the maxium pixel differences.
#
mDiffIm = None
genMDiff = True
if exists(saveBase + "amd.jpg"):
    mDiffIm = Image.open(saveBase + "amd.jpg")
    genMDiff = False
    print("Opened saved file:", saveBase + "amd.jpg")
else:
    mDiffIm = Image.new('RGB', im.size, background)

mdPixels = mDiffIm.load()

# Get maxium intensity differences between pixel and all eight neighbors
if genMDiff:
    for x in range(1, im.size[0] - 1):
        for y in range(1, im.size[1] - 1):
            mdPixels[x, y] = getMaxDiff(gAvgIm, x, y)

if loud:
    mDiffIm.show()

if genMDiff:
    mDiffIm.save(saveBase + "amd.jpg", format="JPEG", quality=95)

print("MaxDiff version done.", str(datetime.now()))
#print(sorted(pixel_dict.items(), reverse=True))

# list to allow histogram generation of differences
mdHisto = []
max_mDiff = 0
pixel_dict = dict()

# Get maxium intensity differences between pixel and all eight neighbors
for x in range(1, im.size[0] - 1):
    for y in range(1, im.size[1] - 1):
        mdp0 = mdPixels[x, y][0]
        if mdp0 in pixel_dict:
            pixel_dict[mdp0] += 1
        else:
            pixel_dict[mdp0] = 1
        mdHisto.append(mdp0)
        if mdp0 > max_mDiff:
            max_mDiff = mdp0

print("max_mDiff =", max_mDiff)
print("pixel diff count:", len(pixel_dict))

threshhold = args.th

hm_colors = []

for c in range(max_mDiff + 1):
    color = cm(c / max_mDiff)
    r = int(color[0] * 255)
    g = int(color[1] * 255)
    b = int(color[2] * 255)
    hm_colors.append((r, g, b))

#print(hm_colors)

for x in range(im.size[0]):
    for y in range(im.size[1]):
        try:
            mdPixels[x, y] = hm_colors[mdPixels[x, y][0]]
        except Exception as e:
            print(e)
            print("index =", mdPixels[x, y][0])
            print("len(hm_colors) =", len(hm_colors))

if loud:
    mDiffIm.show()

mDiffIm.save(savePalBase + "ahm.jpg", format="JPEG", quality=95)

print("MaxDiff heatmap version done.", max_mDiff,  str(datetime.now()))

# Apply calculated edges to heat map
for x in range(im.size[0]):
    for y in range(im.size[1]):
        if (vPixels[x, y][0] > threshhold) or (hPixels[x, y][0] > threshhold):
            mdPixels[x, y] = (0,0,0)

if loud:
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
if args.da and loud:
    hDiffIm.show()
    vDiffIm.show()

if args.se or args.sv:
    vDiffIm.save(savePalBase + "ae.jpg", format="JPEG", quality=95)
    hDiffIm.save(savePalBase + "aec.jpg", format="JPEG", quality=95)

if loud:
    funkyIm.show()

funkyIm.save(savePalBase + "ap.jpg", format="JPEG", quality=95)
print("Posterized and edged version done.",  str(datetime.now()))

if loud:
    afunkyIm.show()

afunkyIm.save(savePalBase + "api.jpg", format="JPEG", quality=95)
print("Anti-posterized and edged version done.")

# Display and save the smoothed and edged version of the original image
if loud:
    avgIm.show()

avgIm.save(saveBase + "se.jpg", format="JPEG", quality=95)

# And make the histogram plot visible.
if args.hi and loud:
    # Use matplotlib to plot the same data as a histogram.
    mdHisto_fig, mdHisto_ax = plt.subplots(1, 1, figsize=(8, 8), tight_layout=True)
    counts, bins, patches = mdHisto_ax.hist(mdHisto, bins=len(pixel_dict))

    plt.show()
    print("Histogram plot generated. Close histogram window to end program.")
