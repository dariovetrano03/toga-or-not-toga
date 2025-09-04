from PIL import Image, ImageDraw, ImageFont
import os

script_dir = os.path.dirname(os.path.abspath(__file__))  # script folder
parent_dir = os.path.dirname(script_dir) 

# Load font
font = ImageFont.truetype(f"{parent_dir}/font/Press_Start_2P/PressStart2P-Regular.ttf", 16)

# Create blank image
img = Image.new("RGBA", (350, 125), (0, 0, 0, 0))  # transparent background
draw = ImageDraw.Draw(img)

# Draw text text
text = "←→ Nozzle exit area\n↑↓ Throttle\nL  Landing Gear\nF  Flap"
draw.multiline_text((10, 10), text, font=font, fill=(255, 255, 255, 255), spacing=8)

# Save as .png
img.save(f"{parent_dir}/sprite/instructions.png")
