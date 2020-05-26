import os
import argparse
from PIL import Image
import numpy as np

class RawFormat(object):

    """ Raw file format
    Holds raw file dimensions, bit depth etc.
    """
    def __init__(self, w, h, bpp, encoding, bayerorder):

        self._width = w
        self._height = h
        self._bayerorder = bayerorder
        self._encoding = encoding
        self._bpp = self.GetBpp(bpp, encoding)
        self._stride = self.GetStride(w, encoding)

        self.CheckFormat()

        return

    def GetBpp(self, bpp, encoding):

        if bpp > 0:
            return bpp
        elif encoding.lower().find("raw8") > -1:
            return 8
        elif encoding.lower().find("raw10") > -1:
            return 10
        elif encoding.lower().find("raw12") > -1:
            return 12
        elif encoding.lower().find("raw14") > -1:
            return 14
        elif encoding.lower().find("raw16") > -1:
            return 16

        # default
        return 16

    def CheckFormat(self):
        #print("Encoding, bayer order, w, h, bpp, stride: ", self._encoding, self._bayerorder, self._width, self._height, self._bpp, self._stride)
        pass

    def GetStride(self, w, encoding):
        if encoding.lower().find("raw8") > -1:
            return int(w)
        if encoding.lower().find("raw10") > -1:
            return int(w*10/8)
        if encoding.lower().find("raw12") > -1:
            return int(w*12/8)
        if encoding.lower().find("raw16") > -1:
            return int(w*2)

class RawDecode(object):
    """ Raw Decode
    Raw decoder
    """
    def __init__(self):
        # decoded byte array in 16bpp format
        self.decoded_raw16 = None

        # 16bpp PIL image created from 16bpp array buffer
        self.image16bpp = None

        # Bayer channels separately
        self.raw_16bpp_r = None
        self.raw_16bpp_gr = None
        self.raw_16bpp_gb = None
        self.raw_16bpp_b = None

        self.raw_types = ["raw8", "raw10", "raw12", "raw16"]
       
        return

    def SupportedRawTypes(self, ext):
        for supported_type in self.raw_types:
            if ext.lower().find(supported_type) > -1:
                return True

        return False


    def Decode(self, im_byte_arr, rawformat):

        if rawformat._encoding.lower().find('raw8') > -1:
            self.decoded_raw16 = self.DecodeRaw8(im_byte_arr, rawformat)

        elif rawformat._encoding.lower().find('raw10') > -1:
            self.decoded_raw16 = self.DecodeRaw10(im_byte_arr, rawformat)
        
        elif rawformat._encoding.lower().find('raw12') > -1:
            self.decoded_raw16 = self.DecodeRaw16(im_byte_arr, rawformat)

        elif rawformat._encoding.lower().find('raw16') > -1:
            self.decoded_raw16 = self.DecodeRaw16(im_byte_arr, rawformat)

        return self.decoded_raw16


    def DecodeRaw8(self, im_byte_arr, rawformat):
        stride = rawformat._stride
        width = rawformat._width
        height = rawformat._height
        print("DecodeRaw8(w:{},h:{},s:{})".format(width, height, stride))

        im_gray = np.zeros((height, width), 'uint16')        

        for y in range(height):
            # Raw10: 1 byte -> 1 pixel
            for x in range(0, width, 1):
                offset = int(stride * y + x)

                # decode to 16 bit
                im_gray[y, x] = ( im_byte_arr[offset]<<8 )

        # Create PIL image
        return im_gray  


    def DecodeRaw10(self, im_byte_arr, rawformat):
        stride = rawformat._stride
        width = rawformat._width
        height = rawformat._height
        print("DecodeRaw10(w:{},h:{},s:{})".format(width, height, stride))

        im_gray = np.zeros((height, width), 'uint16')

        for y in range(height):
            # Raw10: 5 bytes -> 4 pixels
            for x in range(0, width, 4):
                offset = int(stride * y + x*10/8)

                lsbs = int(im_byte_arr[offset+4])
                lsb1 = (lsbs>>6)&3
                lsb2 = (lsbs>>4)&3
                lsb3 = (lsbs>>2)&3
                lsb4 = lsbs&3

                # decode to 10 bit
                p1 = ( im_byte_arr[offset]  <<2 ) | lsb1
                p2 = ( im_byte_arr[offset+1]<<2 ) | lsb2
                p3 = ( im_byte_arr[offset+2]<<2 ) | lsb3
                p4 = ( im_byte_arr[offset+3]<<2 ) | lsb4

                # shift to 16bit
                im_gray[y, x  ] = p1 << 6
                im_gray[y, x+1] = p2 << 6      
                im_gray[y, x+2] = p3 << 6
                im_gray[y, x+3] = p4 << 6

        return im_gray      


    def DecodeRaw16(self, im_byte_arr, rawformat):
        stride = rawformat._stride
        width = rawformat._width
        height = rawformat._height
        print("DecodeRaw16(w:{},h:{},s:{})".format(width, height, stride))

        im_gray = np.zeros((height, width), 'uint16')

        for y in range(height):
            # Raw10: 2 bytes -> 1 pixels
            for x in range(0, width, 1):
                offset = int(stride * y + x*2)

                # decode to 16 bit
                im_gray[y, x] = ( im_byte_arr[offset]<<8 ) | ( im_byte_arr[offset+1] )

        # Create PIL image
        return im_gray    
            
    def SplitToComponents(self, raw_bayer, rawformat):
        width = rawformat._width
        height = rawformat._height
        bayerorder = rawformat._bayerorder
        print("SplitToComponents(w:{},h:{},bo:{})".format(width, height, bayerorder))

        #+---------+
        #| C1 | C2 |
        #+---------+
        #| C3 | C4 |
        #+---------+
        c1 = self.BayerSplit(raw_bayer, width, height, 0, 0)
        c2 = self.BayerSplit(raw_bayer, width, height, 0, 1)
        c3 = self.BayerSplit(raw_bayer, width, height, 1, 0)
        c4 = self.BayerSplit(raw_bayer, width, height, 1, 1)  

        # map channels according to bayer order
        if bayerorder.lower().find("grbg") > -1:
            # G R
            # B G
            self.raw_16bpp_gr = c1
            self.raw_16bpp_r = c2
            self.raw_16bpp_b = c3
            self.raw_16bpp_gb = c4

        elif bayerorder.lower().find("rggb") > -1:
            # R G   
            # G B
            self.raw_16bpp_r = c1
            self.raw_16bpp_gr = c2
            self.raw_16bpp_gb = c3
            self.raw_16bpp_b = c4

        elif bayerorder.lower().find("bggr") > -1:
            # B G   
            # G R
            self.raw_16bpp_b = c1
            self.raw_16bpp_gb = c2
            self.raw_16bpp_gr = c3
            self.raw_16bpp_r = c4

        elif bayerorder.lower().find("gbrg") > -1:
            # G B   
            # R G
            self.raw_16bpp_gb = c1
            self.raw_16bpp_b = c2
            self.raw_16bpp_r = c3
            self.raw_16bpp_gr = c4

    def BayerSplit(self, raw_bayer, w, h, offset_x, offset_y):
        channel = np.zeros((int(h/2), int(w/2)), 'uint16')

        for y in range(offset_y, h, 2):
            for x in range(offset_x, w, 2):
                ch_y = int(y/2)
                ch_x = int(x/2)
                channel[ch_y, ch_x] = raw_bayer[y,x]

        return channel

    def SaveAs(self, decoded_raw16, filename="temp_16bpp.png"):

        if decoded_raw16.all() != None:
            Image.fromarray(decoded_raw16).save(filename)

        return


    def SaveComponents(self, decoded_raw16, rawformat):

        if decoded_raw16.all() != None:
            self.SplitToComponents(decoded_raw,rawformat)
            Image.fromarray(self.raw_16bpp_gr).save("gr.png")
            Image.fromarray(self.raw_16bpp_r).save("r.png")
            Image.fromarray(self.raw_16bpp_b).save("b.png")
            Image.fromarray(self.raw_16bpp_gb).save("gb.png")

        return


    def SaveRGB(self, decoded_raw16, rawformat):

        if decoded_raw16.all() != None:

            if self.raw_16bpp_gr is None:
                self.SplitToComponents(decoded_raw,rawformat)
    
            rgb = self.GetRGB()
            Image.fromarray(rgb).save("rgb.png")

        return

    def GetRGB(self):
        h = self.raw_16bpp_r.shape[0]
        w = self.raw_16bpp_r.shape[1]
        print("GetRGB(w:{},h:{})".format(w,h))
        
        half_rgb = np.zeros([h, w, 3], dtype=np.uint8)

        for y in range(0,h-1):
            for x in range(0,w-1):
                #print(h,w)
                r = float(self.raw_16bpp_r[y,x]) / 256
                g = ( float(self.raw_16bpp_gr[y,x]) + float(self.raw_16bpp_gb[y,x]) ) / 512
                b = float(self.raw_16bpp_b[y,x]) / 256
               
                # wb
                #r = r*2.0
                #b = b*1.7

                r = min(255, r)
                g = min(255, g)
                b = min(255, b)

                half_rgb[y,x,0] = np.uint8(r)
                half_rgb[y,x,1] = np.uint8(g)
                half_rgb[y,x,2] = np.uint8(b)

        return half_rgb
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Raw image decoder')
    parser.add_argument('--file', type=str, help='input file')
    parser.add_argument('--dir', type=str, help='input directory')
    parser.add_argument('--width', type=int, help='width', default=0)
    parser.add_argument('--height', type=int, help='height', default=0)
    parser.add_argument('--bayerorder', type=str, help='Bayer order: [GRBG,RGGB,BGRG,GBRG]', default='BGGR')
    parser.add_argument('--encoding', type=str, help='Raw format: raw8, raw10, raw12, raw16. Default: read from extension.')
    parser.add_argument('--bpp', type=int, help='Bits per pixel in raw image: 1-16, if different than encoding. Default: read from extension', default = 0)
    parser.add_argument('--splitcomponents', help='Save Gr, R, B, Gb components', action='store_true')
    parser.add_argument('--rgb', help='Save RGB output (half resolution)', action='store_true')
    parser.add_argument('--out', type=str, help='Output folder', default='./output')

    args = parser.parse_args()

    rawdecoder = RawDecode()

    #
    # Read file or directory: file parameter overrides dir
    #
    raw_images = []
    if args.file is not None:
        raw_images.append(args.file)

    elif args.dir is not None:
        input_files = os.listdir(args.dir)
    
        # Read files to list. Use file extension to check, if files are valid   
        for f in input_files:
            try:
                filename, ext = os.path.splitext(f)

                if rawdecoder.SupportedRawTypes(ext):
                    raw_images.append(f)
                else:
                    pass
                    #print("File: {} is not in list of supported raw types.".format(ext))

            except IOError:
                print("ERROR: Cannot open", f)
    else:
        print("ERROR: must define --file and/or --dir")

    path = "./"
    if args.out is not None:
        path = "{}/".format(args.out)

    #
    # Process all raw images
    #
    print("Processing supported raw images: ", raw_images)

    for rawfile in raw_images:
        filename, ext = os.path.splitext(rawfile)
        raw_data_arr = open(rawfile, "rb").read()

        # set raw encoding according to user or file extension        
        encoding = ext
        if args.encoding is not None:
            encoding = args.encoding

        # Set format
        raw_format = RawFormat(args.width, args.height, args.bpp, encoding, args.bayerorder)
        
        # Decode raw to 16 bits per pixel array
        decoded_raw = rawdecoder.Decode(raw_data_arr, raw_format)
        
        # Save decoded raw
        if not os.path.exists(path):
            os.makedirs(path)

        #basename = os.path.basename(rawfile)
        filename = filename + "{}".format(".png")
        filename = path + filename
        print("Saving:", filename)
        rawdecoder.SaveAs(decoded_raw, filename)

        if args.splitcomponents:
            rawdecoder.SaveComponents(decoded_raw, raw_format)
    
        if args.rgb:
            rawdecoder.SaveRGB(decoded_raw, raw_format)
  