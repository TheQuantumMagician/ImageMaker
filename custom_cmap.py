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
    # Create a 256 length palette from a colormap
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


# Reddish, Greenish, Purplish
RdGrPu = ((175, 5, 75), (135, 185, 0), (100, 45, 235))
fullProcess(RdGrPu, 'RdGrPu')

# Neon Green, Hot Pink, Purplish
NgHpPu = ((12, 255, 12), (215, 37, 222), (98, 88, 196))
fullProcess(NgHpPu, 'NgHpPu')

# Blue, Orange, Green
BlOrGr = ((5, 10, 100), (250, 115, 10), (120, 205, 40))
fullProcess(BlOrGr, 'BlOrGr')

# Purplish, Bluish, Cyanish
PuBlCy = ((75, 0, 110), (55, 120, 195), (130, 205, 255))
fullProcess(PuBlCy, 'PuBlCy')

# Reddish, Orangish, Brown
RdOrBr = ((230, 0, 0), (250, 115, 0), (140, 50, 5))
fullProcess(RdOrBr, 'RdOrBr')

# Reddish, Orangish, Brown
RdOrBl = ((230, 0, 0), (250, 115, 0), (5, 5, 230))
fullProcess(RdOrBr, 'RdOrBl')

# Slate, Hot Pink, Bluish
SlHpBl = ((35, 75, 100), (240, 15, 220), (5, 5, 230))
fullProcess(SlHpBl, 'SlHpBl')

# Pale Green, Charcoal, Pink
PgChPi = ((5, 160, 75), (90, 105, 110), (225, 80, 200))
fullProcess(PgChPi, 'PgChPi')

# Orangish, Reddish, Purplish
OrRdPu = ((225, 120, 5), (190, 65, 65), (95, 10, 235))
fullProcess(OrRdPu, 'OrRdPu')

# cyclical RGB
CR = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0))
fullProcess(CR, 'CR')

# RYGCBMR -- Cyclical Rainbow
R = ((255, 0, 0),
     (255, 255, 0),
     (0, 255, 0),
     (0, 255, 255),
     (0, 0, 255),
     (255, 0, 255),
     (255, 0, 0),
     )
fullProcess(R, 'R')

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
fullProcess(IL, 'IL')

jList = list()
jList.extend(PgChPi)
jList.extend(RdOrBl)
fullProcess(jList, "PgChPiRdOrBl")

# Gold, Magenta, Blue
GoMaBl = ((245, 195, 5), (153, 0, 250), (5, 15, 205))
fullProcess(GoMaBl, "GoMaBl")
