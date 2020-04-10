#!/usr/bin/env python

import argparse
import base64
import io
import libxmp
import logging
import zipfile

parser = argparse.ArgumentParser(
    description='Extract files from image metadata')
parser.add_argument('image',            help='Image with embedded files in metadata')

def extract_payload(payload):
    payload_io = io.BytesIO(base64.b64decode(payload))
    with zipfile.ZipFile(
            payload_io, mode='r', compression=zipfile.ZIP_LZMA) as zip_file:
        for filename in zip_file.namelist():
            logging.info(f'Extracting {filename}')
            zip_file.extract(filename)

if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    xmp_file = libxmp.XMPFiles(file_path=args.image)
    xmp_meta = xmp_file.get_xmp()

    if xmp_meta is None:
        print(f'Image {args.image} does not contain any embedded files')

    extract_payload(xmp_meta.get_property(
         libxmp.consts.XMP_NS_DC, u'embedded_payload'))
