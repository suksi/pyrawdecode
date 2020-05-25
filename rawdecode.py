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
        self._bpp = bpp
        self._bayerorder = bayerorder
        self._encoding = encoding

        self._stride = self.GetStride(w, encoding)

        self.CheckFormat()

        return

    def CheckFormat(self):
        print("Format, bayer order, w, h, bpp, stride: ", self._encoding, self._bayerorder, self._width, self._height, self._bpp, self._stride)


    def GetStride(self, w, encoding):
        if encoding.lower().find("raw8") > -1:
            return int(w)
        if encoding.lower().find("raw10") > -1:
            return int(w*10/8)
        if encoding.lower().find("raw12") > -1:
            return int(w*12/8)
        if encoding.lower().find("raw16") > -1:
            return int(w*2)

 
    def SetDimensions(self, w, h):
        
        if w <= 0 and h <= 0:
            print ("ERROR: set width and height")
                        
            return

        self._width = w
        self._height = h

        return


class RawDecode(object):
    """ Raw Decode
    Raw decoder
    """
    def __init__(self):
        # decoded byte array in 16bpp format
        self.decoded_raw16_arr = None

        # 16bpp PIL image created from 16bpp array buffer
        self.image16bpp = None

        # Bayer channels separately
        self.raw_16bpp_r = None
        self.raw_16bpp_gr = None
        self.raw_16bpp_gb = None
        self.raw_16bpp_b = None

        self.raw_types = ["raw8", "raw10", "raw12", "raw16"]
       
        return


    def Decode(self, im_byte_arr, rawformat):

        if rawformat._encoding.lower().find('raw8') > -1:
            self.decoded_raw16_arr = self.DecodeRaw8(im_byte_arr, rawformat._width, rawformat._height)

        elif rawformat._encoding.lower().find('raw10') > -1:
            self.decoded_raw16_arr = self.DecodeRaw10(im_byte_arr, rawformat._width, rawformat._height)
        
        elif rawformat._encoding.lower().find('raw12') > -1:
            self.decoded_raw16_arr = self.DecodeRaw16(im_byte_arr, rawformat._width, rawformat._height)

        elif rawformat._encoding.lower().find('raw16') > -1:
            self.decoded_raw16_arr = self.DecodeRaw16(im_byte_arr, rawformat._width, rawformat._height)

        self.SplitToChannels(self.decoded_raw16_arr, rawformat._width, rawformat._height, rawformat._bayerorder)

        return


    def Save(self, filename="temp_16bpp.png"):

        if self.decoded_raw16_arr.all() != None:
            Image.fromarray(self.decoded_raw16_arr).save(filename)
            Image.fromarray(self.raw_16bpp_gr).save("gr.png")
            Image.fromarray(self.raw_16bpp_r).save("r.png")
            Image.fromarray(self.raw_16bpp_b).save("b.png")
            Image.fromarray(self.raw_16bpp_gb).save("gb.png")

            rgb = self.GetRGB()
            Image.fromarray(rgb).save("rgb.png")

        return

    def GetRGB(self):
        h = self.raw_16bpp_r.shape[0]
        w = self.raw_16bpp_r.shape[1]
        
        half_rgb = np.zeros([h, w, 3], dtype=np.uint8)

        #gr = Image.fromarray(self.raw_16bpp_gr)
        #r = Image.fromarray(self.raw_16bpp_r)
        #b = Image.fromarray(self.raw_16bpp_b)
        #gb = Image.fromarray(self.raw_16bpp_gb)

        print(h,w)

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

    def DecodeRaw10(self, im_byte_arr, width, height):
        print("DecodeRaw10():", width, height)

        im_gray = np.zeros((height, width), 'uint16')
        stride = int(width*10/8)

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

        # Create PIL image
        return im_gray      


    def DecodeRaw16(self, im_byte_arr, width, height):
        print("DecodeRaw16():", width, height)

        im_gray = np.zeros((height, width), 'uint16')
        stride = int(width*2)

        for y in range(height):
            # Raw10: 2 bytes -> 1 pixels
            for x in range(0, width, 1):
                offset = int(stride * y + x*2)

                # decode to 16 bit
                im_gray[y, x] = ( im_byte_arr[offset]<<8 ) | ( im_byte_arr[offset+1] )

        # Create PIL image
        return im_gray    


    def DecodeRaw8(self, im_byte_arr, width, height):
        print("DecodeRaw16():", width, height)

        im_gray = np.zeros((height, width), 'uint16')
        stride = int(width)

        for y in range(height):
            # Raw10: 1 byte -> 1 pixel
            for x in range(0, width, 1):
                offset = int(stride * y + x)

                # decode to 16 bit
                im_gray[y, x] = ( im_byte_arr[offset]<<8 )

        # Create PIL image
        return im_gray    

    def SplitToChannels(self, raw_bayer, width, height, bayerorder):
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

        return


    def BayerSplit(self, raw_bayer, w, h, offset_x, offset_y):
        w = int(w/2)
        h = int(h/2)

        channel = np.zeros((h, w), 'uint16')

        for y in range(offset_y, h*2, 2):
            for x in range(offset_x, w*2, 2):
                ch_y = int(y/2)
                ch_x = int(x/2)
                channel[ch_y, ch_x] = raw_bayer[y,x]

        return channel

    def SupportedRawTypes(self, ext):
        for supported_type in self.raw_types:
            if ext.lower().find(supported_type) > -1:
                return True

        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Raw image decoder')
    parser.add_argument('--file', type=str, help='input file')
    parser.add_argument('--dir', type=str, help='input directory')
    parser.add_argument('--width', type=int, help='width', default=0)
    parser.add_argument('--height', type=int, help='height', default=0)
    parser.add_argument('--format', type=str, help='Raw format: raw8, raw10, raw12, raw16. Default: raw16', default='raw16')
    parser.add_argument('--bpp', type=int, help='Bit depth: 1-16. Default: 16', default=16)
    parser.add_argument('--out', type=str, help='Output file: [png]', default='png')

    args = parser.parse_args()

    rawdecoder = RawDecode()

    raw_data_arr = None

    if args.file is not None:
        input_files = [args.file] 

    elif args.dir is not None:
        input_files = os.listdir(args.dir)
        
    raw_images = []
    for f in input_files:
        try:
            filename, ext = os.path.splitext(f)

            if rawdecoder.SupportedRawTypes(ext):
               raw_images.append(f)

        except IOError:
            print("cannot open", f)

    print("Found supported raw images: ", raw_images)

    for raw in raw_images:
        print()
        raw_data_arr = open(raw, "rb").read()

        # set raw format according to user of file extension
        raw_format = RawFormat(args.width, args.height, args.bpp, args.format, "BGGR")
        
        rawdecoder.Decode(raw_data_arr, raw_format)
        rawdecoder.Save()
  