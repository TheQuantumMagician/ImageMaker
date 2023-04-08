#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import argparse

import matplotlib.pyplot as plt

from datetime import datetime
from datetime import date
from pathlib import Path
from PIL import Image

def _find_color(c_val, sdc, len):
    """Given a color map _segmentdata structure, find & calculate current value."""

    color = 0.0
    for index in range(1, len):
        cm_r = sdc[index]
        cm_p = sdc[index - 1]
        i_base = cm_p[0]
        i_next = cm_r[0]
        if c_val >= i_base and c_val < i_next:
            # Found interval. Color ='s previous value plus prorated difference
            #     between start of interval value and end of interval value.
            c_base = cm_p[1]
            c_next = cm_r[1]
            color = c_base + (((c_val - i_base) / (i_next - i_base)) * (c_next - c_base))

    return(color)


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


print("Starting processing now:",  str(datetime.now()))

# background default
background = (0, 0, 0, 255)

# walk_length = 100_000
palette_length = 256

# Build a color lookup table once, based on desired palette length
sd = plt.cm.gist_rainbow._segmentdata
r_len = len(sd['red'])
g_len = len(sd['green'])
b_len = len(sd['blue'])

colors = []
anticolors = []
# Create a separate color for each palette entry from color map calculations.
for col in range(0, palette_length):
    c_val = col / palette_length
    r = int(_find_color(c_val, sd['red'], r_len) * 255)
    g = int(_find_color(c_val, sd['green'], g_len) * 255)
    b = int(_find_color(c_val, sd['blue'], b_len) * 255)
    color = (r, g, b)
    colors.append(color)
    anticolors.append(invert(color))

# Create a grayscale lookup table
grays = [(x, x, x) for x in range(palette_length)]

# Instantiate the command line parser
parser = argparse.ArgumentParser(description="edges: edge-enhancement and posterization application")

# Optional argument for filename (defaults to 'test.jpg')
parser.add_argument('--fn',
                    action="store",
                    dest="fn",
                    help="override default filename",
                    default="test.jpg"
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
parser.add_argument('--do', action='store_true', help="display original")

# Optional argument to compute and display grayscale image
parser.add_argument('--dgs', action='store_true', help="compute and display grayscale")

# Optional argument to display unedged posterized images
parser.add_argument('--dp', action='store_true', help="compute and display plain posters")

# Optional argument to display averaged image
parser.add_argument('--da', action='store_true', help="display averaged")

# Optional argument to display grayscale averaged image
parser.add_argument('--dags', action='store_true', help="display averaged grayscale")

# Optional argument to display vertical differences image
parser.add_argument('--dv', action='store_true', help="display vertical differences")

# Optional argument to display horizontal differences image
parser.add_argument('--dh', action='store_true', help="display horizontal differences")

# Optional argument to autosave the intermediate files
parser.add_argument('--sv', action='store_true', help="autosave displayed intermediate images")

# Optional argument to autosave the edges file
parser.add_argument('--se', action='store_true', help="autosave edges image")

args = parser.parse_args()
print("fn", args.fn)
print("th", args.th)
print("bs", args.bs)
print("do", args.do)
print("dgs", args.dgs)
print("dp", args.dp)
print("da", args.da)
print("dags", args.dags)
print("dv", args.dv)
print("dh", args.dh)
print("sv", args.sv)
print("se", args.se)
# open the file into an image object.
im = Image.open(args.fn)
pixels = im.load()

if args.do:
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

fn = im.filename.split(".")
saveBase = saveDirStr + "/" + today.__format__("%Y%m%d") + "_" + fn[0] + "_"

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

if args.dp:
    pIm.show()
    iIm.show()
    if args.sv:
        pIm.save(saveBase + "p.jpg", format="JPEG", quality=95)
        iIm.save(saveBase + "pi.jpg", format="JPEG", quality=95)

print("Posterized version done.",  str(datetime.now()))
print("Anti-posterized version done.")

if args.dgs:
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
        
if args.da:
    avgIm.show()
    if args.sv:
        avgIm.save(saveBase + "a.jpg", format="JPEG", quality=95)
print("Averaged version done.",  str(datetime.now()))

if args.dags:
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

if args.dv:
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

if args.dh:
    hDiffIm.show()
    if args.sv:
        hDiffIm.save(saveBase + "ah.jpg", format="JPEG", quality=95)
print("Horizontal edges version done.", max_hDiff,  str(datetime.now()))

# Now get funky -- overlay edges on posterized version
funkyIm = Image.new('RGB', im.size, background)
fPixels = funkyIm.load()

afunkyIm = Image.new('RGB', im.size, background)
afPixels = afunkyIm.load()

threshhold = args.th
for x in range(0, im.size[0]):
    # NOTE: Use the vertical differences image to keep track of edge pixels used
    for y in range(0, im.size[1]):
        if (vPixels[x, y][0] > threshhold) or (hPixels[x, y][0] > threshhold):
            pixel = (0, 0, 0)
            apixel = pixel
            # Mark the edge pixels in the smoothed image, too
            aPixels[x, y] = pixel
            # Edge pixel, make white
            vPixels[x, y] = (255, 255, 255)
        else:
            bright = gaPixels[x, y][0]
            pixel = colors[bright]
            apixel = anticolors[bright]
            # Non-edge pixel, make black
            vPixels[x, y] = (0, 0, 0)

        fPixels[x, y] = pixel
        afPixels[x, y] = apixel

# Display and save the representation of the edges.
if args.se:
    vDiffIm.show()
    vDiffIm.save(saveBase + "ae.jpg", format="JPEG", quality=95)

funkyIm.show()
funkyIm.save(saveBase + "ap.jpg", format="JPEG", quality=95)
print("Posterized and edged version done.",  str(datetime.now()))

afunkyIm.show()
afunkyIm.save(saveBase + "api.jpg", format="JPEG", quality=95)
print("Anti-posterized and edged version done.")

# Display and save the smoothed and edged version of the original image
avgIm.show()
avgIm.save(saveBase + "se.jpg", format="JPEG", quality=95)
