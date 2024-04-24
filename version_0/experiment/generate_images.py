#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a keyboard for the noise-tagging project.
"""


from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
from itertools import cycle


path = r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_experiment\images_BOTH_SIZE_INC"
os.makedirs(path, exist_ok=True)
width = 240
height = 240
circle = u'\u25CF'  # Unicode character for a filled circle
triangle = u'\u25B2'  # Unicode character for an upward-pointing triangle
square = u'\u25A0'  # Unicode character for a square
hour_gl = u'\u23F3'  # Unicode character for a star
cross = u'\u271A'  # Unicode character for a cross
# keys = [circle, triangle, square, hour_gl, cross]
keys = ['s', 'c', 'i', 't', 'h'] # rectangle, circle, inv triangle, triangle, hourglass

colors = ["black", "white"]
'luminance check remaining'
text_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 204, 0),(255, 0, 255) ] # r g b dark - y magenta
text_color_cycle = cycle(text_color)
# Set font type
font = ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf", size=100)

# Speller symbols
for key_i in range(len(keys)):
    key = keys[key_i]
    text_col = next(text_color_cycle)
    for color in colors:
        img = Image.new("RGB", (width, height), color=color)
        img_draw = ImageDraw.Draw(img)
        text_width, text_height = img_draw.textsize(key, font=font)
        x_pos = (width - text_width) / 2
        y_pos = (height - text_height) / 2
        
        if key_i ==0: # square
            img_draw.polygon([(x_pos, y_pos),(x_pos + text_width, y_pos) , (x_pos + text_width, y_pos + text_height), (x_pos, y_pos + text_height)], fill=text_col)
            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i ==1: # circle
            x = width/2
            y = height/2
            r = text_height/2
            leftUpPoint = (x-r, y-r)
            rightDownPoint = (x+r, y+r)
            twoPointList = [leftUpPoint, rightDownPoint]
            img_draw.ellipse(twoPointList, fill= text_col)
            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i == 2: #inverted triangle
            
            img_draw.polygon([(x_pos, y_pos),(x_pos + text_width, y_pos ) , (width/2, height/2 + text_height/2) ], fill=text_col)  
            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i == 3: #triangle
            
            img_draw.polygon([(x_pos + text_width, y_pos + text_height), (x_pos, y_pos + text_height), (width/2, height/2 - text_height/2) ], fill=text_col)  
            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
             
            
        elif key_i ==4:

            # Draw Hourglass            
            img_draw.polygon([(x_pos, y_pos),(x_pos + text_width, y_pos ) , (width/2, height/2)], fill=text_col) # upper triangle
            img_draw.polygon([(x_pos, y_pos + text_height),(x_pos + text_width, y_pos + text_height) , (width/2, height/2)], fill=text_col) # lower triangle

            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
		

# # VEP fixation
# for color in colors:
# 	img = Image.new("RGB", (width, height), color=color)
# 	img_draw = ImageDraw.Draw(img)
# 	text_width, text_height = img_draw.textsize("+", font=font)
# 	x_pos = (width - text_width) / 2
# 	y_pos = (height - text_height) / 2
# 	img_draw.text((x_pos, y_pos), "+", font=font, fill=text_color)
# 	img.save(os.path.join(path,f"+_{color}.png"))

# No symbol
for color in colors:
	img = Image.new("RGB", (width, height), color=color)
	img_draw = ImageDraw.Draw(img)
	img.save(os.path.join(path,f"{color}.png"))