# pyrawdecode
Script for decoding raw bayer images (e.g. raw8, raw10, raw12, raw16).

## Install
You need to install following Python modules:
- pip3 install pil
- pip3 install numpy

## Usage
```
usage: rawdecode.py [-h] [--file FILE] [--dir DIR] [--width WIDTH] [--height HEIGHT] [--bayerorder BAYERORDER] [--encoding ENCODING] [--bpp BPP] [--png] [--components] [--rgb] [--plain16] [--outdir OUTDIR]

Raw image decoder

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           input file
  --dir DIR             input directory
  --width WIDTH         width
  --height HEIGHT       height
  --bayerorder BAYERORDER
                        Bayer order: [GRBG,RGGB,BGRG,GBRG]
  --encoding ENCODING   Raw format: raw8, raw10, raw12, raw16. Default: read from extension.
  --bpp BPP             Bits per pixel in raw image: 1-16, if different than encoding. Default: read from extension
  --png                 Save decoded raw files as png
  --components          Save Gr, R, B, Gb components as separate png
  --rgb                 Save RGB output (half resolution at the moment) as png
  --plain16             Save Plain16 (raw16) as binary
  --outdir OUTDIR       Output folder
```
## Command line examples

```
Decode RAW10 file and save it as png, plain16, rgb (half resolution) and separate components as png.
% python3 rawdecode.py --width 3840 --height 2160 --file image.raw10 --rgb --plain16 --png --components
```