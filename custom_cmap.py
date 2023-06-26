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


def plot_linearmap_offline(cm):
    # plot a line map of a colormap in the browser
    from plotly import offline
    from plotly.graph_objs import Layout
    # get the rgb data from the colormap as a 256 length list
    rgba = cm(np.linspace(0, 1, 256))
    x_values = np.arange(256)/256

    traces = []
    traces.append(dict(x = x_values, y = rgba[:, 0], name='red', marker=dict(color='red'), line=dict(width=4)))    
    traces.append(dict(x = x_values, y = rgba[:, 1], name='green', marker=dict(color='green'), line=dict(width=4)))    
    traces.append(dict(x = x_values, y = rgba[:, 2], name='blue', marker=dict(color='blue'), line=dict(width=4)))    

    x_axis_config = {'title': 'index'}
    y_axis_config = {'title': 'RGB'}
    my_layout = Layout(title=cm.name, xaxis=x_axis_config, yaxis=y_axis_config)
    offline.plot({'data': traces, 'layout': my_layout}, filename=cm.name + 'linearmap.html')


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
    # Use a lambda to do the sorting
    lbPal = sorted(palette, key=lambda x: ((0.59 * x[1]) + (0.3 * x[0]) + (0.11 * x[2])))
    return lbPal


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
    cmNew = custCM(Dict, name)
    Colors = palette(cmNew)
    writeColors(Colors, name)
    colorbar(Colors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)


def cmapProcess(name):
    cmNew = plt.cm.get_cmap(name)
    colors = palette(cmNew)
    colorbar(colors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)


def customCmapProcess(name, cmNew):
    colors = palette(cmNew)
    colorbar(colors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)
    writeColors(colors, name)


def _fPAB(palette, name):
    # create both fade and banded transition palettes, display colorbar and linearmap
    cmName = 'cm' + name
    fullProcess(palette, name)
    newCm = customBCM(cmName, palette)
    customCmapProcess(cmName, newCm)
    

def fullProcessAndBanded(palette, name, bsort=False):
    # create both fade and banded transtions, and possible brightness sorted version
    _fPAB(palette, name)
    if bsort:
        bsPalette = bSort(palette)
        bsName = 'b' + name
        _fPAB(bsPalette, bsName)



# Reddish, Greenish, Purplish
RdGrPu = ((175, 5, 75), (135, 185, 0), (100, 45, 235))
#fullProcessAndBanded(RdGrPu, 'RdGrPu', True)

# Neon Green, Hot Pink, Purplish
NgHpPu = ((12, 255, 12), (215, 37, 222), (98, 88, 196))
#fullProcessAndBanded(NgHpPu, 'NgHpPu', True)

# Blue, Orange, Green
BlOrGr = ((5, 10, 100), (250, 115, 10), (120, 205, 40))
#fullProcessAndBanded(BlOrGr, 'BlOrGr', True)

# Purplish, Bluish, Cyanish
PuBlCy = ((75, 0, 110), (55, 120, 195), (130, 205, 255))
#fullProcessAndBanded(PuBlCy, 'PuBlCy', True)

## Purplish, Bluish, Cyanish Extended
PuBlCyE = ((75, 0, 110), (55, 120, 195), (130, 205, 255), (130, 205, 255))
#fullProcessAndBanded(PuBlCy, 'PuBlCyE', True)

# Reddish, Orangish, Brown
RdOrBr = ((230, 0, 0), (250, 115, 0), (140, 50, 5))
#fullProcessAndBanded(RdOrBr, 'RdOrBr', True)

# Reddish, Orangish, Brown Extended
RdOrBrE = ((230, 0, 0), (250, 115, 0), (140, 50, 5), (140, 50, 5))
#fullProcessAndBanded(RdOrBr, 'RdOrBrE', True)

# Reddish, Orangish, Brown
RdOrBl = ((230, 0, 0), (250, 115, 0), (5, 5, 230))
#fullProcessAndBanded(RdOrBr, 'RdOrBl', True)

# Slate, Hot Pink, Bluish
SlHpBl = ((35, 75, 100), (240, 15, 220), (5, 5, 230))
#fullProcessAndBanded(SlHpBl, 'SlHpBl', True)

# Pale Green, Charcoal, Pink
PgChPi = ((5, 160, 75), (90, 105, 110), (225, 80, 200))
#fullProcessAndBanded(PgChPi, 'PgChPi', True)

# Orangish, Reddish, Purplish
OrRdPu = ((225, 120, 5), (190, 65, 65), (95, 10, 235))
#fullProcessAndBanded(OrRdPu, 'OrRdPu', True)

# cyclical RGB
CR = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0))
#fullProcessAndBanded(CR, 'CR', True)

# RYGCBMR -- Cyclical Rainbow
R = ((255, 0, 0),       # red
     (255, 255, 0),     # yellow
     (0, 255, 0),       # green
     (0, 255, 255),     # cyan
     (0, 0, 255),       # blue
     (255, 0, 255),     # magenta
     (255, 0, 0),       # red
     )
#fullProcessAndBanded(R, 'R', True)

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
#fullProcessAndBanded(IL, 'IL', True)

PgChPiRdOrBl = list()
PgChPiRdOrBl.extend(PgChPi)
PgChPiRdOrBl.extend(RdOrBl)
#fullProcessAndBanded(PgChPiRdOrBl, 'PgChPiRdOrBl', True)

# Gold, Magenta, Blue
GoMaBl = ((245, 195, 5), (153, 0, 250), (5, 15, 205))
#fullProcessAndBanded(GoMaBl, 'GoMaBl', True)

# Slate, Gray, Light Blue
SlGyLb = ((100, 125, 145), (200, 205, 200), (150, 210, 255))
#fullProcessAndBanded(SlGyLb, 'SlGyLb', True)

# Slate, Gray, Light Blue Extended
SlGyLbE = ((100, 125, 145), (200, 205, 200), (150, 210, 255), (150, 210, 255))
#fullProcessAndBanded(SlGyLbE, 'SlGyLbE', True)

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
#fullProcessAndBanded(BGS, 'BGS', True)

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
#fullProcessAndBanded(BGSR, 'BGSR', True)

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
#fullProcessAndBanded(GSR, 'GSR', True)

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
#fullProcessAndBanded(GSROYG, 'GSROYG', True)

# Yellow, Red, Orange
YRO = ((195, 185, 10),
       (155, 5, 0),
       (255, 170, 45),
       )
#fullProcessAndBanded(YRO, 'YRO', True)

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
#fullProcessAndBanded(CBR, 'CBR', True)

CBrOrYeRd = ((192, 96, 48),
            (192, 96, 0),
            (192, 192, 0),
            (192, 0, 0),
            (192, 96, 48),
            )
#fullProcessAndBanded(CBrOrYeRd, 'CBrOrYeRd', True)

RdBk = ((255, 0, 0),
      (0, 0, 0),
      )
#fullProcessAndBanded(RdBk, 'RdBk', True)

BkRdBkGrBkBlBk = ((0, 0, 0),
                (255, 0, 0),
                (0, 0, 0),
                (0, 255, 0),
                (0, 0, 0),
                (0, 0, 255),
                (0, 0, 0),
                )
#fullProcessAndBanded(BkRdBkGrBkBlBk, 'BkRdBkGrBkBlBk', True)

BkRdBkOrBkYeBk = ((0, 0, 0),
                 (255, 0, 0),
                 (0, 0, 0),
                 (255, 128, 0),
                 (0, 0, 0),
                 (255, 255, 0),
                 (0, 0, 0),
                 )
#fullProcessAndBanded(BkRdBkOrBkYeBk, 'BkRdBkOrBkYeBk', True)

RdBkBl = ((255, 0, 0),
          (0, 0, 0),
          (0, 0, 255),
          )
#fullProcessAndBanded(RdBkBl, 'RdBkBl', True)

RdWh = ((255, 0, 0),
      (255, 255, 255),
      )
#fullProcessAndBanded(RdWh, 'RdWh', True)

RdWhBl = ((255, 0, 0),
          (255, 255, 255),
          (0, 0, 255),
          )
#fullProcessAndBanded(RdWhBl, 'RdWhBl', True)

# Bright Purplish, Bluish, Cyanish
BPuBlCy = ((174, 0, 255), (72, 157, 255), (130, 205, 255))
#fullProcessAndBanded(BPuBlCy, 'BPuBlCy', True)

# Reddish, Greenish, Purplish
BRdGrPu = ((255, 10, 110), (185, 255, 0), (110, 50, 255))
#fullProcessAndBanded(RdGrPu, 'BRdGrPu', True)

# Neon Green, Hot Pink, Purplish
NgHpPu = ((12, 255, 12), (250, 45, 255), (130, 115, 255))
#fullProcessAndBanded(NgHpPu, 'BNgHpPu', True)

DMaMnRdOrYe = ((0, 0, 0),       # black
               (32, 0, 32),     # magenta
               (64, 0, 32),    # maroon
               (96, 0, 0),     # red
               (128, 64, 0),   # orange
               (160, 160, 0),   # yellow
               (192, 192, 192), # white
               )
#fullProcessAndBanded(DMaMnRdOrYe, 'DMaMnRdOrYe', True)

OrWh = ((255, 126, 64), (255, 255, 255))
#fullProcessAndBanded(OrWh, 'OrWh', True)

BkOr = ((0, 0, 0), (255, 126, 64))
#fullProcessAndBanded(BkOr, 'BkOr', True)

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
#fullProcessAndBanded(Crayola8, 'Crayola8', True)

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
#fullProcessAndBanded(Crayola16, 'Crayola16', True)

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
#fullProcessAndBanded(Crayola24,'Crayola24', True)

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
#fullProcessAndBanded(Crayola32, 'Crayola32', True)

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
#fullProcessAndBanded(Crayola48, 'Crayola48', True)

# Crayola Crayon 64-count Box
Crayola64 = ((35, 35, 35),      # Black                       8
             (149, 145, 140),   # Gray                       24
             (205, 197, 194),	# Silver                     64
             (165, 105, 79),    # Sepia                      48
             (180, 103, 77),    # Brown                       8
             (188, 93, 88),     # Chestnut                   32
             (214, 138, 89),    # Raw Sienna                 48
             (234, 126, 93),    # Burnt Sienna               48
             (222, 179, 136),   # Tumbleweed                 48
             (231, 198, 151),	# Gold                       64
             (203, 65, 84),	# Brick Red                  64
             (205, 74, 74),     # Mahogany                   48
             (230, 168, 215),	# Orchid                     64
             (246, 100, 175),	# Magenta                    64
             (253, 124, 110),	# Bittersweet                64
             (252, 137, 172),	# Tickle Me Pink             64
             (250, 167, 108),   # Tan                        32
             (135, 169, 107),	# Asparagus                  64
             (109, 174, 129),	# Forest Green               64
             (186, 184, 108),   # Olive Green                48
             (197, 208, 230),	# Periwinkle                 64
             (236, 234, 190),   # Spring Green               48
             (239, 152, 170),   # Mauvelous                  48
             (255, 67, 164),	# Wild Strawberry            64
             (255, 127, 73),	# Burnt Orange               64
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
             (28, 169, 201),	# Pacific Blue               64
             (31, 206, 203),	# Robin's Egg Blue           64
             (29, 172, 214),    # Cerulean                   24
             (128, 218, 235),   # Sky Blue                   32
             (154, 206, 235),   # Cornflower                 48
             (119, 221, 231),	# Turquoise Blue             64
             (31, 117, 254),    # Blue                        8
             (46, 80, 144),     # Bluetiful                  24
             (93, 118, 203),    # Indigo                     24
             (115, 102, 189),   # Blue Violet                16
             (146, 110, 174),   # Violet (Purple)             8
             (157, 129, 186),   # Purple Mountains' Majesty  48
             (176, 183, 198),   # Cadet Blue                 32
             (205, 164, 222),   # Wisteria                   32
             (142, 69, 133),	# Plum                       64
             (219, 215, 210),   # Timberwolf                 32
             (237, 237, 237),   # White                      16
            )
#fullProcessAndBanded(Crayola64, 'Crayola64', True)

# Crayola Crayon 96-count Box
Crayola96 = ((35, 35, 35),	# Black
             (26, 72, 118),	# Midnight Blue
             (46, 80, 144),	# Bluetiful
             (23, 128, 109),	# Tropical Rain Forest
             (21, 128, 120),	# Pine Green
             (142, 69, 133),	# Plum
             (43, 108, 196),	# Denim
             (238, 32, 77),	# Red
             (25, 116, 210),	# Navy Blue
             (227, 37, 107),	# Razzmatazz
             (120, 81, 169),	# Royal Purple
             (200, 56, 90),	# Maroon
             (242, 40, 71),	# Scarlet
             (202, 55, 103),	# Jazzberry Jam
             (31, 117, 254),	# Blue
             (203, 65, 84),	# Brick Red
             (205, 74, 74),	# Mahogany
             (192, 68, 143),	# Red Violet
             (115, 102, 189),	# Blue Violet
             (255, 29, 206),	# Hot Magenta
             (255, 29, 206),	# Purple Pizza
             (93, 118, 203),	# Indigo
             (165, 105, 79),	# Sepia
             (188, 93, 88),	# Chestnut
             (25, 158, 189),	# Blue Green
             (221, 68, 146),	# Cerise
             (28, 172, 120),	# Green
             (180, 103, 77),	# Brown
             (146, 110, 174),	# Violet (Purple)
             (28, 169, 201),	# Pacific Blue
             (255, 73, 107),	# Radical Red
             (255, 83, 73),	# Red Orange
             (29, 172, 214),	# Cerulean
             (255, 67, 164),	# Wild Strawberry
             (59, 176, 143),	# Jungle Green
             (195, 100, 197),	# Fuchsia
             (247, 83, 148),	# Violet Red
             (255, 72, 208),	# Razzle Dazzle Rose
             (157, 129, 186),	# Purple Mountains' Majesty
             (149, 145, 140),	# Gray
             (255, 110, 74),	# Outrageous Orange
             (109, 174, 129),	# Forest Green
             (255, 117, 56),	# Orange
             (135, 169, 107),	# Asparagus
             (246, 100, 175),	# Magenta
             (31, 206, 203),	# Robin's Egg Blue
             (252, 108, 133),	# Wild Watermelon
             (234, 126, 93),	# Burnt Sienna
             (214, 138, 89),	# Raw Sienna
             (29, 249, 20),	# Electric Lime
             (255, 127, 73),	# Burnt Orange
             (69, 206, 162),	# Shamrock
             (255, 130, 67),	# Mango Tango
             (253, 124, 110),	# Bittersweet
             (221, 148, 117),	# Copper
             (162, 173, 208),	# Wild Blue Yonder
             (252, 137, 172),	# Tickle Me Pink
             (186, 184, 108),	# Olive Green
             (251, 126, 253),	# Shocking Pink
             (255, 163, 67),	# Neon Carrot
             (239, 152, 170),	# Mauvelous
             (222, 170, 136),	# Tumbleweed
             (176, 183, 198),	# Cadet Blue
             (205, 164, 222),	# Wisteria
             (250, 167, 108),	# Tan
             (255, 160, 137),	# Vivid Tangerine
             (255, 164, 116),	# Atomic Tangerine
             (255, 155, 170),	# Salmon
             (119, 221, 231),	# Turquoise Blue
             (230, 168, 215),	# Orchid
             (128, 218, 235),	# Sky Blue
             (255, 182, 83),	# Yellow Orange
             (154, 206, 235),	# Cornflower
             (205, 197, 194),	# Silver
             (255, 170, 204),	# Carnation Pink
             (118, 255, 122),	# Screamin Green
             (159, 226, 191),	# Sea Green
             (168, 228, 160),	# Granny Smith Apple
             (231, 198, 151),	# Gold
             (178, 236, 93),	# Inchworm
             (255, 189, 136),	# Macaroni and Cheese
             (252, 180, 213),	# Lavender
             (255, 207, 72),	# Sunglow
             (253, 188, 180),	# Melon
             (197, 208, 230),	# Periwinkle
             (197, 227, 132),	# Yellow Green
             (219, 215, 210),	# Timberwolf
             (255, 217, 117),	# Goldenrod
             (255, 207, 171),	# Peach
             (253, 217, 181),	# Apricot
             (240, 232, 145),	# Green Yellow
             (252, 232, 131),	# Yellow
             (236, 234, 190),	# Spring Green
             (237, 237, 237),	# White
             (253, 252, 116),	# Laser Lemon
             (253, 252, 116),	# Unmellow Yellow
             )
fullProcessAndBanded(Crayola96, 'Crayola96')

Crayola120 = ((35, 35, 35),	# Black
              (26, 72, 118),	# Midnight Blue
              (65, 74, 76),	# Outer Space
              (46, 80, 144),	# Bluetiful
              (110, 81, 96),	# Eggplant
              (23, 128, 109),	# Tropical Rain Forest
              (21, 128, 120),	# Pine Green
              (116, 66, 200),	# Purple Heart
              (142, 69, 133),	# Plum
              (43, 108, 196),	# Denim
              (238, 32, 77),	# Red
              (25, 116, 210),	# Navy Blue
              (227, 37, 107),	# Razzmatazz
              (120, 81, 169),	# Royal Purple
              (200, 56, 90),	# Maroon
              (242, 40, 71),	# Scarlet
              (202, 55, 103),	# Jazzberry Jam
              (31, 117, 254),	# Blue
              (143, 80, 157),	# Vivid Violet
              (203, 65, 84),	# Brick Red
              (205, 74, 74),	# Mahogany
              (192, 68, 143),	# Red Violet
              (115, 102, 189),	# Blue Violet
              (255, 29, 206),	# Hot Magenta
              (255, 29, 206),	# Purple Pizza
              (93, 118, 203),	# Indigo
              (165, 105, 79),	# Sepia
              (188, 93, 88),	# Chestnut
              (25, 158, 189),	# Blue Green
              (221, 68, 146),	# Cerise
              (138, 121, 93),	# Shadow
              (28, 172, 120),	# Green
              (180, 103, 77),	# Brown
              (146, 110, 174),	# Violet (Purple)
              (28, 169, 201),	# Pacific Blue
              (255, 73, 107),	# Radical Red
              (204, 102, 102),	# Fuzzy Wuzzy
              (255, 83, 73),	# Red Orange
              (29, 172, 214),	# Cerulean
              (255, 67, 164),	# Wild Strawberry
              (222, 93, 131),	# Blush
              (159, 129, 112),	# Beaver
              (59, 176, 143),	# Jungle Green
              (195, 100, 197),	# Fuchsia
              (247, 83, 148),	# Violet Red
              (48, 186, 143),	# Mountain Meadow
              (253, 94, 83),	# Sunset Orange
              (255, 72, 208),	# Razzle Dazzle Rose
              (157, 129, 186),	# Purple Mountains' Majesty 
              (149, 145, 140),	# Gray
              (255, 110, 74),	# Outrageous Orange
              (109, 174, 129),	# Forest Green
              (28, 211, 162),	# Caribbean Green
              (255, 117, 56),	# Orange
              (135, 169, 107),	# Asparagus
              (246, 100, 175),	# Magenta
              (31, 206, 203),	# Robin's Egg Blue
              (252, 108, 133),	# Wild Watermelon
              (234, 126, 93),	# Burnt Sienna
              (151, 154, 170),	# Manatee
              (214, 138, 89),	# Raw Sienna
              (29, 249, 20),	# Electric Lime
              (113, 188, 120),	# Fern
              (255, 127, 73),	# Burnt Orange
              (69, 206, 162),	# Shamrock
              (255, 130, 67),	# Mango Tango
              (253, 124, 110),	# Bittersweet
              (205, 149, 117),	# Antique Brass
              (221, 148, 117),	# Copper
              (247, 128, 161),	# Pink Sherbet
              (252, 116, 253),	# Pink Flamingo
              (162, 173, 208),	# Wild Blue Yonder
              (252, 137, 172),	# Tickle Me Pink
              (186, 184, 108),	# Olive Green
              (251, 126, 253),	# Shocking Pink
              (173, 173, 214),	# Blue Bell
              (255, 163, 67),	# Neon Carrot
              (239, 152, 170),	# Mauvelous
              (222, 170, 136),	# Tumbleweed
              (176, 183, 198),	# Cadet Blue
              (205, 164, 222),	# Wisteria
              (250, 167, 108),	# Tan
              (255, 160, 137),	# Vivid Tangerine
              (255, 164, 116),	# Atomic Tangerine
              (255, 155, 170),	# Salmon
              (120, 219, 226),	# Aquamarine
              (119, 221, 231),	# Turquoise Blue
              (230, 168, 215),	# Orchid
              (128, 218, 235),	# Sky Blue
              (255, 182, 83),	# Yellow Orange
              (154, 206, 235),	# Cornflower
              (205, 197, 194),	# Silver
              (255, 170, 204),	# Carnation Pink
              (118, 255, 122),	# Screamin Green
              (159, 226, 191),	# Sea Green
              (168, 228, 160),	# Granny Smith Apple
              (231, 198, 151),	# Gold
              (178, 236, 93),	# Inchworm
              (255, 189, 136),	# Macaroni and Cheese
              (252, 180, 213),	# Lavender
              (255, 207, 72),	# Sunglow
              (253, 188, 180),	# Melon
              (197, 208, 230),	# Periwinkle
              (197, 227, 132),	# Yellow Green
              (255, 188, 217),	# Cotton Candy
              (239, 205, 184),	# Desert Sand
              (219, 215, 210),	# Timberwolf
              (255, 217, 117),	# Goldenrod
              (255, 207, 171),	# Peach
              (239, 219, 197),	# Almond
              (253, 217, 181),	# Apricot
              (240, 232, 145),	# Green Yellow
              (252, 232, 131),	# Yellow
              (253, 215, 228),	# Piggy Pink
              (236, 234, 190),	# Spring Green
              (250, 231, 181),	# Banana Mania
              (237, 237, 237),	# White
              (253, 252, 116),	# Laser Lemon
              (253, 252, 116),	# Unmellow Yellow
              (255, 255, 159),	# Canary
              )
fullProcessAndBanded(Crayola120, 'Crayola120')

# Create colorbars and linear maps from all of the builtin cmaps
# It's a lot of them, so don't do the below unless you really want to see _all_ of them.
# Uncomment the 7 lines below to see all built-in colormaps as colorbars and linear maps
#import matplotlib as mpl
#
#cmap_names = getattr(mpl, 'colormaps')
#
#for cmap_name in sorted(cmap_names):
#    print(cmap_name)
#    cmapProcess(cmap_name)
