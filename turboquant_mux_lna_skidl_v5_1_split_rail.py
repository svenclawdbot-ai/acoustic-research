#!/usr/bin/env python3
"""
TurboQuant MUX/LNA Board v5.1 - Split Rail Power Supply

KEY CHANGE: Separate analog and digital power supplies for noise isolation

Power Architecture:
  12V_IN
     ├──► LM7805 (5V_DIG) ──► Digital section (74HCT595, control)
     │                         [Noisy, switching transients OK]
     │
     └──► LC Filter ──► AMS1115-5.0 (5V_ANA) ──► Analog section (MUX, LNA)
                         [Clean, low noise, critical for signal quality]

Additional filtering:
  - Ferrite beads between 5V_DIG and 5V_ANA
  - Separate ground planes (star grounding at power entry)
  - Heavy decoupling on analog supplies

This prevents digital switching noise from coupling into sensitive analog signals.
"""

from skidl import *

# ============================================================================
# SPLIT RAIL POWER SUPPLIES MODULE
# ============================================================================

class PowerSupplies_SplitRail(SubCircuit):
    """
    Split rail power supply: Separate analog and digital 5V
    
    12V ──► Fuse ──► TVS ──┬──► LM7805 ──► 5V_DIG (digital)
                          │
                          └──► LC Filter ──► AMS1117-5.0 ──► 5V_ANA (analog)
                          
    Plus: 5V_ANA ──► AMS1117-3.3 ──► 3.3V (for external MCU if needed)
    
    Key features:
    - Separate regulators prevent digital noise coupling to analog
    - LC filter on analog rail for additional ripple rejection
    - Ferrite bead isolation between domains
    - Star grounding at power entry
    """
    
    def __init__(self):
        self.initialize()
        
        # Input: 12V screw terminal
        self.vin_12v = Net('12V_IN')
        self.gnd = Net('GND')
        
        # Protection components
        self.fuse = Part('Device', 'Polyfuse', value='2A', 
                        footprint='Fuse:Fuse_1206_3216Metric')
        self.d_protection = Part('Device', 'D_Schottky', value='SS34',
                                footprint='Diode_SMD:D_SMA')
        self.tvs = Part('Device', 'D_TVS', value='SMAJ15A',
                       footprint='Diode_SMD:D_SMA')
        
        # ============================================================================
        # DIGITAL SUPPLY (5V_DIG) - LM7805, handles switching noise
        # ============================================================================
        
        self.reg_5v_dig = Part('Regulator_Linear', 'LM7805_TO220',
                              footprint='Package_TO_SOT_SMD:TO-252-2')
        
        # Digital 5V bulk caps
        self.c_dig_in = Part('Device', 'C_Polarized', value='100uF/25V',
                            footprint='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
        self.c_dig_out = Part('Device', 'C', value='10uF',
                             footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_dig_100n = Part('Device', 'C', value='100nF',
                              footprint='Capacitor_SMD:C_0805_2012Metric')
        
        # ============================================================================
        # LC FILTER for analog supply
        # Filters switching noise before analog regulator
        # ============================================================================
        
        # Inductor: 10µH, 1A, low DCR
        self.lc_inductor = Part('Device', 'L', value='10uH',
                               footprint='Inductor_SMD:L_1210_3225Metric')
        
        # LC filter capacitor
        self.lc_cap = Part('Device', 'C', value='100uF',
                          footprint='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
        
        # ============================================================================
        # ANALOG SUPPLY (5V_ANA) - Separate LDO for clean power
        # ============================================================================
        
        # Using AMS1117-5.0 for analog (low noise, good PSRR)
        self.reg_5v_ana = Part('Regulator_Linear', 'AMS1117-5.0',
                              footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
        
        # Heavy filtering on analog supply
        self.c_ana_in = Part('Device', 'C', value='22uF',
                            footprint='Capacitor_SMD:C_1206_3216Metric')
        self.c_ana_out = Part('Device', 'C', value='22uF',
                             footprint='Capacitor_SMD:C_1206_3216Metric')
        self.c_ana_100n = Part('Device', 'C', value='100nF',
                              footprint='Capacitor_SMD:C_0603_1608Metric')
        
        # Additional RC filter for ultra-clean analog supply
        self.r_ana_filter = Part('Device', 'R', value='10',
                                footprint='Resistor_SMD:R_1206_3216Metric')
        self.c_ana_filter = Part('Device', 'C', value='10uF',
                                footprint='Capacitor_SMD:C_0805_2012Metric')
        
        # ============================================================================
        # 3.3V SUPPLY (for external MCU/ESP32)
        # ============================================================================
        
        self.reg_3v3 = Part('Regulator_Linear', 'AMS1117-3.3',
                           footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
        
        self.c_3v3_in = Part('Device', 'C', value='10uF',
                            footprint='Capacitor_SMD:C_0805_2012Metric')
        self.c_3v3_out = Part('Device', 'C', value='10uF',
                             footprint='Capacitor_SMD:C_0805_2012Metric')
        
        # ============================================================================
        # ISOLATION COMPONENTS
        # ============================================================================
        
        # Ferrite bead between digital and analog grounds (optional)
        # Only populate if noise issues observed
        self.fb_gnd = Part('Device', 'FerriteBead', value='600R@100MHz',
                          footprint='Inductor_SMD:L_0805_2012Metric')
        
        # ============================================================================
        # CONNECTIONS
        # ============================================================================
        
        # Input protection
        self.vin_12v & self.fuse & self.d_protection['A,K']
        self.d_protection['K'] & self.tvs['A1']
        self.tvs['A2'] & self.gnd
        
        vin_node = self.d_protection['K']  # Protected 12V node
        
        # Digital regulator (LM7805)
        vin_node & self.c_dig_in & self.gnd
        vin_node += self.reg_5v_dig['VI']
        self.gnd += self.reg_5v_dig['GND']
        
        self.vout_5v_dig = Net('5V_DIG')
        self.vout_5v_dig += self.reg_5v_dig['VO']
        # Note: DPAK tab connected via footprint copper pour
        self.vout_5v_dig & self.c_dig_out & self.gnd
        self.vout_5v_dig & self.c_dig_100n & self.gnd
        
        # LC filter for analog supply (filters switching noise)
        vin_node & self.lc_inductor & self.lc_cap & self.gnd
        vin_filtered = self.lc_inductor[2]  # After inductor
        
        # Analog regulator (AMS1117-5.0)
        vin_filtered & self.c_ana_in & self.gnd
        vin_filtered += self.reg_5v_ana['VI']
        self.gnd += self.reg_5v_ana['GND']
        
        self.vout_5v_ana = Net('5V_ANA')
        self.vout_5v_ana += self.reg_5v_ana['VO']
        self.vout_5v_ana & self.c_ana_out & self.gnd
        self.vout_5v_ana & self.c_ana_100n & self.gnd
        
        # Additional RC filter on analog supply (optional but recommended)
        self.vout_5v_ana & self.r_ana_filter & self.c_ana_filter & self.gnd
        self.vout_5v_ana_clean = self.c_ana_filter[1]  # Clean analog 5V
        
        # 3.3V regulator (from analog 5V for clean 3.3V)
        self.vout_5v_ana += self.reg_3v3['VI']
        self.gnd += self.reg_3v3['GND']
        
        self.vout_3v3 = Net('3V3')
        self.vout_3v3 += self.reg_3v3['VO']
        self.vout_3v3 & self.c_3v3_in & self.gnd
        self.vout_3v3 & self.c_3v3_out & self.gnd
        
        self.finalize()


# ============================================================================
# DIGITAL CONTROL - Powered from 5V_DIG
# ============================================================================

class DigitalControl(SubCircuit):
    """74HCT595 shift register - powered from digital 5V"""
    
    def __init__(self):
        self.initialize()
        
        self.vcc = Net('5V_DIG')  # Digital supply
        self.gnd = Net('GND')
        
        self.sr = Part('74xx', '74HCT595',
                      footprint='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm')
        
        self.ser = Net('SER')
        self.srclk = Net('SRCLK')
        self.rclk = Net('RCLK')
        self.srclr = Net('SRCLR')
        self.oe = Net('OE')
        
        self.outputs = [Net(f'SR_Q{i}') for i in range(8)]
        
        self.vcc += self.sr['VCC']
        self.gnd += self.sr['GND']
        
        self.ser += self.sr['SER']
        self.srclk += self.sr['SRCLK']
        self.rclk += self.sr['RCLK']
        self.srclr += self.sr['~{SRCLR}']
        self.oe += self.sr['~{OE}']
        
        for pin, output in zip(['QA', 'QB', 'QC', 'QD', 'QE', 'QF', 'QG', 'QH'], self.outputs):
            output += self.sr[pin]
        
        self.qh_prime = Net('QH_PRIME')
        self.qh_prime += self.sr["QH'"]
        
        # Decoupling on digital supply
        self.c_vcc = Part('Device', 'C', value='100nF',
                         footprint='Capacitor_SMD:C_0603_1608Metric')
        self.vcc & self.c_vcc & self.gnd
        
        self.finalize()


# ============================================================================
# ANALOG MUX - Powered from 5V_ANA (clean supply)
# ============================================================================

class AnalogMUX_HV(SubCircuit):
    """DG408 100V MUX - powered from clean analog supply"""
    
    def __init__(self, name='MUX_A'):
        self.initialize()
        self.name = name
        
        # Analog supplies (clean)
        self.vdd = Net(f'{name}_VDD')   # HV analog supply (12V or 100V)
        self.vss = Net(f'{name}_VSS')   # Analog ground
        self.vl = Net('5V_ANA')         # LOGIC supply (clean 5V from analog rail)
        self.gnd = Net('GND')
        
        self.mux = Part('Analog_Switch', 'DG408',
                       footprint='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm')
        
        self.inputs = [Net(f'{name}_IN{i}') for i in range(8)]
        self.output = Net(f'{name}_OUT')
        
        self.addr_a = Net(f'{name}_A')
        self.addr_b = Net(f'{name}_B')
        self.addr_c = Net(f'{name}_C')
        self.enable = Net(f'{name}_EN')
        
        self.vdd += self.mux['V+']
        self.vss += self.mux['V-']
        self.vl += self.mux['VL']
        self.gnd += self.mux['GND']
        
        for i, input_net in enumerate(self.inputs):
            input_net += self.mux[f'X{i}']
        self.output += self.mux['X']
        
        self.addr_a += self.mux['A']
        self.addr_b += self.mux['B']
        self.addr_c += self.mux['C']
        self.enable += self.mux['EN']
        
        # Pull-downs with clean analog reference
        for addr in [self.addr_a, self.addr_b, self.addr_c]:
            r_pd = Part('Device', 'R', value='10k',
                       footprint='Resistor_SMD:R_0603_1608Metric')
            addr & r_pd & self.gnd
        
        r_en_pd = Part('Device', 'R', value='10k',
                      footprint='Resistor_SMD:R_0603_1608Metric')
        self.enable & r_en_pd & self.gnd
        
        # Decoupling on analog logic supply
        self.c_vl = Part('Device', 'C', value='100nF',
                        footprint='Capacitor_SMD:C_0603_1608Metric')
        self.vl & self.c_vl & self.gnd
        
        self.finalize()


# ============================================================================
# LNA - Powered from 5V_ANA (clean supply)
# ============================================================================

class LNA(SubCircuit):
    """OPA1641 LNA - powered from clean analog supply"""
    
    def __init__(self, name='LNA_A', gain=10):
        self.initialize()
        self.name = name
        self.gain = gain
        
        # Clean analog supply
        self.vcc = Net('5V_ANA_CLEAN')  # After RC filter
        self.vee = Net('GND')
        
        self.amp = Part('Amplifier_Operational', 'OPA1641',
                       footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
        
        self.input_pos = Net(f'{name}_IN+')
        self.input_neg = Net(f'{name}_IN-')
        self.output = Net(f'{name}_OUT')
        
        self.rg = Part('Device', 'R', value='1k',
                      footprint='Resistor_SMD:R_0805_2012Metric')
        self.rf = Part('Device', 'R', value='9.09k',
                      footprint='Resistor_SMD:R_0805_2012Metric')
        
        # Heavy decoupling on clean analog supply
        self.c_vcc_100n = Part('Device', 'C', value='100nF',
                              footprint='Capacitor_SMD:C_0603_1608Metric')
        self.c_vcc_10u = Part('Device', 'C', value='10uF',
                             footprint='Capacitor_SMD:C_0805_2012Metric')
        
        self.vcc += self.amp['V+']
        self.vee += self.amp['V-']
        
        # Power decoupling
        self.vcc & self.c_vcc_100n & self.vee
        self.vcc & self.c_vcc_10u & self.vee
        
        # Amplifier configuration
        self.input_pos += self.amp['+']
        self.output += self.amp['~']
        self.input_neg += self.amp['-']
        
        self.output & self.rf & self.input_neg & self.rg & self.vee
        
        self.finalize()


# ============================================================================
# TX SWITCH - Gate drive from 5V_DIG, drain at HV
# ============================================================================

class TXSwitch_HV(SubCircuit):
    """High-voltage TX switch"""
    
    def __init__(self, name='TX0'):
        self.initialize()
        self.name = name
        
        self.enable = Net(f'{name}_EN')
        self.input = Net(f'{name}_IN')
        self.output = Net(f'{name}_OUT')
        
        # HV MOSFET
        self.mosfet = Part('Transistor_FET', 'Q_NMOS_GDS',
                          footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
        
        # Gate protection
        self.r_gate = Part('Device', 'R', value='100',
                          footprint='Resistor_SMD:R_0603_1608Metric')
        self.zener_gate = Part('Device', 'D_Zener', value='BZX84C12',
                              footprint='Diode_SMD:D_SOD-323')
        self.r_pd = Part('Device', 'R', value='10k',
                        footprint='Resistor_SMD:R_0603_1608Metric')
        
        self.enable & self.r_gate & self.mosfet['G']
        self.mosfet['G'] & self.zener_gate['K']
        self.zener_gate['A'] & self.gnd
        self.mosfet['G'] & self.r_pd & self.gnd
        
        self.gnd += self.mosfet['S']
        self.output += self.mosfet['D']
        
        self.r_series = Part('Device', 'R', value='1k',
                            footprint='Resistor_SMD:R_1206_3216Metric')
        self.input & self.r_series & self.output
        
        self.finalize()


# ============================================================================
# TOP LEVEL - SPLIT RAIL DESIGN
# ============================================================================

def main():
    """Generate netlist for TurboQuant v5.1 with split rail power"""
    
    print("Building TurboQuant MUX/LNA board v5.1 (Split Rail)...")
    print("\nPOWER ARCHITECTURE:")
    print("  12V_IN")
    print("    ├──► LM7805 ──► 5V_DIG (digital, noisy OK)")
    print("    │")
    print("    └──► LC Filter ──► AMS1117-5.0 ──► 5V_ANA (analog, clean)")
    print("                           └──► AMS1117-3.3 ──► 3.3V")
    print("\nThis prevents digital switching noise from coupling to analog signals.")
    
    # Power supplies (split rail)
    power = PowerSupplies_SplitRail()
    
    # Digital section - use 5V_DIG
    digital = DigitalControl()
    power.vout_5v_dig += digital.vcc
    power.gnd += digital.gnd
    
    # Analog section - use 5V_ANA
    mux_a = AnalogMUX_HV('MUX_A')
    mux_b = AnalogMUX_HV('MUX_B')
    
    for mux in [mux_a, mux_b]:
        power.vin_12v += mux.vdd  # HV supply
        power.gnd += mux.vss
        power.vout_5v_ana += mux.vl  # Clean logic supply
        power.gnd += mux.gnd
    
    # LNAs - use clean 5V after RC filter
    lna_a = LNA('LNA_A', gain=10)
    lna_b = LNA('LNA_B', gain=10)
    
    for lna in [lna_a, lna_b]:
        power.vout_5v_ana_clean += lna.vcc
        power.gnd += lna.vee
    
    # Connect MUX to LNA
    mux_a.output += lna_a.input_pos
    mux_b.output += lna_b.input_pos
    
    # TX switches
    tx_switches = [TXSwitch_HV(f'TX{i}') for i in range(8)]
    
    for i, tx_sw in enumerate(tx_switches):
        tx_sw.output += mux_a.inputs[i]
        tx_sw.output += mux_b.inputs[i]
        digital.outputs[i] += tx_sw.enable
    
    # MUX addressing
    digital.outputs[4] += mux_a.addr_a
    digital.outputs[5] += mux_a.addr_b
    digital.outputs[6] += mux_a.addr_c
    digital.outputs[4] += mux_b.addr_a
    digital.outputs[5] += mux_b.addr_b
    digital.outputs[6] += mux_b.addr_c
    digital.outputs[7] += mux_a.enable
    
    # Connectors
    vin_header = Part('Connector', 'Screw_Terminal_01x02',
                     footprint='TerminalBlock:TerminalBlock_bornier-2_P5.08mm')
    power.vin_12v += vin_header['1']
    power.gnd += vin_header['2']
    
    ctrl_header = Part('Connector', 'Conn_01x06_Pin',
                      footprint='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
    digital.ser += ctrl_header['1']
    digital.srclk += ctrl_header['2']
    digital.rclk += ctrl_header['3']
    digital.srclr += ctrl_header['4']
    digital.oe += ctrl_header['5']
    power.gnd += ctrl_header['6']
    
    v33_header = Part('Connector', 'Conn_01x02_Pin',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    power.vout_3v3 += v33_header['1']
    power.gnd += v33_header['2']
    
    # Output SMAs
    for lna, name in [(lna_a, 'RX0'), (lna_b, 'RX1')]:
        sma = Part('Connector', 'Conn_Coaxial',
                  footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical')
        lna.output += sma['1']
        power.gnd += sma['2']
    
    tx_in_sma = Part('Connector', 'Conn_Coaxial',
                    footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical')
    tx_in_net = Net('TX_IN')
    tx_in_net += tx_in_sma['1']
    power.gnd += tx_in_sma['2']
    
    for tx_sw in tx_switches:
        tx_sw.input += tx_in_net
    
    for i in range(8):
        sma = Part('Connector', 'Conn_Coaxial',
                  footprint='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical',
                  ref=f'TX{i}')
        tx_switches[i].output += sma['1']
        power.gnd += sma['2']
    
    # Generate netlist
    print("\nRunning ERC...")
    ERC()
    
    print("Generating KiCad netlist...")
    generate_netlist(tool=KICAD9, file_='turboquant_mux_lna_v5_1_split_rail.net')
    
    print("\n" + "="*60)
    print("TurboQuant v5.1 Split Rail Summary")
    print("="*60)
    print("\nPower Supplies:")
    print("  • 5V_DIG  - Digital section (74HCT595, control)")
    print("  • 5V_ANA  - Analog section (MUX, LNA) - CLEAN")
    print("  • 3.3V    - External MCU power")
    print("\nNoise Isolation:")
    print("  • Separate regulators")
    print("  • LC filter on analog input")
    print("  • RC filter on clean 5V")
    print("  • Heavy decoupling on analog supplies")
    print("\nGenerated: turboquant_mux_lna_v5_1_split_rail.net")
    print("="*60)


if __name__ == '__main__':
    main()
