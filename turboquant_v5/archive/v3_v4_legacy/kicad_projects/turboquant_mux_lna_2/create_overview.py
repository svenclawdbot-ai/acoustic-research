from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (1400, 900), 'white')
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except:
    font_title = ImageFont.load_default()
    font_header = ImageFont.load_default()
    font_text = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw.text((700, 25), "TurboQuant Mux LNA - System Architecture Overview", 
           fill='black', font=font_title, anchor='mt')

# Input section
draw.rounded_rectangle([50, 80, 250, 160], radius=10, outline='#424242', width=2, fill='#F5F5F5')
draw.text((150, 100), "INPUTS", fill='black', font=font_header, anchor='mm')
draw.text((150, 125), "12V DC Power", fill='black', font=font_text, anchor='mm')
draw.text((150, 142), "8x TX SMA | 2x RX SMA", fill='black', font=font_small, anchor='mm')

# Power system
draw.rounded_rectangle([300, 80, 550, 160], radius=10, outline='#2E7D32', width=2, fill='#E8F5E9')
draw.text((425, 100), "POWER SYSTEM", fill='#1B5E20', font=font_header, anchor='mm')
draw.text((425, 125), "LM7805: 12V to 5V", fill='#1B5E20', font=font_text, anchor='mm')
draw.text((425, 142), "AMS1117: 5V to 3.3V", fill='#1B5E20', font=font_text, anchor='mm')

# Digital control
draw.rounded_rectangle([600, 80, 850, 160], radius=10, outline='#1565C0', width=2, fill='#E3F2FD')
draw.text((725, 100), "DIGITAL CONTROL", fill='#0D47A1', font=font_header, anchor='mm')
draw.text((725, 125), "74HC595 Shift Register", fill='#0D47A1', font=font_text, anchor='mm')
draw.text((725, 142), "8x GATE outputs", fill='#0D47A1', font=font_text, anchor='mm')

# TX Switch Array
draw.rounded_rectangle([50, 200, 450, 350], radius=10, outline='#C62828', width=2, fill='#FFEBEE')
draw.text((250, 220), "TX SWITCH ARRAY (8 channels)", fill='#B71C1C', font=font_header, anchor='mm')
for i in range(4):
    x = 80 + i*90
    draw.rectangle([x, 260, x+60, 320], outline='#1565C0', width=2, fill='white')
    draw.text((x+30, 290), f"BSS138 Ch{i}", fill='black', font=font_small, anchor='mm')
draw.text((250, 335), "+ BAV99 protection diodes", fill='black', font=font_small, anchor='mm')

# Analog MUX
draw.rounded_rectangle([500, 200, 700, 350], radius=10, outline='#6A1B9A', width=2, fill='#F3E5F5')
draw.text((600, 240), "2x CD4051B", fill='#4A148C', font=font_header, anchor='mm')
draw.text((600, 270), "Analog MUX", fill='#4A148C', font=font_text, anchor='mm')
draw.text((600, 300), "8:1 multiplexer", fill='#4A148C', font=font_small, anchor='mm')
draw.text((600, 320), "for RX channels", fill='#4A148C', font=font_small, anchor='mm')

# LNA
draw.rounded_rectangle([750, 200, 950, 350], radius=10, outline='#E65100', width=2, fill='#FFF3E0')
draw.text((850, 240), "2x LNA", fill='#BF360C', font=font_header, anchor='mm')
draw.text((850, 275), "OPA690", fill='#BF360C', font=font_text, anchor='mm')
draw.text((850, 300), "Wideband Amp", fill='#BF360C', font=font_small, anchor='mm')
draw.text((850, 325), "Gain = 1 + Rf/Rg", fill='#BF360C', font=font_small, anchor='mm')

# GPIO Interface
draw.rounded_rectangle([1000, 200, 1200, 350], radius=10, outline='#1565C0', width=2, fill='#E3F2FD')
draw.text((1100, 230), "GPIO INTERFACE", fill='#0D47A1', font=font_header, anchor='mm')
draw.text((1100, 260), "2x10 Header", fill='#0D47A1', font=font_text, anchor='mm')
draw.text((1100, 285), "SER, SRCLK, RCLK", fill='#0D47A1', font=font_small, anchor='mm')
draw.text((1100, 310), "MUX_A, MUX_B, MUX_C", fill='#0D47A1', font=font_small, anchor='mm')

# Outputs
draw.rounded_rectangle([400, 400, 900, 480], radius=10, outline='#424242', width=2, fill='#F5F5F5')
draw.text((650, 420), "OUTPUTS", fill='black', font=font_header, anchor='mm')
draw.text((650, 450), "TX: 8x Element outputs (SMA)  |  RX: 2x LNA outputs (SMA)", 
           fill='black', font=font_text, anchor='mm')

# Connections
# Power
draw.line([(250, 120), (300, 120)], fill='#2E7D32', width=3)
# Control to switches
draw.line([(725, 160), (725, 180)], fill='#1565C0', width=2)
draw.line([(725, 180), (250, 180)], fill='#1565C0', width=2)
draw.line([(250, 180), (250, 200)], fill='#1565C0', width=2)
draw.text((350, 170), "GATE0-7", fill='#1565C0', font=font_small)

# TX to MUX
draw.line([(450, 275), (500, 275)], fill='black', width=2)
# MUX to LNA
draw.line([(700, 275), (750, 275)], fill='black', width=2)

# GPIO to Control
draw.line([(1100, 200), (1100, 170)], fill='#1565C0', width=2)
draw.line([(1100, 170), (850, 170)], fill='#1565C0', width=2)
draw.line([(850, 170), (850, 160)], fill='#1565C0', width=2)

# LNA to Output
draw.line([(850, 350), (850, 380)], fill='black', width=2)
draw.line([(850, 380), (650, 380)], fill='black', width=2)
draw.line([(650, 380), (650, 400)], fill='black', width=2)

img.save('turboquant_system_architecture.jpg', quality=95)
print("Saved: turboquant_system_architecture.jpg (1400x900)")
print("\nBoth images created successfully!")
