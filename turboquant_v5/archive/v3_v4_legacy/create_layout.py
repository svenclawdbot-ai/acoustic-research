from PIL import Image, ImageDraw, ImageFont

# Create a large image for the schematic layout
width, height = 1600, 1200
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except:
    font_title = ImageFont.load_default()
    font_header = ImageFont.load_default()
    font_text = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Title
draw.text((800, 20), "TurboQuant Mux LNA Board - Complete Schematic Layout", 
          fill='black', font=font_title, anchor='mt')

# ============ MAIN SHEET (Top) ============
y_main = 70
draw.rectangle([50, y_main, 1550, y_main+180], outline='black', width=2, fill='#f8f8f8')
draw.text((800, y_main+10), "MAIN SHEET (Root) - Hierarchical Block Diagram", 
          fill='black', font=font_header, anchor='mt')

# Title block
draw.rectangle([1350, y_main+140, 1540, y_main+170], outline='black', width=1, fill='white')
draw.text((1445, y_main+150), "TurboQuant Mux LNA", fill='black', font=font_small, anchor='mm')
draw.text((1445, y_main+162), "Rev 1.2 | 2026-03-30", fill='black', font=font_small, anchor='mm')

# POWER_SUPPLIES Block
draw.rounded_rectangle([80, y_main+50, 350, y_main+130], radius=10, 
                        outline='#2E7D32', width=3, fill='#E8F5E9')
draw.text((215, y_main+75), "POWER_SUPPLIES", fill='#1B5E20', font=font_header, anchor='mm')
draw.text((215, y_main+95), "power.kicad_sch", fill='#1B5E20', font=font_text, anchor='mm')

# Power output pins
pins = ['+12V', '+5V', '+3V3', 'GND']
for i, pin in enumerate(pins):
    y_pin = y_main + 55 + i*18
    draw.rectangle([350, y_pin, 390, y_pin+14], outline='#2E7D32', width=1, fill='white')
    draw.text((370, y_pin+7), pin, fill='#1B5E20', font=font_small, anchor='mm')
    draw.line([(390, y_pin+7), (410, y_pin+7)], fill='#2E7D32', width=2)

# DIGITAL_CONTROL Block
draw.rounded_rectangle([450, y_main+50, 720, y_main+130], radius=10, 
                        outline='#1565C0', width=3, fill='#E3F2FD')
draw.text((585, y_main+75), "DIGITAL_CONTROL", fill='#0D47A1', font=font_header, anchor='mm')
draw.text((585, y_main+95), "digital.kicad_sch", fill='#0D47A1', font=font_text, anchor='mm')

# Digital input pins
for i, pin in enumerate(['+5V', 'GND']):
    y_pin = y_main + 60 + i*25
    draw.rectangle([430, y_pin, 450, y_pin+14], outline='#1565C0', width=1, fill='white')
    draw.text((415, y_pin+7), pin, fill='#0D47A1', font=font_small, anchor='mm')
    draw.line([(410, y_pin+7), (430, y_pin+7)], fill='#1565C0', width=2)

# Digital output pins (GATE0-7)
draw.text((740, y_main+65), "GATE0-7", fill='#0D47A1', font=font_text)
for i in range(8):
    y_pin = y_main + 55 + i*9
    draw.line([(720, y_pin+4), (735, y_pin+4)], fill='#1565C0', width=2)

# ANALOG_FRONTEND Block
draw.rounded_rectangle([300, y_main+150, 800, y_main+170], radius=5, 
                        outline='#C62828', width=3, fill='#FFEBEE')
draw.text((550, y_main+160), "ANALOG_FRONTEND (analog.kicad_sch)", 
          fill='#B71C1C', font=font_text, anchor='mm')

# Power connections between blocks
draw.line([(410, y_main+85), (430, y_main+85)], fill='#2E7D32', width=3)
draw.text((420, y_main+70), "+5V", fill='#2E7D32', font=font_small)
draw.line([(410, y_main+110), (430, y_main+110)], fill='#2E7D32', width=3)
draw.text((420, y_main+125), "GND", fill='#2E7D32', font=font_small)

# GATE connections
draw.line([(735, y_main+90), (750, y_main+90)], fill='#1565C0', width=2)
draw.line([(750, y_main+90), (750, y_main+155)], fill='#1565C0', width=2)
draw.line([(750, y_main+155), (300, y_main+155)], fill='#1565C0', width=2)
draw.text((760, y_main+120), "GATE Signals", fill='#1565C0', font=font_small)

# ============ POWER SHEET (Middle Left) ============
y_pwr = 280
draw.rectangle([50, y_pwr, 750, y_pwr+280], outline='#2E7D32', width=2, fill='#fafafa')
draw.text((400, y_pwr+10), "POWER SHEET - 12V to 5V to 3.3V Regulators", 
          fill='black', font=font_header, anchor='mt')

# 12V Input
draw.text((120, y_pwr+50), "+12V INPUT", fill='#D32F2F', font=font_text)
draw.rectangle([100, y_pwr+70, 140, y_pwr+100], outline='black', width=2, fill='#FFE0B2')
draw.text((120, y_pwr+85), "J1", fill='black', font=font_text, anchor='mm')
draw.ellipse([105, y_pwr+75, 115, y_pwr+85], outline='black', fill='black')
draw.ellipse([125, y_pwr+75, 135, y_pwr+85], outline='black', fill='white')

# Wire to regulator section
draw.line([(120, y_pwr+100), (120, y_pwr+130)], fill='black', width=2)
draw.line([(120, y_pwr+130), (250, y_pwr+130)], fill='black', width=2)

# LM7805 Regulator
draw.rectangle([250, y_pwr+100, 330, y_pwr+160], outline='#1565C0', width=2, fill='#FFF8E1')
draw.text((290, y_pwr+125), "LM7805", fill='black', font=font_text, anchor='mm')
draw.text((290, y_pwr+145), "5V REG", fill='black', font=font_small, anchor='mm')

# Input cap
draw.line([(230, y_pwr+130), (230, y_pwr+150)], fill='black', width=1)
draw.line([(220, y_pwr+145), (240, y_pwr+145)], fill='#D32F2F', width=2)
draw.line([(220, y_pwr+150), (240, y_pwr+150)], fill='#D32F2F', width=2)
draw.text((200, y_pwr+147), "C1", fill='black', font=font_small)

# Output caps
draw.line([(330, y_pwr+130), (340, y_pwr+130)], fill='black', width=1)
draw.line([(340, y_pwr+130), (340, y_pwr+150)], fill='black', width=1)
draw.line([(330, y_pwr+145), (350, y_pwr+145)], fill='#D32F2F', width=2)
draw.line([(330, y_pwr+150), (350, y_pwr+150)], fill='#D32F2F', width=2)
draw.text((360, y_pwr+147), "C2", fill='black', font=font_small)

draw.line([(360, y_pwr+130), (370, y_pwr+130)], fill='black', width=1)
draw.line([(370, y_pwr+130), (370, y_pwr+150)], fill='black', width=1)
draw.line([(360, y_pwr+145), (380, y_pwr+145)], fill='#D32F2F', width=2)
draw.line([(360, y_pwr+150), (380, y_pwr+150)], fill='#D32F2F', width=2)
draw.text((390, y_pwr+147), "C3", fill='black', font=font_small)

# +5V Output
draw.line([(330, y_pwr+115), (450, y_pwr+115)], fill='#D32F2F', width=3)
draw.text((480, y_pwr+115), "+5V OUTPUT", fill='#D32F2F', font=font_text, anchor='mm')

# AMS1117-3.3 Regulator
draw.rectangle([250, y_pwr+200, 330, y_pwr+260], outline='#1565C0', width=2, fill='#FFF8E1')
draw.text((290, y_pwr+225), "AMS1117", fill='black', font=font_text, anchor='mm')
draw.text((290, y_pwr+245), "3.3V REG", fill='black', font=font_small, anchor='mm')

# Connection from 5V
draw.line([(350, y_pwr+115), (350, y_pwr+230)], fill='#D32F2F', width=2)
draw.line([(350, y_pwr+230), (330, y_pwr+230)], fill='#D32F2F', width=2)

# 3.3V caps
draw.line([(340, y_pwr+240), (340, y_pwr+260)], fill='black', width=1)
draw.line([(330, y_pwr+255), (350, y_pwr+255)], fill='#D32F2F', width=2)
draw.line([(330, y_pwr+260), (350, y_pwr+260)], fill='#D32F2F', width=2)
draw.text((360, y_pwr+257), "C4", fill='black', font=font_small)

# +3.3V Output
draw.line([(330, y_pwr+230), (450, y_pwr+230)], fill='#D32F2F', width=3)
draw.text((480, y_pwr+230), "+3.3V OUTPUT", fill='#D32F2F', font=font_text, anchor='mm')

# GND symbols
draw.line([(290, y_pwr+160), (290, y_pwr+170)], fill='black', width=2)
draw.line([(285, y_pwr+170), (295, y_pwr+170)], fill='black', width=2)
draw.line([(287, y_pwr+172), (293, y_pwr+172)], fill='black', width=1)
draw.line([(287, y_pwr+174), (293, y_pwr+174)], fill='black', width=1)

draw.line([(290, y_pwr+260), (290, y_pwr+270)], fill='black', width=2)
draw.line([(285, y_pwr+270), (295, y_pwr+270)], fill='black', width=2)
draw.line([(287, y_pwr+272), (293, y_pwr+272)], fill='black', width=1)
draw.text((310, y_pwr+275), "GND", fill='black', font=font_text)

# ============ DIGITAL SHEET (Middle Right) ============
y_dig = 280
draw.rectangle([850, y_dig, 1550, y_dig+280], outline='#1565C0', width=2, fill='#fafafa')
draw.text((1200, y_dig+10), "DIGITAL SHEET - 74HC595 Shift Register", 
          fill='black', font=font_header, anchor='mt')

# GPIO Header
draw.rectangle([870, y_dig+50, 930, y_dig+110], outline='black', width=2, fill='#E0E0E0')
draw.text((900, y_dig+65), "J2", fill='black', font=font_text, anchor='mm')
draw.text((900, y_dig+85), "GPIO 2x10", fill='black', font=font_small, anchor='mm')
# Header pins
for i in range(5):
    draw.ellipse([875, y_dig+52+i*10, 885, y_dig+62+i*10], outline='black', fill='black')
    draw.ellipse([915, y_dig+52+i*10, 925, y_dig+62+i*10], outline='black', fill='white')

# 74HC595 IC
draw.rectangle([1000, y_dig+60, 1120, y_dig+140], outline='#1565C0', width=3, fill='#E3F2FD')
draw.text((1060, y_dig+90), "74HC595", fill='black', font=font_header, anchor='mm')
draw.text((1060, y_dig+110), "8-bit Shift Reg", fill='black', font=font_small, anchor='mm')

# IC pins (left side - inputs)
inputs = ['SER', 'SRCLK', 'RCLK', '+5V', 'GND']
for i, inp in enumerate(inputs):
    y_pin = y_dig + 70 + i*14
    draw.line([(1000, y_pin), (980, y_pin)], fill='black', width=1)
    draw.text((975, y_pin), inp, fill='black', font=font_small, anchor='rm')

# IC pins (right side - outputs)
draw.text((1140, y_dig+70), "GATE0-7 OUTPUTS", fill='#1565C0', font=font_text)
for i in range(8):
    y_pin = y_dig + 65 + i*9
    draw.line([(1120, y_pin), (1135, y_pin)], fill='black', width=1)
    draw.text((1140, y_pin), f"G{i}", fill='black', font=font_small)

# Power connections
draw.line([(980, y_dig+112), (980, y_dig+240)], fill='#D32F2F', width=2)
draw.text((950, y_dig+200), "+5V", fill='#D32F2F', font=font_text)
draw.text((950, y_dig+220), "GND", fill='black', font=font_text)

# ============ ANALOG SHEET (Bottom) ============
y_ana = 590
draw.rectangle([50, y_ana, 1550, y_ana+280], outline='#C62828', width=2, fill='#fafafa')
draw.text((800, y_ana+10), "ANALOG SHEET - TX Switches, MUX, and LNA", 
          fill='black', font=font_header, anchor='mt')

# TX Section
draw.text((200, y_ana+50), "TX PATH (8-ch)", fill='#C62828', font=font_header)
for i in range(4):
    x = 80 + i*120
    draw.rectangle([x, y_ana+70, x+40, y_ana+100], outline='black', width=1, fill='#FFE0B2')
    draw.text((x+20, y_ana+85), f"EL{i}", fill='black', font=font_small, anchor='mm')
    draw.line([(x+40, y_ana+85), (x+60, y_ana+85)], fill='black', width=1)
    draw.rectangle([x+60, y_ana+70, x+100, y_ana+100], outline='#1565C0', width=2, fill='#E3F2FD')
    draw.text((x+80, y_ana+85), f"Q{i}", fill='black', font=font_text, anchor='mm')
    for j in range(5):
        draw.line([(x+80, y_ana+70-j*4), (x+80, y_ana+68-j*4)], fill='#1565C0', width=1)
    draw.text((x+80, y_ana+45), f"G{i}", fill='#1565C0', font=font_small, anchor='mm')

draw.text((600, y_ana+85), "... (4 more channels)", fill='black', font=font_text)

# Protection diodes note
draw.text((300, y_ana+120), "+ BAV99 protection diodes on all TX channels", 
          fill='black', font=font_small)

# MUX Section
draw.text((850, y_ana+50), "2x CD4051B MUX", fill='#C62828', font=font_header)
draw.rectangle([800, y_ana+70, 920, y_ana+120], outline='#6A1B9A', width=2, fill='#F3E5F5')
draw.text((860, y_ana+95), "CD4051B 8:1 MUX", fill='#4A148C', font=font_text, anchor='mm')

# LNA Section
draw.text((1050, y_ana+50), "2x LNA", fill='#C62828', font=font_header)
draw.rectangle([1000, y_ana+70, 1100, y_ana+120], outline='#E65100', width=2, fill='#FFF3E0')
draw.text((1050, y_ana+95), "OPA690 LNA", fill='#BF360C', font=font_text, anchor='mm')

# RX Output
draw.rectangle([1150, y_ana+70, 1200, y_ana+120], outline='black', width=1, fill='#FFE0B2')
draw.text((1175, y_ana+95), "SMA OUT", fill='black', font=font_small, anchor='mm')

# Connections
draw.line([(500, y_ana+85), (800, y_ana+95)], fill='black', width=1)
draw.line([(920, y_ana+95), (1000, y_ana+95)], fill='black', width=1)
draw.line([(1100, y_ana+95), (1150, y_ana+95)], fill='black', width=1)

# Power rail
draw.line([(80, y_ana+70), (80, y_ana+200)], fill='#D32F2F', width=2)
draw.line([(80, y_ana+200), (1200, y_ana+200)], fill='#D32F2F', width=2)
draw.text((600, y_ana+220), "+5V Power Rail (distributed to all sections)", 
          fill='#D32F2F', font=font_text, anchor='mm')

# Save the image
img.save('turboquant_schematic_layout.jpg', quality=95)
print("Saved: turboquant_schematic_layout.jpg (1600x1200)")
