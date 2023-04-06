#! /Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import argparse

import matplotlib.pyplot as plt
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
# Create a separate color for each palette entry from color map calculations.
for col in range(0, palette_length):
    c_val = col / palette_length
    r = int(_find_color(c_val, sd['red'], r_len) * 255)
    g = int(_find_color(c_val, sd['green'], g_len) * 255)
    b = int(_find_color(c_val, sd['blue'], b_len) * 255)
    colors.append((r, g, b))

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
                    default = 16
                    )

# Optional argument to display compute and display grayscale image
parser.add_argument('--dgs', action='store_true', help="compute and dispaly grayscale")

# Optional argument to display unedged posterized image
parser.add_argument('--dp', action='store_true', help="display plain poster")

args = parser.parse_args()
print(args.fn)
print(args.th)
print(args.dgs)
print(args.dp)

# open the file into an image object.
im = Image.open(args.fn)
pixels = im.load()

# create a canvas to posterize into
pIm = Image.new('RGB', im.size, background)
pPixels = pIm.load()

# creat a canvas to invert posterized version into
iIm = Image.new('RGB', im.size, background)
iPixels = iIm.load()

for x in range(0, im.size[0]):
    for y in range(0, im.size[1]):
        pPixels[x, y] = colors[get_brightness(im.getpixel((x, y)))]
        iPixels[x, y] = invert(pPixels[x, y])

print([x for x in pPixels[0,0]])

pIm.show()
iIm.show()
