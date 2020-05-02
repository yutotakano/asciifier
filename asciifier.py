import argparse
import sys
import math
import numpy as np
from cv2 import cv2
from PIL import Image, ImageDraw, ImageFont, ImageStat
import unicodedata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate an ASCII art file using text input or image input.')
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--image', help='Any type of image file that cv2 supports')
    input_group.add_argument('-t', '--text', help='Some string of text')
    parser.add_argument('-c', '--charset', help='Character set text file, UTF-8, Ignores full-width chars')
    parser.add_argument('-o', '--output', help='Output file name', required=True)
    parser.add_argument('--height', help='Output height in number of lines, also serves as fontsize')
    parser.add_argument('--width', help='Output width in number of characters')
    parser.add_argument('--font', help='Font for the text to be used for display. Matrix pattern calculation always uses FiraCode-Medium')
    parser.add_argument('--ratio', help='How many times taller each character is compared to its width', default='2.3')
    parser.add_argument('--invert', action='store_true', help='Invert image when set')
    parser.add_argument('--matrix', help='Matrix size for sampling', default='5')
    
    args = parser.parse_args()

    matrix_size = int(args.matrix)
    horizontal_vertical_ratio = float(args.ratio)

    if args.image is not None:
        # Image is set
        
        # 0 = grayscale
        im = cv2.imread(args.image, 0)
        
        if im is None:
            print('Image not found.')
            exit()

    else:
        if args.font is None:
            parser.error('Missing argument --font')
            exit()
        if args.height is None:
            parser.error('Missing argument <height> for font')

        im = Image.new('L', (len(args.text)*int(args.height)*matrix_size, int(args.height)*matrix_size), 255)
        font = ImageFont.truetype(args.font, int(args.height)*matrix_size - 2)
        context = ImageDraw.Draw(im)
        context.text((2, 0), args.text, 0, font)

        im = np.array(im)

    if args.invert is True:
        im = cv2.bitwise_not(im)
    
    # Alright, time to move onto sampling `im`

    source_height, source_width = im.shape[:2]
        
    # For each character/pixel of the output, the density is calculated from the shape (rectsize_h, rectsize_w)
    # the two (2) in the expressions are because usual fonts including console ones are about twice taller than wider    
    if args.height is not None and args.width is not None:
        rectsize_h = math.ceil(source_height / int(args.height))
        rectsize_w = math.ceil(source_width / (int(args.width) * horizontal_vertical_ratio))
    elif args.height is not None:
        rectsize_h = math.ceil(source_height / int(args.height))
        rectsize_w = round(rectsize_h / horizontal_vertical_ratio)
    elif args.width is not None:
        rectsize_w = math.ceil(source_width / (int(args.width) * horizontal_vertical_ratio))
        rectsize_h = round(rectsize_w * horizontal_vertical_ratio)
    else:
        rectsize_h = 10
        rectsize_w = 5
    
    output_height = math.ceil(source_height / rectsize_h)
    output_width = math.ceil(source_width / rectsize_w)
        
    # the third and fourth dimension are ALWAYS matrix_size to match the character ones
    Z = np.zeros((output_height, output_width, matrix_size, matrix_size)) 

    for y_index, actual_y_index in enumerate(range(0, len(im), rectsize_h)):
        y = im[actual_y_index]
        for x_index, actual_x_index in enumerate(range(0, len(y), rectsize_w)):
            # loops for every rectangle / output pixel
            blockend_y_index = min(actual_y_index + rectsize_h, len(im) - 1)
            blockend_x_index = min(actual_x_index + rectsize_w, len(y) - 1)

            crop_region = im[actual_y_index:blockend_y_index, actual_x_index:blockend_x_index]
            padded_crop_region = np.ones((rectsize_h, rectsize_w))*255
            padded_crop_region[:crop_region.shape[0],:crop_region.shape[1]] = crop_region
            # hopefully inter_cubic works for this
            resized_padded_crop_region = cv2.resize(padded_crop_region, dsize=(matrix_size, matrix_size), interpolation=cv2.INTER_CUBIC)

            Z[y_index][x_index] = resized_padded_crop_region
        
    # Great I don't even remember what I was doing above when I wrote it yesterday night at 4am but it kinda seems to work
    # Now we have a 4 dimensional array
    # [ for each height
    #   [ for each width
    #       [ for each height in the rect
    #           [ for each width in the rect
    #               grayscale value from 0-255.0
    #           ]
    #       ]
    #   ]
    # ]

    # Not necessary but having values between 0-1 makes me feel better
    Z = Z / 255.0

    # Default charset ASCII if none is specified
    charset = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]\\^_`abcdefghijklmnopqrstuvwxyz{|}~'
    if args.charset is not None:
        try:
            with open(args.charset, mode='r', encoding='utf-8') as f:
                charset = f.read()
                charset = unicodedata.normalize('NFKC', charset)
        except Exception as e:
            pass
    
    # For each character, create a matrix and append it to `data`
 
    char_data = []

    # Use FiraCode because it's a fairly standard Console font and ascii art will be displayed in a similar font most of the time
    font = ImageFont.truetype(r"FiraCode-Medium.ttf", matrix_size)
    letter_image = Image.new('L', (round(matrix_size / horizontal_vertical_ratio), matrix_size), 255)
    for char in charset:
        char_width = unicodedata.east_asian_width(char)
        # Don't check for 'A' (Ambiguous) because that would eliminate █ as well
        if char_width in ['F', 'W']:
            continue
        canvas = ImageDraw.Draw(letter_image)
        canvas.text((0, 0), char, 0, font)
        char_data.append({
            'character': char,
            'matrix': cv2.resize(np.array(letter_image), (matrix_size, matrix_size)) / 255.0
        })
        # blank canvas again
        canvas.rectangle((0, 0, round(matrix_size / horizontal_vertical_ratio), matrix_size), 255)
    
    
    final_output = ''
    # Loop over rows of rectangle
    for index, row in enumerate(Z):
        # Loop over actual rectangles
        for rectangle in row:
            # 1. for each character calculate: the sum of (the element-wise absolute difference between rectangle data and character data)
            # 2. find the indices of the one with the minimum total
            # 3. output the textual representation of that
            indice = np.argmin([np.sum(np.absolute(rectangle - char['matrix'])) for char in char_data])
            final_output = f"{final_output}{char_data[indice]['character']}"

        # Unless last row, add new line
        if index != len(Z) - 1:
            final_output = f"{final_output}\n"
    
    with open(args.output, "w", encoding="utf-8") as text_file:
        print(final_output, file=text_file)