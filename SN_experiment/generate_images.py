#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a keyboard for the noise-tagging project.
"""


from PIL import Image, ImageDraw, ImageFont


path = "/Users/u829215/pynt_codes/experiment/images"
width = 100
height = 100
keys = [
        "A", "B", "C", "D", "E", "F", "G", "H", 
        "I", "J", "K", "L", "M", "N", "O", "P", 
        "Q", "R", "S", "T", "U", "V", "W", "X", 
        "Y", "Z", "_", ".", "?", "!", "<", "#"]
colors = ["black", "white", "green", "blue"]
text_color = (128, 128, 128)

# Set font type
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", size=30)

# Speller symbols
for key in keys:
	for color in colors:
		img = Image.new("RGB", (width, height), color=color)
		img_draw = ImageDraw.Draw(img)
		text_width, text_height = img_draw.textsize(key, font=font)
		x_pos = (width - text_width) / 2
		y_pos = (height - text_height) / 2
		img_draw.text((x_pos, y_pos), key, font=font, fill=text_color)
		img.save(f"{key}_{color}.png")

# VEP fixation
for color in colors:
	img = Image.new("RGB", (width, height), color=color)
	img_draw = ImageDraw.Draw(img)
	text_width, text_height = img_draw.textsize("+", font=font)
	x_pos = (width - text_width) / 2
	y_pos = (height - text_height) / 2
	img_draw.text((x_pos, y_pos), "+", font=font, fill=text_color)
	img.save(f"+_{color}.png")

# No symbol
for color in colors:
	img = Image.new("RGB", (width, height), color=color)
	img_draw = ImageDraw.Draw(img)
	img.save(f"{color}.png")