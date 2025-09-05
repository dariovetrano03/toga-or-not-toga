from PIL import Image, ImageDraw, ImageFont
import os

script_dir = os.path.dirname(os.path.abspath(__file__))  # script folder
parent_dir = os.path.dirname(script_dir) 

# Load font
font = ImageFont.truetype(f"{parent_dir}/font/Press_Start_2P/PressStart2P-Regular.ttf", 16)

# Your text
# text = "←→ Nozzle exit area\n↑↓ Throttle\nL  Landing Gear\nF  Flap"
text = "GAME\nOVER"

# Create a temporary draw object (just for measuring)
dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
dummy_draw = ImageDraw.Draw(dummy_img)

# Get bounding box of the multiline text
bbox = dummy_draw.multiline_textbbox((0, 0), text, font=font, spacing=8)

# bbox = (left, top, right, bottom)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Add some padding
padding = 20
img_width = text_width + padding
img_height = text_height + padding

# Now create the real image
img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw the text centered with padding
draw.multiline_text((padding // 2, padding // 2), text, font=font, fill=(255, 255, 255, 255), spacing=8)

# Save
# img.save(f"{parent_dir}/sprite/instructions.png")
img.save(f"{parent_dir}/sprite/game_over_text.png")
