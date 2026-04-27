#!/usr/bin/env python3
"""Generate icarus-v2.kicad_sym — custom symbol library for Icarus v2.0 modular compute platform."""

import uuid

def uid():
    return str(uuid.uuid4())

def pin_block(pin_type, direction, x, y, angle, length, name, number):
    """Generate a KiCad 10 pin s-expression."""
    return f"""\t\t\t(pin {pin_type} line
\t\t\t\t(at {x} {y} {angle})
\t\t\t\t(length {length})
\t\t\t\t(name "{name}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "{number}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)"""

def property_block(key, value, x, y, hide=False, font_size=1.27):
    hide_str = "\n\t\t\t(hide yes)" if hide else ""
    return f"""\t\t(property "{key}" "{value}"
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no){hide_str}
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size {font_size} {font_size})
\t\t\t\t)
\t\t\t)
\t\t)"""

def symbol_header(name, ref, value, description, keywords, footprint="", fp_filters="", pin_names_hide=False, pin_names_offset=1.016):
    hide_pin = "\n\t\t\t(hide yes)" if pin_names_hide else ""
    fp_filter_block = ""
    if fp_filters:
        fp_filter_block = f"""\n\t\t(property "ki_fp_filters" "{fp_filters}"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)"""
    return f"""\t(symbol "{name}"
\t\t(pin_names
\t\t\t(offset {pin_names_offset}){hide_pin}
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
{property_block("Reference", ref, 0, 2.54, font_size=1.27)}
{property_block("Value", value, 0, -2.54, font_size=1.27)}
{property_block("Footprint", footprint, 0, 0, hide=True)}
{property_block("Datasheet", "", 0, 0, hide=True)}
{property_block("Description", description, 0, 0, hide=True)}
\t\t(property "ki_keywords" "{keywords}"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t){fp_filter_block}"""


def gen_bus_40pin():
    """Generate the Icarus_Bus_40pin symbol — 40-pin 2x20 stacking bus connector."""
    # Pin mapping: (pin_number, signal_name, pin_type)
    # Odd pins on left (angle=0), even pins on right (angle=180)
    pins = [
        (1, "3V3", "power_in"),     (2, "5V", "power_in"),
        (3, "3V3", "power_in"),     (4, "5V", "power_in"),
        (5, "GND", "power_in"),     (6, "GND", "power_in"),
        (7, "GND", "power_in"),     (8, "GND", "power_in"),
        (9, "SPI_CLK", "bidirectional"),   (10, "SPI_MOSI", "bidirectional"),
        (11, "SPI_MISO", "bidirectional"), (12, "SPI_CS0", "bidirectional"),
        (13, "SPI_CS1", "bidirectional"),  (14, "SPI_CS2", "bidirectional"),
        (15, "I2C_SDA", "bidirectional"),  (16, "I2C_SCL", "bidirectional"),
        (17, "I2C2_SDA", "bidirectional"), (18, "I2C2_SCL", "bidirectional"),
        (19, "UART_TX", "bidirectional"),  (20, "UART_RX", "bidirectional"),
        (21, "UART2_TX", "bidirectional"), (22, "UART2_RX", "bidirectional"),
        (23, "USB_D+", "bidirectional"),   (24, "USB_D-", "bidirectional"),
        (25, "USB3_TX+", "bidirectional"), (26, "USB3_TX-", "bidirectional"),
        (27, "USB3_RX+", "bidirectional"), (28, "USB3_RX-", "bidirectional"),
        (29, "INT0", "bidirectional"),     (30, "INT1", "bidirectional"),
        (31, "INT2", "bidirectional"),     (32, "RESET_N", "bidirectional"),
        (33, "I2S_BCLK", "bidirectional"), (34, "I2S_LRCLK", "bidirectional"),
        (35, "I2S_DIN", "bidirectional"),  (36, "I2S_DOUT", "bidirectional"),
        (37, "GPIO_A", "bidirectional"),   (38, "GPIO_B", "bidirectional"),
        (39, "GND", "power_in"),           (40, "GND", "power_in"),
    ]

    # 20 rows, 2.54mm pitch. Top y = 24.13, bottom y = -24.13
    # Body rectangle from -1.27 to 15.24 (wider to accommodate signal names)
    body_left = -1.27
    body_right = 16.51
    n_rows = 20
    top_y = (n_rows - 1) * 2.54 / 2  # 24.13

    lines = []
    lines.append(symbol_header(
        "Icarus_Bus_40pin", "J", "Icarus_Bus_40pin",
        "Icarus v2.0 40-pin stacking bus connector (2x20, 0.1 inch pitch)",
        "connector bus stacking 40pin icarus",
        footprint="Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical",
        fp_filters="Connector*:*_2x20_*"
    ))

    # Sub-symbol with body and pins
    lines.append(f"\t\t(symbol \"Icarus_Bus_40pin_1_1\"")

    # Body rectangle
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start {body_left} {top_y + 1.27})
\t\t\t\t(end {body_right} {-top_y - 1.27})
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)""")

    # Generate pins
    for num, name, ptype in pins:
        row = (num - 1) // 2  # 0-19
        y = top_y - row * 2.54

        if num % 2 == 1:  # Odd = left side
            x = body_left - 3.81
            angle = 0
        else:  # Even = right side
            x = body_right + 3.81
            angle = 180

        lines.append(pin_block(ptype, "line", x, y, angle, 3.81, name, str(num)))

    lines.append("\t\t)")  # close sub-symbol
    lines.append("\t)")  # close symbol
    return "\n".join(lines)


def gen_simple_ic(name, ref, description, keywords, footprint, fp_filters, pins_left, pins_right, body_width=10.16):
    """Generate a simple IC symbol with pins on left and right.

    pins_left/right: list of (number, name, type) from top to bottom
    """
    n_pins = max(len(pins_left), len(pins_right))
    top_y = (n_pins - 1) * 2.54 / 2
    body_half = body_width / 2

    lines = []
    lines.append(symbol_header(name, ref, name, description, keywords, footprint, fp_filters))
    lines.append(f"\t\t(symbol \"{name}_1_1\"")

    # Body rectangle
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start {-body_half} {top_y + 1.27})
\t\t\t\t(end {body_half} {-top_y - 1.27})
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)""")

    # Left pins
    for i, (num, pname, ptype) in enumerate(pins_left):
        y = top_y - i * 2.54
        lines.append(pin_block(ptype, "line", -body_half - 3.81, y, 0, 3.81, pname, str(num)))

    # Right pins
    for i, (num, pname, ptype) in enumerate(pins_right):
        y = top_y - i * 2.54
        lines.append(pin_block(ptype, "line", body_half + 3.81, y, 180, 3.81, pname, str(num)))

    lines.append("\t\t)")
    lines.append("\t)")
    return "\n".join(lines)


def gen_grove_i2c():
    return gen_simple_ic(
        "Grove_I2C", "J",
        "Grove I2C connector (4-pin, Seeed Studio standard)",
        "grove i2c connector seeed",
        "", "",
        pins_left=[
            (1, "SCL", "bidirectional"),
            (2, "SDA", "bidirectional"),
            (3, "VCC", "power_in"),
            (4, "GND", "power_in"),
        ],
        pins_right=[],
        body_width=7.62,
    )


def gen_fs8205a():
    return gen_simple_ic(
        "FS8205A", "Q",
        "Dual N-Channel MOSFET for lithium battery protection",
        "mosfet dual nmos battery protection",
        "Package_SO:TSSOP-8_4.4x3mm_P0.65mm", "",
        pins_left=[
            (1, "S1", "passive"),
            (2, "G1", "input"),
            (3, "S2", "passive"),
            (4, "G2", "input"),
        ],
        pins_right=[
            (5, "D", "passive"),
            (6, "D", "passive"),
            (7, "D", "passive"),
            (8, "D", "passive"),
        ],
        body_width=7.62,
    )


def gen_bh1750():
    return gen_simple_ic(
        "BH1750FVI", "U",
        "Digital ambient light sensor, I2C interface",
        "light sensor i2c ambient",
        "Package_DFN_QFN:WSOF-6_1.4x1.6mm_P0.5mm", "",
        pins_left=[
            (1, "VCC", "power_in"),
            (2, "ADDR", "input"),
            (3, "GND", "power_in"),
        ],
        pins_right=[
            (6, "DVI", "output"),
            (5, "SCL", "input"),
            (4, "SDA", "bidirectional"),
        ],
        body_width=7.62,
    )


def gen_tps63020():
    """TPS63020 buck-boost converter, QFN-14 (3x4mm)."""
    return gen_simple_ic(
        "TPS63020", "U",
        "High-efficiency single inductor buck-boost converter, 3.6A switch, QFN-14",
        "buck-boost converter dcdc ti tps63020",
        "Package_DFN_QFN:QFN-14-1EP_3x4mm_P0.5mm_EP1.78x2.38mm", "",
        pins_left=[
            (1, "VOUT", "power_out"),
            (2, "L2", "passive"),
            (3, "L1", "passive"),
            (4, "VIN", "power_in"),
            (5, "VINA", "power_in"),
            (6, "EN", "input"),
            (7, "PS/SYNC", "input"),
        ],
        pins_right=[
            (14, "FB", "input"),
            (13, "PG", "open_collector"),
            (12, "VOUT", "passive"),
            (11, "PGND", "power_in"),
            (10, "PGND", "power_in"),
            (9, "AGND", "power_in"),
            (8, "NC", "passive"),
        ],
        body_width=10.16,
    )


def gen_inmp441():
    """INMP441 MEMS microphone with I2S output."""
    return gen_simple_ic(
        "INMP441", "U",
        "High-performance omnidirectional MEMS microphone with I2S digital output",
        "mems microphone i2s inmp441 audio",
        "", "",
        pins_left=[
            (1, "VDD", "power_in"),
            (2, "GND", "power_in"),
            (3, "GND", "power_in"),
            (10, "L/R", "input"),
        ],
        pins_right=[
            (4, "WS", "input"),
            (5, "SCK", "input"),
            (6, "SD", "output"),
            (9, "GND", "power_in"),
        ],
        body_width=10.16,
    )


def gen_ov2640():
    """OV2640 camera module — 24-pin DVP interface."""
    return gen_simple_ic(
        "OV2640_Module", "U",
        "2MP CMOS camera module with DVP (parallel) and SCCB interface",
        "camera cmos ov2640 dvp sccb",
        "", "",
        pins_left=[
            (1, "3V3", "power_in"),
            (2, "GND", "power_in"),
            (3, "SCL", "input"),
            (4, "SDA", "bidirectional"),
            (5, "VSYNC", "output"),
            (6, "HREF", "output"),
            (7, "PCLK", "output"),
            (8, "XCLK", "input"),
            (9, "D7", "output"),
            (10, "D6", "output"),
            (11, "D5", "output"),
            (12, "D4", "output"),
        ],
        pins_right=[
            (13, "D3", "output"),
            (14, "D2", "output"),
            (15, "D1", "output"),
            (16, "D0", "output"),
            (17, "RESET", "input"),
            (18, "PWDN", "input"),
            (19, "NC", "passive"),
            (20, "NC", "passive"),
            (21, "NC", "passive"),
            (22, "NC", "passive"),
            (23, "NC", "passive"),
            (24, "GND", "power_in"),
        ],
        body_width=10.16,
    )


def gen_is66wvh8m8bll():
    """IS66WVH8M8BLL 64Mbit HyperRAM, BGA-24."""
    return gen_simple_ic(
        "IS66WVH8M8BLL", "U",
        "64Mbit (8MB) HyperRAM, HyperBus interface, BGA-24",
        "hyperram memory hyperbus issi",
        "Package_BGA:BGA-24_5.0x5.0mm_Layout4x6_P0.8mm", "",
        pins_left=[
            ("A1", "CK", "input"),
            ("A2", "CK#", "input"),
            ("A3", "CS#", "input"),
            ("A4", "RESET#", "input"),
            ("B1", "RWDS", "bidirectional"),
            ("B2", "VCC", "power_in"),
            ("B3", "VSS", "power_in"),
            ("B4", "VCCQ", "power_in"),
            ("C1", "DQ0", "bidirectional"),
            ("C2", "DQ1", "bidirectional"),
            ("C3", "VSSQ", "power_in"),
            ("C4", "DQ4", "bidirectional"),
        ],
        pins_right=[
            ("D1", "DQ2", "bidirectional"),
            ("D2", "DQ3", "bidirectional"),
            ("D3", "DQ5", "bidirectional"),
            ("D4", "DQ6", "bidirectional"),
            ("E1", "DQ7", "bidirectional"),
            ("E2", "VSS", "power_in"),
            ("E3", "VCCQ", "power_in"),
            ("E4", "NC", "passive"),
            ("F1", "NC", "passive"),
            ("F2", "NC", "passive"),
            ("F3", "PSC", "input"),
            ("F4", "NC", "passive"),
        ],
        body_width=12.7,
    )


def gen_tusb8020b():
    """TUSB8020B USB 3.0 2-port hub controller, QFP-64."""
    # Organized by function: power, USB upstream, USB downstream 1&2, config, misc
    left_pins = [
        # USB3 Upstream
        (1, "SSTXP_U", "output"),
        (2, "SSTXN_U", "output"),
        (3, "AVDD33_TX_U", "power_in"),
        (4, "SSRXP_U", "input"),
        (5, "SSRXN_U", "input"),
        (6, "AVDD33_RX_U", "power_in"),
        (7, "AVDD12_PLL", "power_in"),
        # USB2 Upstream
        (8, "DM_U", "bidirectional"),
        (9, "DP_U", "bidirectional"),
        # Config
        (10, "XTAL_IN", "input"),
        (11, "XTAL_OUT", "output"),
        (12, "DVDD12_CORE", "power_in"),
        (13, "DVDD33_CORE", "power_in"),
        (14, "RESET_N", "input"),
        (15, "GANG_N", "input"),
        (16, "STRAP0", "input"),
    ]
    right_pins = [
        # USB3 Downstream Port 1
        (64, "SSTXP_D1", "output"),
        (63, "SSTXN_D1", "output"),
        (62, "AVDD33_TX_D1", "power_in"),
        (61, "SSRXP_D1", "input"),
        (60, "SSRXN_D1", "input"),
        (59, "AVDD33_RX_D1", "power_in"),
        # USB2 Downstream Port 1
        (58, "DM_D1", "bidirectional"),
        (57, "DP_D1", "bidirectional"),
        # USB3 Downstream Port 2
        (56, "SSTXP_D2", "output"),
        (55, "SSTXN_D2", "output"),
        (54, "AVDD33_TX_D2", "power_in"),
        (53, "SSRXP_D2", "input"),
        (52, "SSRXN_D2", "input"),
        (51, "AVDD33_RX_D2", "power_in"),
        # USB2 Downstream Port 2
        (50, "DM_D2", "bidirectional"),
        (49, "DP_D2", "bidirectional"),
    ]
    # Bottom pins (power and misc) — we'll put them on left/right to keep it simpler
    # Actually let's extend the left/right lists
    left_pins += [
        (17, "STRAP1", "input"),
        (18, "STRAP2", "input"),
        (19, "STRAP3", "input"),
        (20, "SDA", "bidirectional"),
        (21, "SCL", "input"),
        (22, "DVDD12_1", "power_in"),
        (23, "DVDD33_1", "power_in"),
        (24, "DVDD12_2", "power_in"),
    ]
    right_pins += [
        (48, "DVDD33_2", "power_in"),
        (47, "DVDD12_3", "power_in"),
        (46, "OCS1_N", "input"),
        (45, "OCS2_N", "input"),
        (44, "PRTPWR1", "output"),
        (43, "PRTPWR2", "output"),
        (42, "LED_U", "output"),
        (41, "SUSPEND_N", "output"),
    ]
    # Remaining ground/power pins
    left_pins += [
        (25, "AVSS_U", "power_in"),
        (26, "DVSS_1", "power_in"),
        (27, "DVSS_2", "power_in"),
        (28, "DVSS_3", "power_in"),
        (29, "TEST", "input"),
        (30, "NC", "passive"),
        (31, "NC", "passive"),
        (32, "NC", "passive"),
    ]
    right_pins += [
        (40, "NC", "passive"),
        (39, "NC", "passive"),
        (38, "AVSS_D1", "power_in"),
        (37, "AVSS_D2", "power_in"),
        (36, "DVSS_4", "power_in"),
        (35, "DVSS_5", "power_in"),
        (34, "DVSS_6", "power_in"),
        (33, "AVSS_PLL", "power_in"),
    ]

    return gen_simple_ic(
        "TUSB8020B", "U",
        "2-port USB 3.0 hub controller, QFP-64",
        "usb3 hub controller tusb8020b ti superspeed",
        "Package_QFP:TQFP-64_10x10mm_P0.5mm", "",
        left_pins, right_pins,
        body_width=15.24,
    )


def gen_ecp5_45f():
    """LFE5U-45F-6BG256 — Lattice ECP5 FPGA in BGA-256.

    Multi-unit symbol organized by I/O bank + config + power.
    Pin mapping from Lattice FPGA-TN-02033 for BGA-256 package.
    """
    lines = []

    # Symbol header
    lines.append(symbol_header(
        "LFE5U-45F-6BG256", "U",
        "Lattice ECP5 FPGA, 44K LUTs, BGA-256",
        "fpga lattice ecp5 lfe5u bga256",
        "Package_BGA:BGA-256_14x14mm_Layout16x16_P0.8mm",
        ""
    ))

    # --- Unit 1: Bank 0 (left side I/O, primary config) ---
    bank0_left = [
        ("A2", "PT67A/PL47A", "bidirectional"),
        ("B1", "PT65B/PL47B", "bidirectional"),
        ("B2", "PT62B/PL44B", "bidirectional"),
        ("A3", "PT62A/PL44A", "bidirectional"),
        ("C1", "PT60B", "bidirectional"),
        ("C2", "PT60A", "bidirectional"),
        ("D1", "PT56B", "bidirectional"),
        ("E1", "PT56A", "bidirectional"),
        ("D2", "PT53B", "bidirectional"),
        ("E2", "PT53A", "bidirectional"),
        ("C3", "PT51B", "bidirectional"),
        ("D3", "PT51A", "bidirectional"),
    ]
    bank0_right = [
        ("E3", "PT49B", "bidirectional"),
        ("F1", "PT49A", "bidirectional"),
        ("F2", "PT47B", "bidirectional"),
        ("F3", "PT47A", "bidirectional"),
        ("G2", "PT44B", "bidirectional"),
        ("G1", "PT44A", "bidirectional"),
        ("H1", "PT42B", "bidirectional"),
        ("H2", "PT42A", "bidirectional"),
        ("G3", "PT40B", "bidirectional"),
        ("H3", "PT38A", "bidirectional"),
        ("J1", "PT36B", "bidirectional"),
        ("J2", "PT36A", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_1_1\"")
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {len(bank0_left)*1.27 + 1.27})
\t\t\t\t(end 7.62 {-len(bank0_left)*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank0_left):
        y = len(bank0_left)*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank0_right):
        y = len(bank0_right)*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 2: Bank 1 ---
    bank1 = [
        ("J3", "PR2A", "bidirectional"),
        ("K1", "PR2B", "bidirectional"),
        ("K2", "PR5A", "bidirectional"),
        ("K3", "PR5B", "bidirectional"),
        ("L1", "PR8A", "bidirectional"),
        ("L2", "PR8B", "bidirectional"),
        ("L3", "PR11A", "bidirectional"),
        ("M1", "PR11B", "bidirectional"),
        ("M2", "PR14A", "bidirectional"),
        ("M3", "PR14B", "bidirectional"),
        ("N1", "PR17A", "bidirectional"),
        ("N2", "PR17B", "bidirectional"),
    ]
    bank1_r = [
        ("N3", "PR20A", "bidirectional"),
        ("P1", "PR20B", "bidirectional"),
        ("P2", "PR23A", "bidirectional"),
        ("P3", "PR23B", "bidirectional"),
        ("R1", "PR26A", "bidirectional"),
        ("R2", "PR26B", "bidirectional"),
        ("R3", "PR29A", "bidirectional"),
        ("T2", "PR29B", "bidirectional"),
        ("T3", "PR32A", "bidirectional"),
        ("R4", "PR32B", "bidirectional"),
        ("T4", "PR35A", "bidirectional"),
        ("P4", "PR35B", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_2_1\"")
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {len(bank1)*1.27 + 1.27})
\t\t\t\t(end 7.62 {-len(bank1)*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank1):
        y = len(bank1)*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank1_r):
        y = len(bank1_r)*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 3: Bank 2 ---
    bank2 = [
        ("N4", "PR38A", "bidirectional"),
        ("T5", "PR38B", "bidirectional"),
        ("R5", "PR41A", "bidirectional"),
        ("P5", "PR41B", "bidirectional"),
        ("T6", "PR44A", "bidirectional"),
        ("R6", "PR44B", "bidirectional"),
        ("N6", "PR47A", "bidirectional"),
        ("P6", "PR47B", "bidirectional"),
    ]
    bank2_r = [
        ("T7", "PR49A", "bidirectional"),
        ("R7", "PR49B", "bidirectional"),
        ("P7", "PR53A", "bidirectional"),
        ("T8", "PR53B", "bidirectional"),
        ("R8", "PR56A", "bidirectional"),
        ("P8", "PR56B", "bidirectional"),
        ("N8", "PR59A", "bidirectional"),
        ("T9", "PR59B", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_3_1\"")
    h2 = max(len(bank2), len(bank2_r))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h2*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h2*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank2):
        y = h2*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank2_r):
        y = h2*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 4: Bank 3 ---
    bank3 = [
        ("R9", "PB4A", "bidirectional"),
        ("P9", "PB4B", "bidirectional"),
        ("T10", "PB6A", "bidirectional"),
        ("R10", "PB6B", "bidirectional"),
        ("P10", "PB9A", "bidirectional"),
        ("N10", "PB9B", "bidirectional"),
        ("T11", "PB11A", "bidirectional"),
        ("R11", "PB11B", "bidirectional"),
    ]
    bank3_r = [
        ("P11", "PB13A", "bidirectional"),
        ("N11", "PB13B", "bidirectional"),
        ("T12", "PB15A", "bidirectional"),
        ("R12", "PB15B", "bidirectional"),
        ("P12", "PB18A", "bidirectional"),
        ("N12", "PB18B", "bidirectional"),
        ("T13", "PB20A", "bidirectional"),
        ("R13", "PB20B", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_4_1\"")
    h3 = max(len(bank3), len(bank3_r))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h3*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h3*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank3):
        y = h3*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank3_r):
        y = h3*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 5: Bank 6 ---
    bank6 = [
        ("P13", "PL5A", "bidirectional"),
        ("N13", "PL5B", "bidirectional"),
        ("T14", "PL8A", "bidirectional"),
        ("R14", "PL8B", "bidirectional"),
        ("P14", "PL11A", "bidirectional"),
        ("N14", "PL11B", "bidirectional"),
        ("T15", "PL14A", "bidirectional"),
        ("R15", "PL14B", "bidirectional"),
    ]
    bank6_r = [
        ("P15", "PL17A", "bidirectional"),
        ("N15", "PL17B", "bidirectional"),
        ("T16", "PL20A", "bidirectional"),
        ("R16", "PL20B", "bidirectional"),
        ("P16", "PL23A", "bidirectional"),
        ("N16", "PL23B", "bidirectional"),
        ("M16", "PL26A", "bidirectional"),
        ("L16", "PL26B", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_5_1\"")
    h5 = max(len(bank6), len(bank6_r))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h5*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h5*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank6):
        y = h5*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank6_r):
        y = h5*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 6: Bank 7 ---
    bank7 = [
        ("K16", "PL29A", "bidirectional"),
        ("K15", "PL29B", "bidirectional"),
        ("J16", "PL32A", "bidirectional"),
        ("J15", "PL32B", "bidirectional"),
        ("J14", "PL35A", "bidirectional"),
        ("H16", "PL35B", "bidirectional"),
        ("H15", "PL38A", "bidirectional"),
        ("H14", "PL38B", "bidirectional"),
    ]
    bank7_r = [
        ("G16", "PL41A", "bidirectional"),
        ("G15", "PL41B", "bidirectional"),
        ("G14", "PL44A", "bidirectional"),
        ("F16", "PL47A", "bidirectional"),
        ("F15", "PL47B", "bidirectional"),
        ("E16", "PL50A", "bidirectional"),
        ("E15", "PL50B", "bidirectional"),
        ("E14", "PL53A", "bidirectional"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_6_1\"")
    h6 = max(len(bank7), len(bank7_r))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h6*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h6*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(bank7):
        y = h6*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(bank7_r):
        y = h6*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 7: Configuration ---
    cfg_left = [
        ("A1", "PROGRAMN", "input"),
        ("A4", "INITN", "bidirectional"),
        ("B4", "DONE", "bidirectional"),
        ("C4", "TMS", "input"),
        ("D4", "TCK", "input"),
        ("C5", "TDI", "input"),
        ("E4", "TDO", "output"),
        ("D5", "CCLK/MCLK", "bidirectional"),
    ]
    cfg_right = [
        ("C6", "SO/SPISO", "bidirectional"),
        ("D6", "SI/SISPI", "bidirectional"),
        ("B5", "SN/CSN", "output"),
        ("A5", "CFG0", "input"),
        ("A6", "CFG1", "input"),
        ("B6", "CFG2", "input"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_7_1\"")
    h7 = max(len(cfg_left), len(cfg_right))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h7*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h7*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(cfg_left):
        y = h7*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(cfg_right):
        y = h7*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    # --- Unit 8: Power ---
    pwr_left = [
        ("D7", "VCC", "power_in"),
        ("E7", "VCC", "power_in"),
        ("F7", "VCC", "power_in"),
        ("G7", "VCC", "power_in"),
        ("H7", "VCC", "power_in"),
        ("J7", "VCC", "power_in"),
        ("K7", "VCC", "power_in"),
        ("L7", "VCC", "power_in"),
        ("D8", "VCCIO0", "power_in"),
        ("E8", "VCCIO1", "power_in"),
        ("F8", "VCCIO2", "power_in"),
        ("G8", "VCCIO3", "power_in"),
        ("H8", "VCCIO6", "power_in"),
        ("J8", "VCCIO7", "power_in"),
        ("K8", "VCCAUX", "power_in"),
        ("L8", "VCCAUX", "power_in"),
    ]
    pwr_right = [
        ("D9", "GND", "power_in"),
        ("E9", "GND", "power_in"),
        ("F9", "GND", "power_in"),
        ("G9", "GND", "power_in"),
        ("H9", "GND", "power_in"),
        ("J9", "GND", "power_in"),
        ("K9", "GND", "power_in"),
        ("L9", "GND", "power_in"),
        ("D10", "GND", "power_in"),
        ("E10", "GND", "power_in"),
        ("F10", "GND", "power_in"),
        ("G10", "GND", "power_in"),
        ("H10", "GND", "power_in"),
        ("J10", "GND", "power_in"),
        ("K10", "GND", "power_in"),
        ("L10", "GND", "power_in"),
    ]

    lines.append(f"\t\t(symbol \"LFE5U-45F-6BG256_8_1\"")
    h8 = max(len(pwr_left), len(pwr_right))
    lines.append(f"""\t\t\t(rectangle
\t\t\t\t(start -7.62 {h8*1.27 + 1.27})
\t\t\t\t(end 7.62 {-h8*1.27 - 1.27})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)""")
    for i, (ball, name, ptype) in enumerate(pwr_left):
        y = h8*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", -7.62 - 3.81, y, 0, 3.81, name, ball))
    for i, (ball, name, ptype) in enumerate(pwr_right):
        y = h8*1.27 - i * 2.54
        lines.append(pin_block(ptype, "line", 7.62 + 3.81, y, 180, 3.81, name, ball))
    lines.append("\t\t)")

    lines.append("\t)")  # close symbol
    return "\n".join(lines)


def gen_ddr2_sodimm():
    """DDR2 SODIMM socket — simplified 200-pin connector.
    Only define the commonly used pins; NC pins omitted for clarity.
    Uses a single-unit flat symbol with key signal groups."""
    # For a 200-pin DDR2 SODIMM we'll create a simplified symbol with grouped pins
    # Full 200-pin symbol would be enormous; this covers the essential signals
    left_pins = []
    right_pins = []

    # Address pins (A0-A13) + BA0-BA2
    for i in range(14):
        left_pins.append((str(i*2+1), f"A{i}", "input"))
    left_pins.append(("29", "BA0", "input"))
    left_pins.append(("31", "BA1", "input"))
    left_pins.append(("33", "BA2", "input"))

    # Control
    left_pins.append(("35", "RAS#", "input"))
    left_pins.append(("37", "CAS#", "input"))
    left_pins.append(("39", "WE#", "input"))
    left_pins.append(("41", "CS0#", "input"))
    left_pins.append(("43", "CKE0", "input"))
    left_pins.append(("45", "ODT0", "input"))
    left_pins.append(("47", "CK0", "input"))
    left_pins.append(("49", "CK0#", "input"))

    # Data DQ0-DQ7 + DQS0/DM0
    for i in range(8):
        right_pins.append((str(60+i*2), f"DQ{i}", "bidirectional"))
    right_pins.append(("76", "DQS0", "bidirectional"))
    right_pins.append(("78", "DQS0#", "bidirectional"))
    right_pins.append(("80", "DM0", "output"))

    # Data DQ8-DQ15 + DQS1/DM1
    for i in range(8):
        right_pins.append((str(82+i*2), f"DQ{i+8}", "bidirectional"))
    right_pins.append(("98", "DQS1", "bidirectional"))
    right_pins.append(("100", "DQS1#", "bidirectional"))
    right_pins.append(("102", "DM1", "output"))

    # Power
    left_pins.append(("140", "VDD", "power_in"))
    left_pins.append(("142", "VDD", "power_in"))
    left_pins.append(("144", "VDDQ", "power_in"))
    left_pins.append(("146", "VDDQ", "power_in"))
    left_pins.append(("150", "VREF", "input"))

    right_pins.append(("141", "VSS", "power_in"))
    right_pins.append(("143", "VSS", "power_in"))
    right_pins.append(("145", "VSSQ", "power_in"))
    right_pins.append(("147", "VSSQ", "power_in"))
    right_pins.append(("200", "SDA", "bidirectional"))
    right_pins.append(("199", "SCL", "input"))

    return gen_simple_ic(
        "DDR2_SODIMM", "J",
        "DDR2 SODIMM socket, 200-pin (simplified symbol — key signals only)",
        "ddr2 sodimm memory socket",
        "", "",
        left_pins, right_pins,
        body_width=15.24,
    )


def main():
    header = """(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
"""
    footer = ")\n"

    symbols = []
    symbols.append(gen_bus_40pin())
    symbols.append(gen_grove_i2c())
    symbols.append(gen_fs8205a())
    symbols.append(gen_bh1750())
    symbols.append(gen_tps63020())
    symbols.append(gen_inmp441())
    symbols.append(gen_ov2640())
    symbols.append(gen_is66wvh8m8bll())
    symbols.append(gen_tusb8020b())
    symbols.append(gen_ecp5_45f())
    symbols.append(gen_ddr2_sodimm())

    with open("icarus-v2.kicad_sym", "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(symbols))
        f.write("\n")
        f.write(footer)

    print(f"Generated icarus-v2.kicad_sym with {len(symbols)} symbols")


if __name__ == "__main__":
    main()
