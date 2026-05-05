from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

turboquant_mux_lna_skidl = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Polyfuse', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Polyfuse'}), 'ref_prefix':'F', 'fplist':[''], 'footprint':'Fuse:Fuse_1206_3216Metric', 'keywords':'resettable fuse PTC PPTC polyfuse polyswitch', 'description':'Resettable fuse, polymeric positive temperature coefficient', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D_Schottky', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D_Schottky'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'Diode_SMD:D_SOD-123', 'keywords':'diode Schottky', 'description':'Schottky diode', 'datasheet':'~', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LM7805_TO220', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LM7805_TO220'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_THT:TO-220-3_Vertical'], 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':'Voltage Regulator 1A Positive', 'description':'Positive 1A 35V Linear Regulator, Fixed Output 5V, TO-220', 'datasheet':'https://www.onsemi.cn/PowerSolutions/document/MC7800-D.PDF', 'pins':[
            Pin(num='1',name='VI',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='VO',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'AMS1117-3.3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'AMS1117-3.3'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'linear regulator ldo fixed positive', 'description':'1A Low Dropout regulator, positive, 3.3V fixed output, SOT-223', 'datasheet':'http://www.advanced-monolithic.com/pdf/ds1117.pdf', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='VO',func=pin_types.PWROUT,unit=1),
            Pin(num='3',name='VI',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_SMD:C_0805_2012Metric', 'keywords':'cap capacitor', 'description':'Unpolarized capacitor', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'74HC595', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'74HC595'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', 'keywords':'HCMOS SR 3State', 'description':'8-bit serial in/out Shift Register 3-State Outputs', 'datasheet':'http://www.ti.com/lit/ds/symlink/sn74hc595.pdf', 'pins':[
            Pin(num='14',name='SER',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='SRCLK',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='~{SRCLR}',func=pin_types.INPUT,unit=1),
            Pin(num='12',name='RCLK',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='~{OE}',func=pin_types.INPUT,unit=1),
            Pin(num='16',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='15',name='QA',func=pin_types.TRISTATE,unit=1),
            Pin(num='1',name='QB',func=pin_types.TRISTATE,unit=1),
            Pin(num='2',name='QC',func=pin_types.TRISTATE,unit=1),
            Pin(num='3',name='QD',func=pin_types.TRISTATE,unit=1),
            Pin(num='4',name='QE',func=pin_types.TRISTATE,unit=1),
            Pin(num='5',name='QF',func=pin_types.TRISTATE,unit=1),
            Pin(num='6',name='QG',func=pin_types.TRISTATE,unit=1),
            Pin(num='7',name='QH',func=pin_types.TRISTATE,unit=1),
            Pin(num='9',name="QH'",func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'CD4051B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CD4051B'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', 'keywords':'analog switch selector multiplexer', 'description':'CMOS single 8-channel analog multiplexer demultiplexer, TSSOP-16/DIP-16/SOIC-16', 'datasheet':'http://www.ti.com/lit/ds/symlink/cd4052b.pdf', 'pins':[
            Pin(num='11',name='A',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='C',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='X',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='INH',func=pin_types.INPUT,unit=1),
            Pin(num='7',name='VEE',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='VSS',func=pin_types.PWRIN,unit=1),
            Pin(num='16',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='13',name='X0',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='X1',func=pin_types.BIDIR,unit=1),
            Pin(num='15',name='X2',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='X3',func=pin_types.BIDIR,unit=1),
            Pin(num='1',name='X4',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='X5',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='X6',func=pin_types.BIDIR,unit=1),
            Pin(num='4',name='X7',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'OPA1641', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'OPA1641'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'keywords':'single opamp', 'description':' JFET input, ultralow distortion, low-noise operational amplifier, SOIC-8/VSSOP-8', 'datasheet':'http://www.ti.com/lit/ds/symlink/opa1641.pdf', 'pins':[
            Pin(num='1',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='2',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='6',name='~',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='8',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':'R res resistor', 'description':'Resistor', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Q_NMOS_GSD', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Q_NMOS_GSD'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':'transistor NMOS N-MOS N-MOSFET', 'description':'N-MOSFET transistor, gate/source/drain', 'datasheet':'~', 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='S',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Screw_Terminal_01x02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Screw_Terminal_01x02'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'TerminalBlock:TerminalBlock_bornier-2_P5.08mm', 'keywords':'screw terminal', 'description':'Generic screw terminal, single row, 01x02, script generated (kicad-library-utils/schlib/autogen/connector/)', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x10_Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x10_Pin'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x10, script generated', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='10',name='Pin_10',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Pin_5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Pin_6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='Pin_7',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='Pin_8',func=pin_types.PASSIVE,unit=1),
            Pin(num='9',name='Pin_9',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_Coaxial', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_Coaxial'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_Coaxial:SMA_Amphenol_132134-11_Vertical', 'keywords':'BNC SMA SMB SMC LEMO coaxial connector CINCH RCA MCX MMCX U.FL UMRF', 'description':'coaxial connector (BNC, SMA, SMB, SMC, Cinch/RCA, LEMO, ...)', 'datasheet':' ~', 'pins':[
            Pin(num='1',name='In',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Ext',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x06_Pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x06_Pin'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 'keywords':'connector', 'description':'Generic connector, single row, 01x06, script generated', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Pin_5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Pin_6',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])