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
from PIL import ImageColor

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


def get_lum(pixel):
    # Calculate luminosity of an (r, g, b) pixel
    # gray level = 0.3r + 0.59g + 0.11b

    lum = int((0.3 * pixel[0]) + (0.59 * pixel[1]) + (0.11 * pixel[2]))

    return(lum)


def colorbar(colors):
    # Create a colorbar image from a palette
    cbIm = Image.new('RGB', (5 * 256, 64))
    cbPixels = cbIm.load()

    for y in range(64):
        for x in range(256 * 5):
            cbPixels[x, y] = colors[int(x / 5)]

    cbIm.show()


def brightnessColorbar(colors):
    # Create a colorbar image from a palette based on luminosity
    cbIm = Image.new('RGB', (5 * 256, 64))
    cbPixels = cbIm.load()

    for y in range(64):
        for x in range(256 * 5):
            lum = get_lum(colors[int(x / 5)])
            cbPixels[x, y] = (lum, lum, lum)

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


# Write the provided palette out as JSON data
def writeColors(colors, name):
    cpFP = open(name + '.json', 'wt')
    json.dump(colors, cpFP, indent=4)
    cpFP.close()
    print('Custom palette', name + '.json', 'written to disk.')


# Sort a palette based on the grayscale value brightness of the colors
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
    print("fullProcess")
    Dict = createCDict(colors)
    cmNew = custCM(Dict, name)
    Colors = palette(cmNew)
    writeColors(Colors, name)
    colorbar(Colors)
    brightnessColorbar(Colors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)


def cmapProcess(name):
    print("cmapProcess")
    cmNew = plt.colormaps[name]
    colors = palette(cmNew)
    writeColors(colors, name)
    colorbar(colors)
    brightnessColorbar(colors)
    anticolors = [(255 - r, 255 - g, 255 - b) for r, g, b in colors]
    colorbar(anticolors)
    colors.reverse()
    colorbar(colors)
    anticolors.reverse()
    colorbar(anticolors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)


def customCmapProcess(name, cmNew):
    print("customCmapProcess")
    colors = palette(cmNew)
    colorbar(colors)
    brightnessColorbar(colors)
#    plot_linearmap(cmNew)
    plot_linearmap_offline(cmNew)
    writeColors(colors, name)


def _fPAB(palette, name):
    print("_fPAB")
    # create both fade and banded transition palettes, display colorbar and linearmap
    cmName = 'cm' + name
    fullProcess(palette, name)
    newCm = customBCM(cmName, palette)
    customCmapProcess(cmName, newCm)
    

def fullProcessAndBanded(palette, name, bsort=False):
    print("fullProcessAndBanded")
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

# KRYGCBMWMBCGYRK rainbow
BWIL = ((0, 0, 0),        # black
      (255, 0, 0),      # red
      (255, 255, 0),    # yellow
      (0, 255, 0),      # green
      (0, 255, 255),    # cyan
      (0, 0, 255),      # blue
      (255, 0, 255),    # magenta
      (255, 255, 255),  # white
      (255, 0, 255),    # magenta
      (0, 0, 255),      # blue
      (0, 255, 255),    # cyan
      (0, 255, 0),      # green
      (255, 255, 0),    # yellow
      (255, 0, 0),      # red
      (0, 0, 0),        # black
      )
#fullProcessAndBanded(BWIL, 'BWIL', True)

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
               (64, 0, 32),     # maroon
               (96, 0, 0),      # red
               (128, 64, 0),    # orange
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

# Crayola Crayon 8-count Box
SCrayola8 = ((35, 35, 35),       # Black
             (238, 32, 77),      # Red
             (255, 117, 56),     # Orange
             (252, 232, 131),    # Yellow
             (28, 172, 120),     # Green
             (31, 117, 254),     # Blue
             (146, 110, 174),    # Violet (Purple)
             (180, 103, 77),     # Brown
             )
#fullProcessAndBanded(SCrayola8, 'SCrayola8', True)

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
#fullProcessAndBanded(Crayola96, 'Crayola96')

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
#fullProcessAndBanded(Crayola120, 'Crayola120')

YeGr = ((255, 255, 0), (0, 255, 0))
#fullProcessAndBanded(YeGr, 'YeGr')

YeCy = ((255, 255, 0), (0, 255, 255))
#fullProcessAndBanded(YeCy, 'YeCy')

RGBR = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0))
#fullProcessAndBanded(RGBR, 'RGBR')

SepiaW = ((112, 66, 20), (255, 255, 255))
#fullProcessAndBanded(SepiaW, 'SepiaW')

Sepia = ((112, 66, 20), (255, 150, 46))
#fullProcessAndBanded(Sepia, 'Sepia')

VIBGYOR = ((138,  43, 226),
           ( 75,   0, 130),
           (  0,   0, 255),
           (  0, 255,   0),
           (255, 255,   0),
           (255, 128,   0),
           (255,   0,   0),
          )
#fullProcessAndBanded(VIBGYOR, 'VIBGYOR', True)

BkVIBGYORW = ((0, 0, 0),
           (138,  43, 226),
           ( 75,   0, 130),
           (  0,   0, 255),
           (  0, 255,   0),
           (255, 255,   0),
           (255, 128,   0),
           (255,   0,   0),
           (255, 255, 255),
          )
#fullProcessAndBanded(BkVIBGYORW, 'BkVIBGYORW', True)

# Dark Brown to Bright Sepia
DBS = ((55, 33, 17),
       (255, 150, 46)
      )
#fullProcessAndBanded(DBS, 'DBS', True)

BSW = ((0, 0, 0),
       (112, 66, 20),
       (255, 255, 255),
      )
#fullProcessAndBanded(BSW, 'BSW', True)

SortedC120 = (
	(35, 35, 35),
	(237, 237, 237),
	(204, 102, 102),
	(205, 74, 74),
	(188, 93, 88),
	(255, 83, 73),
	(253, 94, 83),
	(253, 124, 110),
	(253, 188, 180),
	(255, 160, 137),
	(255, 110, 74),
	(234, 126, 93),
	(180, 103, 77),
	(205, 197, 194),
	(255, 127, 73),
	(221, 148, 117),
	(165, 105, 79),
	(255, 117, 56),
	(255, 130, 67),
	(255, 164, 116),
	(159, 129, 112),
	(205, 149, 117),
	(239, 205, 184),
	(214, 138, 89),
	(222, 170, 136),
	(250, 167, 108),
	(255, 207, 171),
	(255, 189, 136),
	(253, 217, 181),
	(255, 163, 67),
	(239, 219, 197),
	(149, 145, 140),
	(219, 215, 210),
	(255, 182, 83),
	(231, 198, 151),
	(138, 121, 93),
	(255, 217, 117),
	(250, 231, 181),
	(255, 207, 72),
	(252, 232, 131),
	(240, 232, 145),
	(236, 234, 190),
	(186, 184, 108),
	(253, 252, 116),
	(253, 252, 116),
	(255, 255, 159),
	(197, 227, 132),
	(178, 236, 93),
	(135, 169, 107),
	(168, 228, 160),
	(29, 249, 20),
	(118, 255, 122),
	(113, 188, 120),
	(109, 174, 129),
	(159, 226, 191),
	(28, 172, 120),
	(69, 206, 162),
	(48, 186, 143),
	(59, 176, 143),
	(28, 211, 162),
	(23, 128, 109),
	(21, 128, 120),
	(31, 206, 203),
	(120, 219, 226),
	(119, 221, 231),
	(128, 218, 235),
	(65, 74, 76),
	(28, 169, 201),
	(25, 158, 189),
	(29, 172, 214),
	(154, 206, 235),
	(26, 72, 118),
	(25, 116, 210),
	(43, 108, 196),
	(31, 117, 254),
	(46, 80, 144),
	(197, 208, 230),
	(176, 183, 198),
	(162, 173, 208),
	(93, 118, 203),
	(151, 154, 170),
	(173, 173, 214),
	(115, 102, 189),
	(116, 66, 200),
	(120, 81, 169),
	(157, 129, 186),
	(146, 110, 174),
	(205, 164, 222),
	(143, 80, 157),
	(195, 100, 197),
	(251, 126, 253),
	(252, 116, 253),
	(142, 69, 133),
	(255, 0, 204),
	(230, 168, 215),
	(255, 72, 208),
	(255, 0, 187),
	(192, 68, 143),
	(110, 81, 96),
	(255, 67, 164),
	(246, 100, 175),
	(221, 68, 146),
	(252, 180, 213),
	(255, 188, 217),
	(255, 170, 204),
	(247, 83, 148),
	(227, 37, 107),
	(253, 215, 228),
	(202, 55, 103),
	(252, 137, 172),
	(222, 93, 131),
	(247, 128, 161),
	(200, 56, 90),
	(238, 32, 77),
	(239, 152, 170),
	(255, 73, 107),
	(252, 108, 133),
	(242, 40, 71),
	(255, 155, 170),
	(203, 65, 84),
)
#fullProcessAndBanded(SortedC120, 'SortedC120', True)

SortedC32 = (
	(35, 35, 35),
	(237, 237, 237),
	(188, 93, 88),
	(255, 83, 73),
	(253, 188, 180),
	(180, 103, 77),
	(255, 117, 56),
	(250, 167, 108),
	(255, 207, 171),
	(253, 217, 181),
	(149, 145, 140),
	(219, 215, 210),
	(255, 182, 83),
	(252, 232, 131),
	(240, 232, 145),
	(197, 227, 132),
	(28, 172, 120),
	(128, 218, 235),
	(25, 158, 189),
	(29, 172, 214),
	(31, 117, 254),
	(46, 80, 144),
	(176, 183, 198),
	(93, 118, 203),
	(115, 102, 189),
	(146, 110, 174),
	(205, 164, 222),
	(247, 83, 248),
	(192, 68, 143),
	(255, 170, 204),
	(247, 83, 148),
	(238, 32, 77),
)
#fullProcessAndBanded(SortedC32, 'SortedC32', True)

DblCy = (
    (0, 0, 64),     # Dark Blue
    (0, 255, 255),  # Cyan
)
#fullProcessAndBanded(DblCy, 'DblCy', True)

PPiW = (
    (175,  14, 248),  # Purple
    (242, 131, 252),  # Pink
    (255, 255, 255),  # White
)
#fullProcessAndBanded(PPiW, 'PPiW', True)

# Based on the "tab20" cmap.
T20 = (
    ( 31, 119, 180),
    (174, 199, 232),
    (255, 127,  14),
    (255, 187, 120),
    ( 44, 160,  44),
    (152, 223, 138),
    (214,  39,  40),
    (255, 152, 150),
    (148, 103, 189),
    (197, 176, 213),
    (140,  86,  75),
    (196, 156, 148),
    (227, 119, 194),
    (247, 182, 210),
    (127, 127, 127),
    (199, 199, 199),
    (188, 189,  34),
    (219, 219, 141),
    ( 23, 190, 207),
    (158, 218, 229),
)
#fullProcessAndBanded(T20, 'T20', True)

T20B = (   
    ( 57,  59, 121),
    ( 82,  84, 163),
    (107, 110, 207),
    (156, 158, 222),
    ( 99, 121,  57),
    (140, 162,  82),
    (181, 207, 107),
    (206, 219, 156),
    (140, 109,  49),
    (189, 158,  57),
    (231, 186,  82),
    (231, 203, 148),
    (132,  60,  57),
    (173,  73,  74),
    (214,  97, 107),
    (231, 150, 156),
    (123,  65, 115),
    (165,  81, 148),
    (206, 109, 189),
    (222, 158, 214),
)
#fullProcessAndBanded(T20B, 'T20B', True)

T20C = (( 49, 130, 189),
 (107, 174, 214),
 (158, 202, 225),
 (198, 219, 239),
 (230,  85,  13),
 (253, 141,  60),
 (253, 174, 107),
 (253, 208, 162),
 ( 49, 163,  84),
 (199, 233, 192),
 (117, 107, 177),
 (158, 154, 200),
 (188, 189, 220),
 (218, 218, 235),
 ( 99,  99,  99),
 (150, 150, 150),
 (189, 189, 189),
 (217, 217, 217),
)
#fullProcessAndBanded(T20C, 'T20C', True)


YlChOr = ((255, 255, 0),
          (24, 32, 32),
          (255, 128, 0)
)
#fullProcessAndBanded(YlChOr, 'YlChOr', True)


PureC8 = ((  0,   0,   0),      # Pure Black
          ( 35,  35,  35),      # Black
          (152,  80,   0),      # Pure Brown
          (180, 103,  77),      # Brown
          (255,   0,   0),      # Pure Red
          (238,  32,  77),      # Red
          (255, 128,   0),      # Pure Orange
          (255, 117,  56),      # Orange
          (255, 255,   0),      # Pure Yellow
          (252, 232, 131),      # Yellow
          (  0, 255,   0),      # Pure Green
          ( 28, 172, 120),      # Green
          (  0,   0, 255),      # Pure Blue
          ( 31, 117, 254),      # Blue
          (210,   0, 255),      # Pure Violet
          (146, 110, 174),      # Violet (Purple)
)
#fullProcessAndBanded(PureC8, "PureC8", True)

# interleaved rainbow and reverse rainbow
ILRR = ((255, 0, 0),      # red
        (255, 0, 255),    # magenta
        (255, 255, 0),    # yellow
        (0, 0, 255),      # blue
        (0, 255, 0),      # green
        (0, 255, 255),    # cyan
        (0, 255, 255),    # cyan
        (0, 255, 0),      # green
        (0, 0, 255),      # blue
        (255, 255, 0),    # yellow
        (255, 0, 255),    # magenta
        (255, 0, 0),      # red
      )
#fullProxcessAndBanded(ILRR, 'ILRR', True)

BlOr = ((0, 0, 255), (255, 192, 0))
#fullProcessAndBanded(BlOr, 'BlOr', True)

GrMa = ((0, 255, 0), (255, 0, 192))
#fullProcessAndBanded(GrMa, 'GrMa', True)

RdCy = ((255, 0, 0), (0, 192, 255))
#fullProcessAndBanded(RdCy, 'RdCy', True)

YlCy = ((255, 255, 0), (0, 192, 255))
#fullProcessAndBanded(YlCy, 'YlCy', True)

Comps = ((0, 0, 255),
         (255, 0, 0),
         (0, 255, 0),
         (0, 192, 255),
         (255, 0, 192),
         (255, 192, 0),
        )
#fullProcessAndBanded(Comps, 'Comps', True)

# Copper and Teal
CT = ((0, 128, 128),
      (185, 115, 50),
     )
#fullProcessAndBanded(CT, 'CT', True)

# Bright Copper and Teal
BCT = ((0, 255, 255),
      (255, 160, 70),
     )
#fullProcessAndBanded(BCT, 'BCT', True)

#Red to Yellow through Orange
RY = ((255, 0, 0),
      (255, 128, 0),
      (255, 255, 0),
     )
#fullProcessAndBanded(RY, 'RY', True)

# Bright Rainbow
BR = ((255, 0, 0),      # Red
      (255, 128, 0),    # Orange
      (255, 255, 0),    # Yellow
      (128, 255, 0),    # Chartreuse
      (0, 255, 0),      # Green
      (0, 255, 128),    # Aquamarine
      (0, 255, 255),    # Cyan
      (0, 128, 255),    # Cornflower
      (0, 0, 255),      # Blue
      (128, 0, 255),    # Purple
      (255, 0, 255),    # Magenta
      (255, 0, 128),    # Rose
      (255, 0, 0),      # Red
    )
#fullProcessAndBanded(BR, 'BR', True)


# Charcoal/Red/Orange/Yellow
ChRdOrYl = ((24, 32, 32),
            (255, 0, 0),
            (255, 128, 0),
            (255, 255, 0),
)
#fullProcessAndBanded(ChRdOrYl, 'ChRdOrYl', True)


# Charcoal-interleaved Bright Rainbow
ChBR = ((24, 32, 32),   # Charcoal
        (255, 0, 0),      # Red
        (24, 32, 32),   # Charcoal
        (255, 128, 0),    # Orange
        (24, 32, 32),   # Charcoal
        (255, 255, 0),    # Yellow
        (24, 32, 32),   # Charcoal
        (128, 255, 0),    # Chartreuse
        (24, 32, 32),   # Charcoal
        (0, 255, 0),      # Green
        (24, 32, 32),   # Charcoal
        (0, 255, 128),    # Aquamarine
        (24, 32, 32),   # Charcoal
        (0, 255, 255),    # Cyan
        (24, 32, 32),   # Charcoal
        (0, 128, 255),    # Cornflower
        (24, 32, 32),   # Charcoal
        (0, 0, 255),      # Blue
        (24, 32, 32),   # Charcoal
        (128, 0, 255),    # Purple
        (24, 32, 32),   # Charcoal
        (255, 0, 255),    # Magenta
        (24, 32, 32),   # Charcoal
        (255, 0, 128),    # Rose
        (24, 32, 32),   # Charcoal
        (255, 0, 0),      # Red
        (24, 32, 32),   # Charcoal
       )
#fullProcessAndBanded(ChBR, 'ChBR', True)


# Charcoal-interleaved Bright Rainbow
partialChBR = ((24, 32, 32),   # Charcoal
        (255, 0, 0),      # Red
        (255, 128, 0),    # Orange
        (255, 255, 0),    # Yellow
        (128, 255, 0),    # Chartreuse
        (24, 32, 32),   # Charcoal
        (0, 255, 0),      # Green
        (0, 255, 128),    # Aquamarine
        (0, 255, 255),    # Cyan
        (0, 128, 255),    # Cornflower
        (24, 32, 32),   # Charcoal
        (0, 0, 255),      # Blue
        (128, 0, 255),    # Purple
        (255, 0, 255),    # Magenta
        (255, 0, 128),    # Rose
        (24, 32, 32),   # Charcoal
        (255, 0, 0),      # Red
       )
#fullProcessAndBanded(partialChBR, 'partialChBR', True)

# Cyan -> White
iced = ((0, 128, 255),
        (128, 192, 255),
        (255, 255, 255),
       )
#fullProcessAndBanded(iced, 'iced', True)

# dark green -> orange
pumpkin = ((0, 32, 0),
           (0, 64, 0),
           (0, 96, 0),
           (0, 128, 0),
           (0, 160, 0),
           (255, 96, 0),
           (255, 128, 0),
           (255, 160, 0),
           (255, 192, 0),
          )
#fullProcessAndBanded(pumpkin, 'pumpkin', False)

BlW = ((0, 0, 255),
      (255, 255, 255),
     )
#fullProcessAndBanded(BlW, "BlW", True)

FallingApart = (ImageColor.getcolor("#E43D96", "RGB"),
                ImageColor.getcolor("#C22658", "RGB"),
                ImageColor.getcolor("#AA1E21", "RGB"),
                ImageColor.getcolor("#471002", "RGB"),
                ImageColor.getcolor("#A24300", "RGB"),
                ImageColor.getcolor("#A67200", "RGB"),
                ImageColor.getcolor("#A59A00", "RGB"),
               )
#fullProcessAndBanded(FallingApart, "FallingApart", True)

AVaseOfVengeance = (ImageColor.getcolor("#15417E", "RGB"),
                    ImageColor.getcolor("#1494C3", "RGB"),
                    ImageColor.getcolor("#9BBA45", "RGB"),
                    ImageColor.getcolor("#FADD41", "RGB"),
                    ImageColor.getcolor("#FE8E2A", "RGB"),
                    ImageColor.getcolor("#DC483A", "RGB"),
                    )
#fullProcessAndBanded(AVaseOfVengeance, "AVaseOfVengeance", True)

Pretend = (ImageColor.getcolor("#F087AA", "RGB"),
           ImageColor.getcolor("#D769AF", "RGB"),
           ImageColor.getcolor("#A51EA5", "RGB"),
           ImageColor.getcolor("#7319AF", "RGB"),
           ImageColor.getcolor("#412396", "RGB"),
           ImageColor.getcolor("#2D1464", "RGB"),
          )
#fullProcessAndBanded(Pretend, "Pretend", True)

FireweedDragon = (ImageColor.getcolor("#2B0A03", "RGB"),
                  ImageColor.getcolor("#630C14", "RGB"),
                  ImageColor.getcolor("#9B0F4C", "RGB"),
                  ImageColor.getcolor("#C42391", "RGB"),
                  ImageColor.getcolor("#EB76D8", "RGB"),
                 )
fullProcessAndBanded(FireweedDragon, "FireweedDragon", True)



#cmapProcess("gnuplot")
#cmapProcess("gist_rainbow")
#cmapProcess("tab20")
#cmapProcess("tab20b")
#cmapProcess("tab20c")
#cmapProcess("autumn")

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
