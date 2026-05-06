#!/usr/bin/env python3
"""
TurboQuant MUX/LNA Board - SKiDL Implementation with Red Pitaya Interface

A programmable 8-channel analog multiplexer with low-noise amplification
designed for Red Pitaya STEMlab integration. Controlled via E1 GPIO header.

Features:
- 8-channel TX switching (controlled by 74HC595 shift register)
- Dual 8:1 analog multiplexers (CD4051B) for I/Q acquisition
- Dual low-noise amplifiers (OPA1641) with gain of 10
- 12V → 5V → 3.3V power regulation
- Red Pitaya E1 GPIO control interface
- SMA connectors for TX input and RX0/RX1 outputs
"""

from skidl import *

# ============================================================================
# POWER SUPPLIES MODULE
# ============================================================================

class PowerSupplies(SubCircuit):
    """12V → 5V → 3.3V power regulation with protection"""
    
    def __init__(self):
        self.initialize()
        
        # Input: 12V screw terminal
        self.vin_12v = Net('12V_IN')
        self.gnd = Net('GND')
        
        # Protection: Polyfuse + reverse polarity diode
        self.fuse = Part('Device', 'Polyfuse', value='2A', footprint='Fuse:Fuse_1206_3216Metric')
        self.d_protection = Part('Device', 'D_Schottky', value='1N4007', footprint='Diode_SMD:D_SOD-123')
        
        # 12V → 5V: LM7805 (TO-220)
        self.reg_5v = Part('Regulator_Linear', 'LM7805_TO220', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
        
        # 5V → 3.3V: AMS1117-3.3 (SOT-223)
        self.reg_3v3 = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
        
        # Decoupling capacitors
        self.c_in_12v = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_5v_in = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_5v_out = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_3v3_in = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_3v3_out = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0805_2012Metric')
        
        # Define outputs
        self.vout_5v = Net('5V')
        self.vout_3v3 = Net('3V3')
        self.vee = Net('GND')  # Negative supply (ground for single-supply operation)
        
        # Connections: 12V input path
        self.vin_12v & self.fuse & self.d_protection['A,K'] & self.reg_5v['VI']
        self.d_protection['K'] & self.c_in_12v & self.gnd
        
        # LM7805 connections
        self.reg_5v['GND'] += self.gnd
        self.reg_5v['VI'] & self.c_5v_in & self.gnd
        self.vout_5v += self.reg_5v['VO']
        self.vout_5v & self.c_5v_out & self.gnd
        
        # AMS1117-3.3 connections
        self.vout_5v += self.reg_3v3['VI']
        self.reg_3v3['GND'] += self.gnd
        self.reg_3v3['VI'] & self.c_3v3_in & self.gnd
        self.vout_3v3 += self.reg_3v3['VO']
        self.vout_3v3 & self.c_3v3_out & self.gnd
        
        self.finalize()


# ============================================================================
# DIGITAL CONTROL MODULE (74HC595 Shift Register)
# ============================================================================

class DigitalControl(SubCircuit):
    """74HC595 8-bit shift register for MUX/LNA control"""
    
    def __init__(self):
        self.initialize()
        
        # Power
        self.vcc = Net('5V')
        self.gnd = Net('GND')
        
        # 74HC595 Shift Register (SOIC-16)
        self.sr = Part('74xx', '74HC595', footprint='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm')
        
        # Control signals (from MCU/RPi)
        self.ser = Net('SER')           # Serial data input
        self.srclk = Net('SRCLK')       # Shift register clock
        self.rclk = Net('RCLK')         # Storage register clock
        self.srclr = Net('SRCLR')       # Shift register clear (active low)
        self.oe = Net('OE')             # Output enable (active low)
        
        # 8-bit parallel outputs (to TX switches and MUX)
        self.outputs = [Net(f'SR_Q{i}') for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']]
        
        # Connect power
        self.vcc += self.sr['VCC']
        self.gnd += self.sr['GND']
        
        # Connect control signals
        self.ser += self.sr['SER']
        self.srclk += self.sr['SRCLK']
        self.rclk += self.sr['RCLK']
        self.srclr += self.sr['~{SRCLR}']
        self.oe += self.sr['~{OE}']
        
        # Connect outputs (QA-QH)
        output_pins = ['QA', 'QB', 'QC', 'QD', 'QE', 'QF', 'QG', 'QH']
        for pin, output in zip(output_pins, self.outputs):
            output += self.sr[pin]
        
        # Cascade output (optional chaining)
        self.qh_prime = Net('QH_PRIME')
        self.qh_prime += self.sr["QH'"]
        
        self.finalize()


# ============================================================================
# ANALOG MUX MODULE (CD4051B)
# ============================================================================

class AnalogMUX(SubCircuit):
    """CD4051B 8-channel analog multiplexer"""
    
    def __init__(self, name='MUX_A'):
        self.initialize()
        self.name = name
        
        # Power (analog ±5V or single 5V)
        self.vdd = Net('5V')
        self.vee = Net('VEE')           # Negative supply (or GND for single supply)
        self.vss = Net('GND')
        
        # CD4051B (SOIC-16)
        self.mux = Part('Analog_Switch', 'CD4051B', footprint='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm')
        
        # 8 analog inputs (from TX switches or receive channels)
        self.inputs = [Net(f'{name}_IN{i}') for i in range(8)]
        
        # Common output
        self.output = Net(f'{name}_OUT')
        
        # Address select lines (from shift register or MCU)
        self.addr_a = Net(f'{name}_A')   # LSB
        self.addr_b = Net(f'{name}_B')
        self.addr_c = Net(f'{name}_C')   # MSB
        
        # Inhibit (active high = disable)
        self.inhibit = Net(f'{name}_INH')
        
        # Connect power
        self.vdd += self.mux['VDD']
        self.vee += self.mux['VEE']
        self.vss += self.mux['VSS']
        
        # Connect analog I/O
        for i, input_net in enumerate(self.inputs):
            input_net += self.mux[f'X{i}']
        self.output += self.mux['X']
        
        # Connect control
        self.addr_a += self.mux['A']
        self.addr_b += self.mux['B']
        self.addr_c += self.mux['C']
        self.inhibit += self.mux['INH']
        
        self.finalize()


# ============================================================================
# LNA MODULE (OPA690)
# ============================================================================

class LNA(SubCircuit):
    """OPA690 wideband op-amp for low-noise amplification"""
    
    def __init__(self, name='LNA_A', gain=10):
        self.initialize()
        self.name = name
        self.gain = gain
        
        # Power (±5V or single 5V)
        self.vcc = Net('5V')
        self.vee = Net('VEE')
        self.gnd = Net('GND')
        
        # OPA690 (or generic high-speed op-amp) - using OPA1641 as placeholder
        self.amp = Part('Amplifier_Operational', 'OPA1641', footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
        
        # Input/output
        self.input_pos = Net(f'{name}_IN+')
        self.input_neg = Net(f'{name}_IN-')
        self.output = Net(f'{name}_OUT')
        
        # Gain-setting resistors (non-inverting configuration)
        # Gain = 1 + Rf/Rg
        self.rg = Part('Device', 'R', value=f'{10e3/gain:.0f}', footprint='Resistor_SMD:R_0805_2012Metric')  # 1k for gain of 10
        self.rf = Part('Device', 'R', value='9k', footprint='Resistor_SMD:R_0805_2012Metric')  # 9k for gain of 10
        
        # Decoupling
        self.c_vcc = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_vee = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
        
        # Connect power
        self.vcc += self.amp['V+']
        self.vee += self.amp['V-']
        self.vcc & self.c_vcc & self.gnd
        self.vee & self.c_vee & self.gnd
        
        # Non-inverting amplifier configuration
        self.input_pos += self.amp['+']
        self.output += self.amp['~']  # Output pin
        self.input_neg += self.amp['-']
        
        # Power pins
        self.vcc += self.amp['V+']
        self.vee += self.amp['V-']
        
        # Feedback network: OUT → Rf → IN- → Rg → GND
        self.output & self.rf & self.input_neg & self.rg & self.gnd
        
        self.finalize()


# ============================================================================
# TX SWITCH MODULE
# ============================================================================

class TXSwitch(SubCircuit):
    """Individual TX channel switch (MOSFET or analog switch)"""
    
    def __init__(self, name='TX0'):
        self.initialize()
        self.name = name
        
        # Control signal (from shift register)
        self.enable = Net(f'{name}_EN')
        
        # Signal path
        self.input = Net(f'{name}_IN')
        self.output = Net(f'{name}_OUT')
        
        # Simple analog switch (could be MOSFET or dedicated switch IC)
        # Using a generic NMOS for TX switching
        self.sw = Part('Transistor_FET', 'Q_NMOS_GSD', footprint='Package_TO_SOT_SMD:SOT-23')
        
        # Pull-down resistor when off
        self.r_pd = Part('Device', 'R', value='10k', footprint='Resistor_SMD:R_0603_1608Metric')
        
        # Connect switch
        self.input += self.sw['D']
        self.output += self.sw['S']
        self.enable += self.sw['G']
        self.output & self.r_pd & Net('GND')
        
        self.finalize()


# ============================================================================
# TOP LEVEL - MUX/LNA BOARD
# ============================================================================

def main():
    """Generate netlist for TurboQuant MUX/LNA board"""
    
    # Instantiate subcircuits
    print("Building TurboQuant MUX/LNA board...")
    
    # Power section
    power = PowerSupplies()
    
    # Digital control (shift register)
    digital = DigitalControl()
    power.vout_5v += digital.vcc
    power.gnd += digital.gnd
    
    # Connect shift register control signals (would come from external MCU)
    # These would be defined at the top level or brought out to headers
    
    # Two 8-channel MUXes (for I/Q or dual-channel acquisition)
    mux_a = AnalogMUX('MUX_A')
    mux_b = AnalogMUX('MUX_B')
    
    for mux in [mux_a, mux_b]:
        power.vout_5v += mux.vdd
        power.vee += mux.vee  # Could be GND for single-supply
        power.gnd += mux.vss
    
    # Two LNAs (for I/Q channels)
    lna_a = LNA('LNA_A', gain=10)
    lna_b = LNA('LNA_B', gain=10)
    
    for lna in [lna_a, lna_b]:
        power.vout_5v += lna.vcc
        power.vee += lna.vee  # Could be GND or negative rail
        power.gnd += lna.gnd
    
    # Connect MUX outputs to LNA inputs
    mux_a.output += lna_a.input_pos
    mux_b.output += lna_b.input_pos
    
    # 8 TX switches (one per channel)
    tx_switches = [TXSwitch(f'TX{i}') for i in range(8)]
    
    # Connect TX switches to MUX inputs
    for i, tx_sw in enumerate(tx_switches):
        # TX switch output goes to both MUX A and MUX B inputs
        tx_sw.output += mux_a.inputs[i]
        tx_sw.output += mux_b.inputs[i]
        
        # Control signals from shift register
        # Using first 8 outputs of shift register for TX enables
        digital.outputs[i] += tx_sw.enable
    
    # MUX address lines (could come from MCU or shift register bits 4-6)
    # For now, leaving as external nets
    
    # ============================================================================
    # RED PITAYA INTERFACE
    # ============================================================================
    
    # 12V power input (external supply, not from Red Pitaya)
    vin_header = Part('Connector', 'Screw_Terminal_01x02', footprint='TerminalBlock:TerminalBlock_bornier-2_P5.08mm')
    power.vin_12v += vin_header['1']
    power.gnd += vin_header['2']
    
    # --- RED PITAYA E1 GPIO HEADER ---
    # Using two 1x10 connectors to represent the 2x10 E1 header
    rp_e1_odd = Part('Connector', 'Conn_01x10_Pin',  # Odd pins 1,3,5,7,9,11,13,15,17,19
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical')
    rp_e1_even = Part('Connector', 'Conn_01x10_Pin',  # Even pins 2,4,6,8,10,12,14,16,18,20
                      footprint='Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical')
    
    # E1 header pinout for Red Pitaya STEMlab 125-14
    # Pin  Odd (1,3,5...)  |  Pin  Even (2,4,6...)
    # ------------------------------------------------
    # 1    GND             |  2    +3.3V
    # 3    DIO0_P          |  4    DIO0_N (SER)
    # 5    DIO1_P          |  6    DIO1_N (SRCLK)
    # 7    DIO2_P          |  8    DIO2_N (RCLK)
    # 9    DIO3_P          |  10   DIO3_N (~OE)
    # 11   DIO4_P          |  12   DIO4_N (~SRCLR)
    # 13   DIO5_P          |  14   DIO5_N
    # 15   DIO6_P          |  16   DIO6_N
    # 17   DIO7_P          |  18   DIO7_N
    # 19   GND             |  20   GND
    
    # Connect shift register control signals to E1 header (even pins)
    digital.ser += rp_e1_even['2']      # Pin 4 - DIO0_N
    digital.srclk += rp_e1_even['3']    # Pin 6 - DIO1_N
    digital.rclk += rp_e1_even['4']     # Pin 8 - DIO2_N
    digital.oe += rp_e1_even['5']       # Pin 10 - DIO3_N (active low)
    digital.srclr += rp_e1_even['6']    # Pin 12 - DIO4_N (active low)
    
    # Power and ground
    power.vout_3v3 += rp_e1_even['1']   # Pin 2 - +3.3V
    power.gnd += rp_e1_odd['1']         # Pin 1 - GND
    power.gnd += rp_e1_odd['10']        # Pin 19 - GND
    power.gnd += rp_e1_even['10']       # Pin 20 - GND
    
    # Unused GPIO pins (available for MUX address or other control)
    # DIO5, DIO6, DIO7 available on pins 13-18
    
    # --- RED PITAYA ANALOG INTERFACE (SMA) ---
    
    # TX Input: From Red Pitaya DAC to board TX switches
    # This is the excitation signal that gets routed to selected TX channel
    rp_tx_in = Part('Connector', 'Conn_Coaxial', 
                    footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical')
    rp_tx_in_net = Net('RP_TX_IN')  # Signal from Red Pitaya DAC
    rp_tx_in_net += rp_tx_in['1']
    power.gnd += rp_tx_in['2']
    
    # Connect Red Pitaya TX input to all TX switches (routed through switches to transducers)
    # Note: In actual implementation, TX switches route this signal to 8 different outputs
    # For this design, we connect TX_IN to the switch inputs
    for tx_sw in tx_switches:
        rp_tx_in_net += tx_sw.input  # Each switch can route TX_IN to its output
    
    # RX0 Output: LNA_A → Red Pitaya ADC0
    rp_rx0_out = Part('Connector', 'Conn_Coaxial',
                      footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical')
    lna_a.output += rp_rx0_out['1']
    power.gnd += rp_rx0_out['2']
    
    # RX1 Output: LNA_B → Red Pitaya ADC1
    rp_rx1_out = Part('Connector', 'Conn_Coaxial',
                      footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical')
    lna_b.output += rp_rx1_out['1']
    power.gnd += rp_rx1_out['2']
    
    # Optional: External control header (for testing without Red Pitaya)
    # 6-pin header mirroring the E1 control signals
    ext_ctrl_header = Part('Connector', 'Conn_01x06_Pin', 
                           footprint='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
    digital.ser += ext_ctrl_header['1']
    digital.srclk += ext_ctrl_header['2']
    digital.rclk += ext_ctrl_header['3']
    digital.srclr += ext_ctrl_header['4']
    digital.oe += ext_ctrl_header['5']
    power.gnd += ext_ctrl_header['6']
    
    # ERC and netlist generation
    print("Running ERC...")
    ERC()
    
    print("Generating KiCad netlist...")
    generate_netlist(tool=KICAD9, file_='turboquant_mux_lna.net')
    
    # Note: Schematic generation is disabled due to routing complexity
    # The netlist can be imported into KiCad for manual schematic/layout
    print("\nDone! Generated files:")
    print("  - turboquant_mux_lna.net (KiCad netlist)")
    print("\nTo use: Import the netlist into KiCad for PCB layout")
    print("Red Pitaya interface included:")
    print("  - E1 GPIO header (2x10): Digital control (SER, SRCLK, RCLK, OE, SRCLR)")
    print("  - SMA TX_IN: From Red Pitaya DAC")
    print("  - SMA RX0_OUT: To Red Pitaya ADC0")
    print("  - SMA RX1_OUT: To Red Pitaya ADC1")


if __name__ == '__main__':
    main()
