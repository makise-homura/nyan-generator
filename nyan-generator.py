#!/usr/bin/env python3

import av
import random
from PIL import Image, ImageDraw, ImageFont

fontname = 'CC Wild Words Roman'
fonttext = 'Nyan'

# Background source and output video parameters
source = av.open('source.mp4', mode = 'r').decode(video=0) # or None if no back is needed
container = av.open('result.mp4', mode = 'w')
stream = container.add_stream('mpeg4', rate = 30)
stream.width = 1280
stream.height = 720
stream.pix_fmt = 'yuv420p'
maxframe = 3600 # 3600 / 30 = 120 seconds of resulting video

def generate():
    p = {}
    p['x'] = random.randrange(20, 1260)
    p['y'] = random.randrange(740, 780)
    p['a'] = random.randrange(0, 360)
    p['s'] = random.randrange(40, 100)
    p['dx'] = random.randrange(-5, 5) 
    p['dy'] = random.randrange(-25, -20)
    p['da'] = random.randrange(2, 15) * random.randrange(-1, 2, 2)
    return p;

def increment(p):
    p['x'] += p['dx']
    p['y'] += p['dy']
    p['a'] += p['da']
    p['dy'] += 1
    return p;

def outofbounds(p):
    return p['y'] > 800 and p['dy'] > 0

pp = [ generate(), generate(), generate(), generate(), generate() ] # How many simultaneous "nyan"s required

for frame in range(0, maxframe):

    # Initialize frame image
    if source is None:
        img = Image.new('RGBA', (1280, 720), color = (255, 255, 255, 255))
    else:
        img = next(source).to_image().convert('RGBA')
    print('Processing frame', frame, end = '\r', flush = True)

    for i in range(0, len(pp) - 1):
        pp[i] = increment(pp[i])
        if outofbounds(pp[i]):
            pp[i] = generate()
        image = Image.new('RGBA', (400, 400), color = (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((200, 200), fonttext, font = ImageFont.truetype(fontname, pp[i]['s']), fill = (0, 0, 0, 255), anchor = 'mm')
        image = image.rotate(pp[i]['a'])
        image = image.crop((60,60,340,340))
        image2 = Image.new('RGBA', (2560, 1440), color = (255, 255, 255, 0))
        image2.alpha_composite(image, (pp[i]['x'] - 140 + 640, pp[i]['y'] - 140 + 360))
        image2 = image2.crop((640,360,1920,1080))
        img.alpha_composite(image2)

    # Pack frame to output stream
    frame = av.VideoFrame.from_image(img)
    for packet in stream.encode(frame):
        container.mux(packet)

for packet in stream.encode():
    container.mux(packet)

container.close()