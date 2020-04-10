#!/usr/bin/env python

import argparse
import base64
import io
import libxmp
import logging
import os.path
import zipfile

# Command line argument parsing
parser = argparse.ArgumentParser(
    description='Embed files in image metadata')
parser.add_argument('filename', nargs='+',
                    help='File to embed in image metadata')
parser.add_argument('--input', required=True,
                    help='Input image to use as template')
parser.add_argument('--output', required=True,
                    help='Output image including files as metadata')


# Returns base64-encoded ZIP archive with all files in file listing
def generate_payload(file_listing):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
            zip_buffer, mode='w', compression=zipfile.ZIP_LZMA) as zip_file:
        for filename in file_listing:
            logging.info(f'Compressing file {filename}')
            zip_file.write(filename, os.path.basename(filename))
    return base64.b64encode(zip_buffer.getbuffer()).decode('utf8')


if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    # Create a copy of the input file
    with open(args.output, 'wb') as output_io:
        output_io.write(open(args.input, 'rb').read())

    logging.info(f'Reading input image {args.input}')
    xmp_file = libxmp.XMPFiles(file_path=args.output, open_forupdate=True)
    xmp_meta = libxmp.XMPMeta()
    xmp_meta.set_property(libxmp.consts.XMP_NS_DC,
                          u'embedded_payload', generate_payload(args.filename))

    logging.info(f'Writing output image {args.output}')
    xmp_file.put_xmp(xmp_meta)
    xmp_file.close_file()
