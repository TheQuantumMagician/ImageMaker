#
# Apply a watermark image file to the lower right corner of an image file.
#
# 20230508 smb  @TheQuantumMagician - Created
#


import argparse

from pathlib import Path
from PIL import Image

# Instantiate the command line parser
parser = argparse.ArgumentParser(description="edges: edge-enhancement and posterization application")

# Optional argument for filename (defaults to 'test.jpg')
parser.add_argument('--fn',
                    action="store",
                    dest="fn",
                    help="filename of image to be watermarked",
                    default="test.jpg"
                    )

# Optional argument for watermark filename (defaults to 'watermark.png')
parser.add_argument('--wm',
                    action="store",
                    dest="wm",
                    help="filename of watermark image",
                    default="watermark.png"
                    )

args = parser.parse_args()

print("fn\t", args.fn)
print("wm\t", args.wm)

fnPath = Path(args.fn)
if fnPath.exists():
    wmPath = Path(args.wm)
    if wmPath.exists():
        im = Image.open(args.fn)
        wm = Image.open(args.wm)
        loc = ((im.size[0] - wm.size[0]), (im.size[1] - wm.size[1]))

        im.paste(wm, loc, wm)
        wm.close()
        
        newName = fnPath.with_name("wm_" + fnPath.name)

        im.save(newName)
        im.close()
        print(f"Watermarked and saved to %s" % newName)
    else:
        print(f"The watermark file (%s) does not exist." % args.wm)
else:
    print(f"The image file (%s) does not exist." % args.rn)
