import colorsys, os, sys
from PIL import Image, ImageDraw
from optparse import OptionParser

'''
    skin colors in RGB format
'''
skin_colors = [
    (207,126,97), (209,136,95), (186,122,97), (188,124,96),
    (223,168,161), (184,147,128), (170,117,77), (199,142,99),
    (205,123,83), (219,169,160), (175,120,79), (190,97,82),
    (193,94,71), (218,147,115), (197,110,90), (202,136,120),
    (155,83,61), (226,127,88), (238,128,101), (172,96,72),
    (207,173,146), (189,140,126), (210,146,134), (237,189,169),
    (146,71,52), (175,125,136), (203,126,84), (226,180,164),
    (143,61,21), (194,133,112), (193,129,85), (222,187,167),
    (251,180,138), (200,139,118), (229,182,138)
]

'''
    HSV thresholds
'''
threshold_h_min = 0.04
threshold_h_max = 0.04
threshold_s_min = 0.09
threshold_s_max = 0.09


'''
    detection mode
'''
MODE_SKIN_COLORS = 1
MODE_HSV_RANGE = 2

detection_mode = MODE_HSV_RANGE

'''
    resize size
'''
resize_w = 250
resize_h = 250

'''
    return of skin pixels
'''
_skin_pixels = []
return_skin_pixels = False


'''
    save copy to folder
'''
output_dir = None


'''
    private
'''
_skin_colors_hsv = []


'''
    detect function
'''
def detect(image):

    if isinstance(image, str):
        im = Image.open(image)
        file_name = os.path.basename(image)
    else:
        im = image
        file_name = "image.jpg" # @todo: timestamp as name 


    # convert rgb colors to hsv
    if not _skin_colors_hsv and detection_mode == MODE_SKIN_COLORS:
        for r, g, b in skin_colors:
            _skin_colors_hsv.append(colorsys.rgb_to_hsv(float(r), float(g), float(b)))
    

    # resize image to thumbnail size
    if im.size[0] > im.size[1]:
        im.thumbnail((resize_w, resize_h * (im.size[0] / im.size[1])))
    else:
        im.thumbnail((resize_w * (im.size[1] / im.size[0]), resize_h))
    
    
    # save copy of original thumbnail
    if output_dir:
        file_name, file_ext = os.path.splitext(file_name)
        im.save(output_dir + os.sep + file_name + "_orig.jpg")
        
    
    pixels_overall = im.size[0] * im.size[1]
    pixels_skin = 0
    
    # go trough each pixel of the image
    for x in range(0, im.size[0]):
        for y in range(0, im.size[1]):
            
            # get color of pixel in rgb
            rgb = im.getpixel((x, y))
            
            # when no tuple is returned, make a tuple
            if type(rgb) == type(1):
                rgb = (rgb, rgb, rgb)
                
            pixels_overall += 1
                
            # is skin
            if _is_skin(rgb):
                pixels_skin += 1
                
                # paint skin regions
                if output_dir:
                    im.putpixel((x, y), (255, 0, 0))
                
                # append into skin pixel list
                if return_skin_pixels:
                    _skin_pixels.append((x, y))
    
    
    ret = { 'skin_ratio': pixels_skin / float(pixels_overall) * 100 }
    
    if return_skin_pixels:
        ret['pixels_skin_list'] = _skin_pixels
        
        
    # print skin ratio on image and
    # save image
    if output_dir:
        imd = ImageDraw.Draw(im)
        text = "skin_ratio: {0:.2f} %".format(ret['skin_ratio'])
        imd.text((11, 11), text, fill="white")
        imd.text((10, 10), text, fill="black")

        im.save(output_dir + os.sep + file_name + "_result.jpg")

    return ret
                

'''
    is skin function
'''
def _is_skin((r, g, b)):
    
    # transform rgb to hsv
    h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
    
    # skin detection based on rgb skin colors.
    # each color in the list is matched against
    # the given rgb-value + min/max threshold for H and S
    if detection_mode == MODE_SKIN_COLORS:
        for ch, cs, cv  in _skin_colors_hsv:
            
            # range for hue
            range_h_min = 0 if ch - threshold_h_min < 0 else ch - threshold_h_min
            range_h_max = 1 if ch + threshold_h_max > 1 else ch + threshold_h_max

            # range for saturation
            range_s_min = 0 if cs - threshold_s_min < 0 else cs - threshold_s_min
            range_s_max = 1 if cs + threshold_s_max > 1 else cs + threshold_s_max

            # test color
            if h >= range_h_min and h <= range_h_max and s >= range_s_min and s <= range_s_max:
                return True
            
    # skin detection based on HSV (HS) range.
    elif detection_mode == MODE_HSV_RANGE:

        if h < (1/float(360))*50 and s > 0.23 and s < 0.68:
            return True

    
    return False
     

if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options] arg1 arg2")
    parser.add_option("-f", "--file", dest="file", help="read image from file", metavar="FILE")
    #parser.add_option("-d", "--dir", dest="file", help="read images from dir", metavar="FILE")
    parser.add_option("-o", "--output_dir", dest="output_dir", help="save processed image", metavar="DIR")
    
    (options, args) = parser.parse_args()
        
    if options.output_dir:
        output_dir = options.output_dir

    if options.file:
        ret = detect(options.file)
        print "file: {0}".format(options.file)
        print "skin_ratio: {0:.2f} %".format(ret["skin_ratio"])
        
