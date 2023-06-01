#
# gradpal.py
#
# Output to standard out a custome JSON palette.
#
# The first 36 colors are 12 triplets (half, three-quarters, full) 
# of the full spectrum (red, orange, yellow, chartreuse, green, turquoise,
# cyan, aqua, blue, purple, magenta, maroon.) The remaining 220 colors are a
# grayscale starting at (36, 36, 36) and ending at (255, 255, 255).
#
# 20230527  @TheQuantumMagician Created.
#

def print_triplet(bases, incs):
    # Print three different colors, starting at bases and increasing by incs
    r = bases[0]
    g = bases[1]
    b = bases[2]
    for i in range(3):
        print("    [")
        print("        " + str(r) + ",")
        print("        " + str(g) + ",")
        print("        " + str(b))
        print("    ],")
        r += incs[0]
        g += incs[1]
        b += incs[2]


print("[")
print_triplet((128, 0, 0), (64, 0, 0))      # reds
print_triplet((128, 64, 0), (64, 32, 0))    # oranges
print_triplet((128, 128, 0), (64, 64, 0))   # yellows
print_triplet((64, 128, 0), (32, 64, 0))    # chartreuses
print_triplet((0, 128, 0), (0, 64, 0))      # greens
print_triplet((0, 128, 64), (0, 64, 32))    # green-cyans
print_triplet((0, 128, 128), (0, 64, 64))   # cyans
print_triplet((0, 64, 128), (0, 32, 64))    # aquas
print_triplet((0, 0, 128), (0, 0, 64))      # blues
print_triplet((64, 0, 128), (32, 0, 64))    # purples
print_triplet((128, 0, 128), (64, 0, 64))   # magentas
print_triplet((128, 0, 64), (64, 0, 32))    # maroons

# grayscales
for i in range(36, 256):
        print("    [")
        print("        " + str(i) + ",")
        print("        " + str(i) + ",")
        print("        " + str(i))
        print("    ],")

print("]")
