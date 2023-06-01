#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import argparse

from datetime import date
from datetime import datetime
from pathlib import Path
from PIL import Image
from os.path import basename
from os.path import exists

# Instantiate the command line parser
parser = argparse.ArgumentParser(description="cli_inverter: color plane inverter and swapper")

# Optional argument for filename (defaults to 'test.jpg')
parser.add_argument('--fn',
                    action="store",
                    dest="fn",
                    help="override default filename",
                    default="test.jpg"
                    )

# Optional argument to invert the red plane
parser.add_argument('--ir', action='store_true', help="invert reds")

# Optional argument to invert the green plane
parser.add_argument('--ig', action='store_true', help="invert greens")

# Optional argument to invert the blue plane
parser.add_argument('--ib', action='store_true', help="invert blues")

# Optional argument to swap the red and green planes
parser.add_argument('--srg', action='store_true', help="swap red and green")

# Optional argument to swap the red and blue planes
parser.add_argument('--srb', action='store_true', help="swap red and blue")

# Optional argument to swap the green and blue planes
parser.add_argument('--sgb', action='store_true', help="swap green and blue")

args = parser.parse_args()
print("fn\t", args.fn)
print("ir\t", args.ir)
print("ig\t", args.ig)
print("ib\t", args.ib)
print("srg\t", args.srg)
print("srb\t", args.srb)
print("sgb\t", args.sgb)

# default background for the new image: black and fully transparent
background = (0, 0, 0, 0)

# create a tag based on what planes are being inverted
saveOpsStr = ""

# build the palettes based on the command line options
reds = []
greens = []
blues = []

if args.ir:
    saveOpsStr += "r"
    for c in range(255, -1, -1):
        reds.append(c)
else:
    for c in range(256):
        reds.append(c)

if args.ig:
    saveOpsStr += 'g'
    for c in range(255, -1, -1):
        greens.append(c)
else:
    for c in range(256):
        greens.append(c)

if args.ib:
    saveOpsStr += "b"
    for c in range(255, -1, -1):
        blues.append(c)
else:
    for c in range(256):
        blues.append(c)

#print(len(reds), reds)
#print(len(greens), greens)
#print(len(blues), blues)

# Set up for image file save.
today = date.today()
saveDirStr = "./" + today.__format__("%Y%m%d")
saveDir = Path(saveDirStr)

if not saveDir.exists():
    print("Createing the save directory:", saveDirStr)
    saveDir.mkdir()

# Build the base file name string
fullname = basename(args.fn)
nameParts = fullname.split(".")
name = ""
for index in range(len(nameParts) - 1):
    name += nameParts[index]
saveBaseStr = saveDirStr + "/"
saveBaseStr += today.__format__("%Y%m%d") + "_"
saveBaseStr += name + "_" + saveOpsStr

print(name)
print(saveBaseStr)

# open the original file into an image object.
oIm = Image.open(args.fn)
pixels = oIm.load()

# create a canvas for the manipulated file
iIm = Image.new('RGB', oIm.size, background)
iPixels = iIm.load()

# do any requested inversions
for x in range(oIm.size[0]):
    for y in range(oIm.size[1]):
        r, g, b = pixels[x, y]
        iPixels[x, y] = (reds[r], greens[g], blues[b])

#do any requested swaps
# swap red and green planes
if args.srg:
    saveBaseStr += '_sgr'
    for x in range(oIm.size[0]):
        for y in range(oIm.size[1]):
            r, g, b = iPixels[x, y]
            iPixels[x, y] = (g, r, b)

# swap red and blue planes
if args.srb:
    saveBaseStr += '_sbr'
    for x in range(oIm.size[0]):
        for y in range(oIm.size[1]):
            r, g, b = iPixels[x, y]
            iPixels[x, y] = (b, g, r)

# swap green and blue planes
if args.sgb:
    saveBaseStr += '_sgb'
    for x in range(oIm.size[0]):
        for y in range(oIm.size[1]):
            r, g, b = iPixels[x, y]
            iPixels[x, y] = (r, b, g)

iIm.show()
iIm.save(saveBaseStr + ".jpg", format="JPEG", quality=95)
