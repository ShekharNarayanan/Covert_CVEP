"""
@author: Shekhar Narayanan (shekharnarayanan833@gmail.com), Jordy Thielen* (jordy.thielen@donders.ru.nl)
*: corresponding author

Python script for generating the images used in the stimulus paradigm
"""
# import libraries
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
from itertools import cycle
import math

# define relevant functions
def makeRectangle(l, w, theta, offset=(0,0)):
    """
    Make a rotated rectangle

    Args:
        l (float): length
        w (float): width
        theta (float): rotation angle in degrees
        offset (tuple, optional): center of the rectangle. Defaults to (0,0).

    Returns:
        list: All coordinates of the rotated rectangle
    """
    c, s = math.cos(theta), math.sin(theta)
    rectCoords = [(l/2.0, w/2.0), (l/2.0, -w/2.0), (-l/2.0, -w/2.0), (-l/2.0, w/2.0)]
    return [(c*x-s*y+offset[0], s*x+c*y+offset[1]) for (x,y) in rectCoords]

path = r'C:\Users\s1081686\Desktop\RA_Project\Graz\graz_codes\experiment\images' # save images here
os.makedirs(path, exist_ok=True)

# image specifications
width = 280
height = 280
background_colors = ["black", "white"]

# shape specifications
shapes = ['r', 'c', 'i', 't', 'h'] # rectangle, circle, inv triangle, triangle, hourglass
shape_colors = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 204, 0),(255, 0, 255) ] # red rectangle, green circle, cyan inverted triangle, yellow triangle, magenta hourglass
shape_color_cycle = cycle(shape_colors)

# Set font type
font = ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf", size=100)

# generate images with all shapes
for key_i in range(len(shapes)):
    key = shapes[key_i]
    text_col = next(shape_color_cycle)
    for color in background_colors:
        img = Image.new("RGB", (width, height), color=color)
        img_draw = ImageDraw.Draw(img)
        text_width, text_height = img_draw.textsize(key, font=font)
        x_pos = (width - text_width) / 2
        y_pos = (height - text_height) / 2
        
        if key_i ==0: # rectangle

            l = text_height
            w = text_width
            theta  = 45*math.pi/180
            rect  = makeRectangle(1.5*l, 0.75*w, theta, offset=(height/2,width/2))
            img_draw.polygon(rect, fill=text_col)
            img  = ImageEnhance.Brightness(img).enhance(1.5)
           
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i ==1: # circle
            x = width/2
            y = height/2
            r = 0.75*text_height
            leftUpPoint = (x-r, y-r)
            rightDownPoint = (x+r, y+r)
            twoPointList = [leftUpPoint, rightDownPoint]
            img_draw.ellipse(twoPointList, fill= text_col)
            img  = ImageEnhance.Brightness(img).enhance(1.5) # enhance brightness to 150%
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i == 2: #inverted triangle
            
            img_draw.polygon([(x_pos- text_width/2, y_pos),(x_pos + 3/2*text_width, y_pos ) , (width/2, height/2 + text_height/2)], fill=text_col)  
            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))
            
        elif key_i == 3: #triangle
            
            img_draw.polygon([(x_pos - text_width/2, y_pos + text_height),(x_pos + 3/2*text_width, y_pos + text_height) , (width/2, height/2 - text_height/2)], fill=text_col)   
            img  = ImageEnhance.Brightness(img).enhance(1.5) 
            img.save(os.path.join(path, f"{key}_{color}.png"))
             
            
        elif key_i ==4: # hourglass
       
            img_draw.polygon([(x_pos- text_width/2, y_pos),(x_pos + 3/2*text_width, y_pos ) , (width/2, height/2)], fill=text_col) # upper triangle
            img_draw.polygon([(x_pos- text_width/2, y_pos + text_height),(x_pos + 3/2*text_width, y_pos + text_height) , (width/2, height/2)], fill=text_col) # lower triangle

            img  = ImageEnhance.Brightness(img).enhance(1.5)
            img.save(os.path.join(path, f"{key}_{color}.png"))

# No shapes, just images with a black or white background
for color in background_colors:
	img = Image.new("RGB", (width, height), color=color)
	img_draw = ImageDraw.Draw(img)
	img.save(os.path.join(path,f"{color}.png"))