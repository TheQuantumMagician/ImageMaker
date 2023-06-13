#
# custom_cmap.py
#
# Create, display, plot, and save to file custom colormaps from color lists.
#
# 20230503 smb -- Created
#

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

import json
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
    return(LinearSegmentedColormap(name, segmentdata=cdict, N=256))


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


# Steps:
#     1. Create a CDict from a color list
#     2. Create colormap from CDict
#     3. Create palette from colormap
#     4. Draw colorbar from colormap
#     5. Plot colormap lines
#     6. Write the palette to a JSON file.
def fullProcess(colors, name):
    
    Dict = createCDict(colors)
    Cm = custCM(Dict, name)
    Colors = palette(Cm)
    colorbar(Colors)
    plot_linearmap(Cm)
    writeColors(Colors, name)


def cmapProcess(name):
    cm = plt.cm.get_cmap(name)
    colors = palette(cm)
    colorbar(colors)
    plot_linearmap(cm)
#    writeColors(Colors, name)



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
fullProcess(OrWh, "OrWh")

BkOr = ((0, 0, 0), (255, 126, 64))
fullProcess(BkOr, "BkOr")

# Create colorbars and linear maps for some of the builtin cmaps
# Uncomment the block below to see all default colormaps as colorbars and linear maps
#import matplotlib as mpl
#
#cmap_names = getattr(mpl, 'colormaps')
#
#for cmap_name in sorted(cmap_names):
#    print(cmap_name)
#    cmapProcess(cmap_name)
