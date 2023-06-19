#
# custom_cmap.py
#
# Create, display, plot, and save to file custom colormaps from color lists.
#
# 20230503 smb -- Created
#

import json

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap as lsc

from PIL import Image

from datetime import datetime


def createCDict(colors):
    # Create an evenly spaced cdict dictionary from a list of colors
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
        cdict['red'][color].append(colors[color][0] / 255)
        cdict['red'][color].append(colors[color][0] / 255)
        cdict['green'][color].append(colors[color][1] / 255)
        cdict['green'][color].append(colors[color][1] / 255)
        cdict['blue'][color].append(colors[color][2] / 255)
        cdict['blue'][color].append(colors[color][2] / 255)

    return(cdict)


def custCM(cdict, name):
    # Create a custom colormap from a color dictionary
    return(lsc(name, segmentdata=cdict, N=256))


def palette(cm):
    # Create a palette from a colormap
    ncColors = []

    for c in range(256):
        color = cm(c / 255)

        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)

        ncColors.append((r, g, b))

    return(ncColors)


def colorbar(colors):
    # Create a colorbar mage from a palette
    cbIm = Image.new('RGB', (5 * 256, 64))
    cbPixels = cbIm.load()

    for y in range(64):
        for x in range(256 * 5):
            cbPixels[x, y] = colors[int(x / 5)]

    cbIm.show()


def plot_linearmap(cm):
    # plot a line map of a colormap
    rgba = cm(np.linspace(0, 1, 256))

    fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
    col = ['r', 'g', 'b']
    for xx in [0.0, 0.25, 0.5, 0.75, 1.0]:
        ax.axvline(xx, color='0.7', linestyle='--')
    for i in range(3):
        ax.plot(np.arange(256)/256, rgba[:, i], color=col[i])
    ax.set_xlabel('index')
    ax.set_ylabel('RGB')

    plt.title(cm.name)
    plt.show()


# Write the provide palette out as JSON data
def writeColors(colors, name):
    cpFP = open(name + '.json', 'wt')
    json.dump(colors, cpFP, indent=4)
    cpFP.close()
    print('Custom palette', name + '.json', 'written to disk.')


# Sort a palette based on the gray value brightness of the colors
def bSort(palette):
    # create a version of the input palette sorted by brightness
    # first, create a dictionary of color keyed by brightness
    bDict = dict()
    for color in palette:
        # calcualte the current color's brightness
        lum = ((0.3 * color[0]) + (0.59 * color[1]) + (0.11 * color[2]))
        if lum in bDict:
            # already have at least one color this bright, add this color to the list
            tmpList = list()
            for shade in bDict[lum]:
                tmpList.append(shade)
            tmpList.append(color)
            bDict[lum] = tmpList
        else:
            # first color at this brightness, add to dictionary
            bDict[lum] = [color]

    # new, empty palette
    bPal = list()
    # sorting the keys gives us the brightness order
    bKeys = sorted(bDict.keys())
    for key in bKeys:
        # get all the colors at this brightness
        colors = list(bDict[key])
        for color in colors:
            # add color to the new palette
            bPal.append(color)

    return bPal


def customBCM(name, palette):

    # palette in (0..255) range, need in (0.0..1.0) range for lsc.from_list()
    newPal = list()
    for color in palette:
        # convert color from tuple of 3 (0..255) values to tuple of (0.0..1.0) values
        r = color[0] / 255
        g = color[1] / 255
        b = color[2] / 255
        newPal.append((r, g, b))

    cBCM = lsc.from_list(name, newPal, N=len(newPal))

    return cBCM


# Steps:
#     1. Create a CDict from a color list
#     2. Create colormap from CDict
#     3. Create palette from colormap
#     4. Write the palette to a JSON file.
#     5. Draw colorbar from colormap
#     6. Plot colormap lines
def fullProcess(colors, name):
    
    Dict = createCDict(colors)
    Cm = custCM(Dict, name)
    Colors = palette(Cm)
    writeColors(Colors, name)
    colorbar(Colors)
    plot_linearmap(Cm)


def cmapProcess(name):
    cm = plt.cm.get_cmap(name)
    colors = palette(cm)
    colorbar(colors)
    plot_linearmap(cm)


def customCmapProcess(name, cm):
    colors = palette(cm)
    colorbar(colors)
    plot_linearmap(cm)
    writeColors(colors, name)


# Reddish, Greenish, Purplish
RdGrPu = ((175, 5, 75), (135, 185, 0), (100, 45, 235))
#fullProcess(RdGrPu, 'RdGrPu')

# Neon Green, Hot Pink, Purplish
NgHpPu = ((12, 255, 12), (215, 37, 222), (98, 88, 196))
#fullProcess(NgHpPu, 'NgHpPu')

# Blue, Orange, Green
BlOrGr = ((5, 10, 100), (250, 115, 10), (120, 205, 40))
#fullProcess(BlOrGr, 'BlOrGr')

# Purplish, Bluish, Cyanish
PuBlCy = ((75, 0, 110), (55, 120, 195), (130, 205, 255))
#fullProcess(PuBlCy, 'PuBlCy')

## Purplish, Bluish, Cyanish Extended
PuBlCyE = ((75, 0, 110), (55, 120, 195), (130, 205, 255), (130, 205, 255))
#fullProcess(PuBlCy, 'PuBlCyE')

# Reddish, Orangish, Brown
RdOrBr = ((230, 0, 0), (250, 115, 0), (140, 50, 5))
#fullProcess(RdOrBr, 'RdOrBr')

# Reddish, Orangish, Brown Extended
RdOrBrE = ((230, 0, 0), (250, 115, 0), (140, 50, 5), (140, 50, 5))
#fullProcess(RdOrBr, 'RdOrBrE')

# Reddish, Orangish, Brown
RdOrBl = ((230, 0, 0), (250, 115, 0), (5, 5, 230))
#fullProcess(RdOrBr, 'RdOrBl')

# Slate, Hot Pink, Bluish
SlHpBl = ((35, 75, 100), (240, 15, 220), (5, 5, 230))
#fullProcess(SlHpBl, 'SlHpBl')

# Pale Green, Charcoal, Pink
PgChPi = ((5, 160, 75), (90, 105, 110), (225, 80, 200))
#fullProcess(PgChPi, 'PgChPi')

# Orangish, Reddish, Purplish
OrRdPu = ((225, 120, 5), (190, 65, 65), (95, 10, 235))
#fullProcess(OrRdPu, 'OrRdPu')

# cyclical RGB
CR = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0))
#fullProcess(CR, 'CR')

# RYGCBMR -- Cyclical Rainbow
R = ((255, 0, 0),       # red
     (255, 255, 0),     # yellow
     (0, 255, 0),       # green
     (0, 255, 255),     # cyan
     (0, 0, 255),       # blue
     (255, 0, 255),     # magenta
     (255, 0, 0),       # red
     )
#fullProcess(R, 'R')

# RYGCBMMBCGYR rainbow
IL = ((255, 0, 0),      # red
      (255, 255, 0),    # yellow
      (0, 255, 0),      # green
      (0, 255, 255),    # cyan
      (0, 0, 255),      # blue
      (255, 0, 255),    # magenta
      (255, 0, 255),    # magenta
      (0, 0, 255),      # blue
      (0, 255, 255),    # cyan
      (0, 255, 0),      # green
      (255, 255, 0),    # yellow
      (255, 0, 0),      # red
      )
#fullProcess(IL, 'IL')

PgChPiRdOrBl = list()
PgChPiRdOrBl.extend(PgChPi)
PgChPiRdOrBl.extend(RdOrBl)
#fullProcess(PgChPiRdOrBl, "PgChPiRdOrBl")

# Gold, Magenta, Blue
GoMaBl = ((245, 195, 5), (153, 0, 250), (5, 15, 205))
#fullProcess(GoMaBl, "GoMaBl")

# Slate, Gray, Light Blue
SlGyLb = ((100, 125, 145), (200, 205, 200), (150, 210, 255))
#fullProcess(SlGyLb, "SlGyLb")

# Slate, Gray, Light Blue Extended
SlGyLbE = ((100, 125, 145), (200, 205, 200), (150, 210, 255), (150, 210, 255))
#fullProcess(SlGyLbE, "SlGyLbE")

# Banded Grayscale
BGS = ((0, 0, 0),
       (0, 0, 0),
       (64, 64, 64),
       (64, 64, 64),
       (128, 128, 128),
       (128, 128, 128),
       (194, 194, 194),
       (194, 194, 194),
       (255, 255, 255),
       (255, 255, 255),
       )
#fullProcess(BGS, "BGS")

# Banded Grayscale and Rainbow
BGSR = ((0, 0, 0),
       (0, 0, 0),
       (64, 64, 64),
       (64, 64, 64),
       (128, 128, 128),
       (128, 128, 128),
       (194, 194, 194),
       (194, 194, 194),
       (255, 255, 255),
       (255, 255, 255),
       (255, 0, 0),       # red
       (255, 255, 0),     # yellow
       (0, 255, 0),       # green
       (0, 255, 255),     # cyan
       (0, 0, 255),       # blue
       (255, 0, 255),     # magenta
       (255, 0, 0),       # red
       )
#fullProcess(BGSR, "BGSR")

# Grayscale and Rainbow
GSR = ((0, 0, 0),
       (32, 32, 32),
       (64, 64, 64),
       (96, 96, 96),
       (128, 128, 128),
       (160, 160, 160),
       (192, 192, 192),
       (224, 224, 224),
       (255, 255, 255),
       (255, 0, 0),       # red
       (255, 128, 0),     # orange
       (255, 255, 0),     # yellow
       (128, 255, 0),     # yellow-green
       (0, 255, 0),       # green
       (0, 255, 128),     # blue-green
       (0, 255, 255),     # cyan
       (0, 128, 255),     # aqua
       (0, 0, 255),       # blue
       (128, 0, 255),     # purple
       (255, 0, 255),     # magenta
       (255, 0, 128),     # maroon
       (255, 0, 0),       # red
       )
#fullProcess(GSR, "GSR")

# Grayscale and ROYG
GSROYG = ((0, 0, 0),
          (32, 32, 32),
          (64, 64, 64),
          (96, 96, 96),
          (128, 128, 128),
          (160, 160, 160),
          (192, 192, 192),
          (224, 224, 224),
          (255, 255, 255),
          (255, 0, 0),       # red
          (255, 64, 0),
          (255, 128, 0),     # orange
          (255, 192, 0),
          (255, 255, 0),     # yellow
          (192, 255, 0),
          (128, 255, 0),     # chartreuse
          (64, 255, 0),
          (0, 255, 0),       # green
          (0, 0, 0),
          )
#fullProcess(GSROYG, "GSROYG")

# Yellow, Red, Orange
YRO = ((195, 185, 10),
       (155, 5, 0),
       (255, 170, 45),
       )
#fullProcess(YRO, "YRO")

CBR = ((255, 0, 0),       # red
       (255, 0, 0),       # red
       (255, 128, 0),     # orange
       (255, 255, 0),     # yellow
       (255, 255, 0),     # yellow
       (128, 255, 0),     # yellow-green
       (0, 255, 0),       # green
       (0, 255, 0),       # green
       (0, 255, 128),     # blue-green
       (0, 255, 255),     # cyan
       (0, 255, 255),     # cyan
       (0, 128, 255),     # aqua
       (0, 0, 255),       # blue
       (0, 0, 255),       # blue
       (128, 0, 255),     # purple
       (255, 0, 255),     # magenta
       (255, 0, 255),     # magenta
       (255, 0, 128),     # maroon
       (255, 0, 0),       # red
       )
#fullProcess(CBR, "CBR")

CBrOrYeRd = ((192, 96, 48),
            (192, 96, 0),
            (192, 192, 0),
            (192, 0, 0),
            (192, 96, 48),
            )
#fullProcess(CBrOrYeRd, "CBrOrYeRd")

RdBk = ((255, 0, 0),
      (0, 0, 0),
      )
#fullProcess(RdBk, "RdBk")

BkRdBkGrBkBlBk = ((0, 0, 0),
                (255, 0, 0),
                (0, 0, 0),
                (0, 255, 0),
                (0, 0, 0),
                (0, 0, 255),
                (0, 0, 0),
                )
#fullProcess(BkRdBkGrBkBlBk, "BkRdBkGrBkBlBk")

BkRdBkOrBkYeBk = ((0, 0, 0),
                 (255, 0, 0),
                 (0, 0, 0),
                 (255, 128, 0),
                 (0, 0, 0),
                 (255, 255, 0),
                 (0, 0, 0),
                 )
#fullProcess(BkRdBkOrBkYeBk, "BkRdBkOrBkYeBk")

RdBkBl = ((255, 0, 0),
          (0, 0, 0),
          (0, 0, 255),
          )
#fullProcess(RdBkBl, "RdBkBl")

RdWh = ((255, 0, 0),
      (255, 255, 255),
      )
#fullProcess(RdWh, "RdWh")

RdWhBl = ((255, 0, 0),
          (255, 255, 255),
          (0, 0, 255),
          )
#fullProcess(RdWhBl, "RdWhBl")

# Bright Purplish, Bluish, Cyanish
BPuBlCy = ((174, 0, 255), (72, 157, 255), (130, 205, 255))
#fullProcess(BPuBlCy, 'BPuBlCy')

# Reddish, Greenish, Purplish
BRdGrPu = ((255, 10, 110), (185, 255, 0), (110, 50, 255))
#fullProcess(RdGrPu, 'BRdGrPu')

# Neon Green, Hot Pink, Purplish
NgHpPu = ((12, 255, 12), (250, 45, 255), (130, 115, 255))
#fullProcess(NgHpPu, 'BNgHpPu')

DMaMnRdOrYe = ((0, 0, 0),       # black
               (32, 0, 32),     # magenta
               (64, 0, 32),    # maroon
               (96, 0, 0),     # red
               (128, 64, 0),   # orange
               (160, 160, 0),   # yellow
               (192, 192, 192), # white
               )
#fullProcess(DMaMnRdOrYe, "DMaMnRdOrYe")

OrWh = ((255, 126, 64), (255, 255, 255))
#fullProcess(OrWh, "OrWh")

BkOr = ((0, 0, 0), (255, 126, 64))
#fullProcess(BkOr, "BkOr")

# Crayola Crayon 8-count Box
Crayola8 = ((35, 35, 35),       # Black
            (180, 103, 77),     # Brown
            (238, 32, 77),      # Red
            (255, 117, 56),     # Orange
            (252, 232, 131),    # Yellow
            (28, 172, 120),     # Green
            (31, 117, 254),     # Blue
            (146, 110, 174),    # Violet (Purple)
            )
#fullProcess(Crayola8, "Crayola8")

# Crayola Crayon 16-count Box
Crayola16 = ((35, 35, 35),      # Black
             (180, 103, 77),    # Brown
             (192, 68, 143),    # Red Violet
             (238, 32, 77),     # Red
             (255, 83, 73),     # Red Orange
             (255, 117, 56),    # Orange
             (255, 182, 83),    # Yellow Orange
             (252, 232, 131),   # Yellow
             (197, 227, 132),   # Yellow Green
             (28, 172, 120),    # Green
             (25, 158, 189),    # Blue Green
             (31, 117, 254),    # Blue
             (115, 102, 189),   # Blue Violet
             (146, 110, 174),   # Violet (Purple)
             (255, 170, 204),   # Carnation Pink
             (237, 237, 237),   # White
            )
#fullProcess(Crayola16, "Crayola16")

# Crayola Crayon 24-count Box
Crayola24 = ((35, 35, 35),      # Black
             (149, 145, 140),   # Gray
             (180, 103, 77),    # Brown
             (253, 217, 181),   # Apricot
             (192, 68, 143),    # Red Violet
             (247, 83, 148),    # Violet Red
             (255, 170, 204),   # Carnation Pink
             (247, 83, 248),    # Scarlet
             (238, 32, 77),     # Red
             (255, 83, 73),     # Red Orange
             (255, 117, 56),    # Orange
             (255, 182, 83),    # Yellow Orange
             (252, 232, 131),   # Yellow
             (240, 232, 145),   # Green Yellow
             (197, 227, 132),   # Yellow Green
             (28, 172, 120),    # Green
             (25, 158, 189),    # Blue Green
             (29, 172, 214),    # Cerulean
             (31, 117, 254),    # Blue
             (46, 80, 144),     # Bluetiful
             (93, 118, 203),    # Indigo
             (115, 102, 189),   # Blue Violet
             (146, 110, 174),   # Violet (Purple)
             (237, 237, 237),   # White
            )
#fullProcess(Crayola24, "Crayola24")

# Crayola Crayon 32-count Box
Crayola32 = ((35, 35, 35),      # Black                   8
             (149, 145, 140),   # Gray                   24
             (180, 103, 77),    # Brown                   8
             (188, 93, 88),     # Chestnut               32
             (250, 167, 108),   # Tan                    32
             (253, 188, 180),   # Melon                  32
             (253, 217, 181),   # Apricot                24
             (255, 207, 171),   # Peach                  32
             (192, 68, 143),    # Red Violet             16
             (247, 83, 148),    # Violet Red             24
             (255, 170, 204),   # Carnation Pink         16
             (247, 83, 248),    # Scarlet                24
             (238, 32, 77),     # Red                     8
             (255, 83, 73),     # Red Orange             16
             (255, 117, 56),    # Orange                  8
             (255, 182, 83),    # Yellow Orange          16
             (252, 232, 131),   # Yellow                  8
             (240, 232, 145),   # Green Yellow           24
             (197, 227, 132),   # Yellow Green           16
             (28, 172, 120),    # Green                   8
             (25, 158, 189),    # Blue Green             16
             (29, 172, 214),    # Cerulean               24
             (128, 218, 235),   # Sky Blue               32
             (31, 117, 254),    # Blue                    8
             (46, 80, 144),     # Bluetiful              24
             (93, 118, 203),    # Indigo                 24
             (115, 102, 189),   # Blue Violet            16
             (146, 110, 174),   # Violet (Purple)         8
             (176, 183, 198),   # Cadet Blue             32
             (205, 164, 222),   # Wisteria               32
             (219, 215, 210),   # Timberwolf             32
             (237, 237, 237),   # White                  16
            )
#fullProcess(Crayola32, "Crayola32")

# Crayola Crayon 48-count Box
Crayola48 = ((35, 35, 35),      # Black                       8
             (149, 145, 140),   # Gray                       24
             (165, 105, 79),    # Sepia                      48
             (180, 103, 77),    # Brown                       8
             (188, 93, 88),     # Chestnut                   32
             (186, 184, 108),   # Olive Green                48
             (205, 74, 74),     # Mahogany                   48
             (214, 138, 89),    # Raw Sienna                 48
             (234, 126, 93),    # Burnt Sienna               48
             (222, 179, 136),   # Tumbleweed                 48
             (250, 167, 108),   # Tan                        32
             (236, 234, 190),   # Spring Green               48
             (239, 152, 170),   # Mauvelous                  48
             (255, 155, 170),   # Salmon                     48
             (252, 180, 213),   # Lavender                   48
             (253, 188, 180),   # Melon                      32
             (253, 217, 181),   # Apricot                    24
             (255, 189, 136),   # Macaroni and Cheese        48
             (255, 207, 171),   # Peach                      32
             (255, 217, 117),   # Goldenrod                  48
             (192, 68, 143),    # Red Violet                 16
             (247, 83, 148),    # Violet Red                 24
             (255, 170, 204),   # Carnation Pink             16
             (247, 83, 248),    # Scarlet                    24
             (238, 32, 77),     # Red                         8
             (255, 83, 73),     # Red Orange                 16
             (255, 117, 56),    # Orange                      8
             (159, 226, 191),   # Sea Green                  48
             (168, 228, 160),   # Granny Smith Apple         48
             (255, 182, 83),    # Yellow Orange              16
             (252, 232, 131),   # Yellow                      8
             (240, 232, 145),   # Green Yellow               24
             (197, 227, 132),   # Yellow Green               16
             (28, 172, 120),    # Green                       8
             (25, 158, 189),    # Blue Green                 16
             (29, 172, 214),    # Cerulean                   24
             (128, 218, 235),   # Sky Blue                   32
             (154, 206, 235),   # Cornflower                 48
             (31, 117, 254),    # Blue                        8
             (46, 80, 144),     # Bluetiful                  24
             (93, 118, 203),    # Indigo                     24
             (115, 102, 189),   # Blue Violet                16
             (146, 110, 174),   # Violet (Purple)             8
             (157, 129, 186),   # Purple Mountains' Majesty  48
             (176, 183, 198),   # Cadet Blue                 32
             (205, 164, 222),   # Wisteria                   32
             (219, 215, 210),   # Timberwolf                 32
             (237, 237, 237),   # White                      16
            )
fullProcess(Crayola48, "Crayola48")

bC8 = bSort(Crayola8)
fullProcess(bC8, "bC8")

bC16 = bSort(Crayola16)
#fullProcess(bC16, "bC16")

bC24 = bSort(Crayola24)
#fullProcess(bC24, "bC24")

bC32 = bSort(Crayola32)
#fullProcess(bC32, "bC32")

bC48 = bSort(Crayola48)
fullProcess(bC48, "bC48")

# sort by brightness, and then banded, palettes
cmBC8 = customBCM("cmBC8", bC8)
customCmapProcess("cmBC8", cmBC8)

cmBC16 = customBCM("cmBC16", bC16)
#customCmapProcess("cmBC16", cmBC16)

cmBC24 = customBCM("cmBC24", bC24)
#customCmapProcess("cmBC24", cmBC24)

cmBC32 = customBCM("cmBC32", bC32)
#customCmapProcess("cmBC32", cmBC32)

cmBC48 = customBCM("cmBC48", bC48)
customCmapProcess("cmBC48", cmBC48)

# Create to compare calculated brightness vs sorting on (g, r, b)
SBC48_GRB = sorted(Crayola48, key=lambda x: (x[1], x[0], x[2]))
fullProcess(SBC48_GRB, "SBC48_GRB")

cmSBC48_GRB = customBCM("cmSBC48_GRB", SBC48_GRB)
customCmapProcess("cmSBC48_GRB", cmSBC48_GRB)

# Create colorbars and linear maps from all of the builtin cmaps
# Uncomment the 7 lines below to see all built-in colormaps as colorbars and linear maps
#import matplotlib as mpl
#
#cmap_names = getattr(mpl, 'colormaps')
#
#for cmap_name in sorted(cmap_names):
#    print(cmap_name)
#    cmapProcess(cmap_name)
