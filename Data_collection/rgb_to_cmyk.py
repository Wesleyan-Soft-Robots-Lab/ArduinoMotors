# source: https://stackoverflow.com/questions/14088375/how-can-i-convert-rgb-to-cmyk-and-vice-versa-in-python

RGB_SCALE = 255
CMYK_SCALE = 100

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        # black
        return 0, 0, 0, CMYK_SCALE

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / RGB_SCALE
    m = 1 - g / RGB_SCALE
    y = 1 - b / RGB_SCALE

    # extract out k [0, 1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0, CMYK_SCALE]
    return c * CMYK_SCALE, m * CMYK_SCALE, y * CMYK_SCALE, k * CMYK_SCALE

# tested with comparison to https://www.rapidtables.com/convert/color/cmyk-to-rgb.html
# verified works as advertised
print("rbg = 255, 0, 0")
print("cmyk = ", rgb_to_cmyk(255, 0, 0))
print("")
print("rbg = 0, 255, 0")
print("cmyk = ", rgb_to_cmyk(0, 255, 0))
print("rbg = 0, 0, 255")
print("cmyk = ", rgb_to_cmyk(0, 0, 255))
print("rbg = 170, 50, 50")
print("cmyk = ", rgb_to_cmyk(170, 100, 100))