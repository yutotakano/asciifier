# Asciifier.py

![Demonstration](https://i.imgur.com/YWOtVje.png)

Asciifier turns any image (or text string) into text art. Despite the name of the program containing "ascii", it supports outputting any character in unicode.

## Description

A frequently used method of generating ascii text art from an image involves the following process:

1. For each character in ASCII set, generate a small rectangle containing only the character, and find the blackness value by taking the mean colour.
2. Turn main image black-and-white and resize image to output height/width
3. For each pixel in image, find the closest blackness match in the map of characters

This method has its drawbacks in that it cannot distinguish between two characters that have the same mean color. For example, ▌ and ▐ have the same mean colour, yet they are vertical half blocks placed on the opposite sides (U+258C and U+2590). This leads to unexpected "blocky-ness" in the output, which could have been smoothed out with the proper use of a content-aware algorithm that chooses the characters.

In Asciifier, this problem is solved through sampling numerous positions within the rectangle that represents one output character. By default, the matrix size is 5, which means blackness values from 5x5=25 points are stored as a matrix. By mathematically comparing this matrix to the map of matrices for all possible characters, the precision and accuracy of choosing appropriate characters increases significantly compared to the old method. As a result, a smoother text art that accurately reflects the original image is generated.

## Usage

`python3 asciifier.py [-h] (-i IMAGE | -t TEXT) [-f FONT] [-c CHARSET] -o OUTPUT [--ratio RATIO] [--invert] [--matrix MATRIX] [--height] [--width]`

```cmd
arguments:
  -i IMAGE, --image IMAGE  Any type of image file that cv2 supports
  -t TEXT, --text TEXT     Some string of text
  -c CHARSET, --charset CHARSET
                           Character set text file, UTF-8, Ignores full-width chars
  -o OUTPUT, --output OUTPUT
                           Output file name
  --height                 Output height in number of lines, also serves as fontsize
  --width                  Output width in number of characters
  --font FONT              Font for the text to be used for display. Matrix pattern calculation
                           always uses FiraCode-Medium
  --ratio RATIO            How many times taller each character is compared to its width
  --invert                 Invert image when set
  --matrix MATRIX          Matrix size for sampling
```

## Examples

`python3 asciifier.py -i image.png -o output.txt`

⇒ The simplest usage. Takes an input image and generates art using a default scale of 10:1.

`python3 asciifier.py -i image.png --height 20 --width 40 -o output.txt`

⇒ Takes an input image, generates art using separate scale factors for horizontal and vertical (calculated from the output height/width).

`python3 asciifier.py -t "Hello :)" --font "~/path/to/font.ttf" --height 20 -o output.txt`

⇒ Creates an image of height 20 (and dynamic width), writes the input text with the specified font, then uses that temporary image to generate art.
