# pyrawdecode
Script for decoding raw bayer images.

## Install
You need to install following Python modules:
- pip3 install pillow
- pip3 install numpy

## Supported raw formats
- RAW8: 8bits per pixel                                         
- RAW10: 10bits per pixel
- RAW12: 12bits per pixel
- RAW16: 1-16bits per pixel. LE and BE.

Byte order   | BYTE_1      | BYTE_2       | BYTE_3       | BYTE_4       | BYTE_5       | BYTE_6       | ...
-----------------------------------------------------------------------------------------------------------
- RAW8:      | P1          | P2           | P3           | P4           | P5           | P6           | ...                                        
- RAW10:     | P1_MSB      | P2_MSB       | P3_MSB       | P4_MSB       | P1_2_3_4_LSB | P5_MSB       | ...
- RAW12:     | P1_MSB      | P2_MSB       | P1_2_LSB     | P3_MSB       | P4_MSB       | P3_4_LSB     | ...
- RAW16 (LE):| P1_MSB      | P1_LSB       | P2_MSB       | P2_LSB       | P3_MSB       | P3_LSB       | ...
- RAW16 (BE):| P1_LSB      | P1_MSB       | P2_LSB       | P2_MSB       | P3_LSB       | P3_MSB       | ...

## Usage
```
usage: rawdecode.py [-h] [--file FILE] [--dir DIR] [--outdir OUTDIR] [--width WIDTH] [--height HEIGHT] [--headerbytes HEADERBYTES] [--leftbytes LEFTBYTES] [--rightbytes RIGHTBYTES] [--bayerorder BAYERORDER]
                    [--encoding ENCODING] [--bpp BPP] [--endian ENDIAN] [--png] [--jpg] [--components] [--plain16] [--rgb] [--display] [--wb WB WB WB]
                    [input]

Raw image decoder

positional arguments:
  input                 input file

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           input file
  --dir DIR             input directory
  --outdir OUTDIR       Output folder
  --width WIDTH         width
  --height HEIGHT       height
  --headerbytes HEADERBYTES
                        Header Bytes before image data
  --leftbytes LEFTBYTES
                        Extra Bytes left of image data on every line
  --rightbytes RIGHTBYTES
                        Extra Bytes right of image data on every line
  --bayerorder BAYERORDER
                        Bayer order: [GRBG,RGGB,BGGR,GBRG]
  --encoding ENCODING   Raw format: raw8, raw10, raw12, raw16. Default: read from extension.
  --bpp BPP             Bits per pixel in raw image: 1-16, if different than encoding suggests. 
                        Bpp will be used to shift data to 16bpp. Default: read from extension
  --endian ENDIAN       Use defined endianness when writing or reading 16 bit values (read/write .raw16). 
                        [le, be]. Default: le
  --png                 Save decoded raw files as png (16bit)
  --jpg                 Save decoded raw files as jpg (8bit)
  --components          Save Gr, R, B, Gb components as separate png
  --plain16             Save Plain16 (.raw16) as 16bpp binary
  --rgb                 Save RGB output (half resolution at the moment) as png (8bit)
  --display             Show processed image
  --wb WB WB WB         White balance RGB gains: [R, G, B] - applied only for RGB export. 
                        Default: 1.0 1.0 1.0
```
## Command line examples

```
Decode RAW10 file and save it as png, plain16, rgb (half resolution) and separate components as png.
% python3 rawdecode.py --width 3840 --height 2160 --file image.raw10 --rgb --plain16 --png --components
```

## Backlog
```
- Format and parameter checking
- Verify RAW8
- Verify RAW12
- Add Demosaic
- Add Gamma
- Add Black level
- Add 3x3 color matrix
```