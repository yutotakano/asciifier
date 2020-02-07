from PIL import Image, ImageDraw, ImageFont, ImageStat
import sys

if len(sys.argv) != 7:
    print('Wrong number of arguments. Format: python "ascii art.py" "texthere" width height output_width output_height font')
    exit()

(text, width, height, output_width, output_height, font_file) = sys.argv[1:]
width = int(width)
height = int(height)
output_width = int(output_width)
output_height = int(output_height)

letter_image = Image.new('RGB', (60, 100), (255, 255, 255))
font = ImageFont.truetype(r"FiraCode-Medium.ttf", 100)
characters = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]\\^_`abcdefghijklmnopqrstuvwxyz{|}~'
data = []
for character_index in range(len(characters)):
    canvas = ImageDraw.Draw(letter_image)
    canvas.text((0, 0), characters[character_index], (0, 0, 0, 255), font)
    data.append({
        'character': characters[character_index],
        'value': ImageStat.Stat(letter_image).mean[0]
    })
    canvas.rectangle((0, 0, 60, 100), (255, 255, 255))

data.sort(key=lambda item: item['value'], reverse=False)

im = Image.new('RGB', (width, height), (255, 255, 255))
font = ImageFont.truetype(font_file, height - 2)
context = ImageDraw.Draw(im)
context.text((2, 0), text, (0, 0, 0, 255), font)
resized_im = im.resize((output_width, output_height), Image.NEAREST)
final_output = ''

for y in range(output_height):
    for x in range(output_width):
        r, g, b = resized_im.getpixel((x, y))
        if r != g or r != b:
            continue 
        index = r / (255 / len(characters))
        if index > len(characters) - 1: index = index - 1
        character = data[round(index)]['character']
        final_output = f'{final_output}{character}'
        if x == output_width - 1:
            final_output = f"{final_output}\n"

with open("ascii output.txt", "w") as text_file:
    print(final_output, file=text_file)
