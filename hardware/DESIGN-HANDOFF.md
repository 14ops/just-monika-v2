# DESIGN HANDOFF: Icarus Carrier Board
**Orange Pi CM5 Custom Carrier for Just Monika AI Companion**

**Document Version:** 1.0  
**Date:** 2026-03-14  
**Target Form Factor:** ~100mm × 90mm  
**Layer Count:** 4-layer  
**Status:** Ready for Layout Phase

---

## Table of Contents
1. [B2B Connector Signal Allocation](#1-b2b-connector-signal-allocation)
2. [Pin Mapping — CM5 to Icarus Peripherals](#2-pin-mapping--cm5-to-icarus-peripherals)
3. [Power Architecture](#3-power-architecture)
4. [PCB Design Constraints](#4-pcb-design-constraints)
5. [Component Count Estimate](#5-component-count-estimate)
6. [Board Outline and Connector Placement](#6-board-outline-and-connector-placement)
7. [Risk Register](#7-risk-register)

---

## 1. B2B Connector Signal Allocation

### Overview
The Orange Pi CM5 uses **three 100-pin DF40C-100DP-0.4V(51) B2B connectors** at 0.4mm pitch. Signal assignments below reflect interface groupings; **exact pin numbers must be confirmed against Orange Pi CM5 official schematic (PENDING)**.

### Connector JP1 (Primary Power & Storage)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **POWER** | IN | 4 | +5V (2×), GND (2×), bulk input from USB-C/barrel jack |
| **SATA_0 / PCIe 2.0** | TX/RX | 4 | M.2 Key M NVMe or SATA SSD interface |
| **USB3.0** | TX/RX | 4 | Primary USB 3.0 host port |
| **Reserved/NC** | — | ~84 | For future expansion or GND planes |

### Connector JP2 (Multimedia & USB 2.0)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **HDMI 2.1 / eDP 1.3** | TX | 6 | Primary display output (HDMI preferred for Constellation UI) |
| **USB2.0 (×3)** | TX/RX | 12 | Flashing (via CP2102N), debug, future expansion |
| **TYPE-C ALT-MODE** | TX/RX | 2 | USB 2.0 data for flashing; 5V power on separate pins (via JP1) |
| **uSD Card** | TX/RX | 6 | μSD interface for boot/storage backup |
| **MIPI TX 4-lane** | TX | 4 | Camera/display serial interface (future) |
| **Reserved/NC** | — | ~64 | GND, routing flexibility |

### Connector JP3 (Audio, Control, & Misc I/O)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **I2S Bus** | TX/RX | 4 | I2S_SCLK, I2S_LRCK, I2S_SDO (to amp), I2S_SDI (from mic) |
| **I2C Bus** | TX/RX | 2 | I2C_SDA/SCL for OLED (0x3C) and future sensors |
| **UART Debug** | TX/RX | 2 | UART to CP2102N USB bridge |
| **GPIO (Digital)** | TX/RX | 6 | LED Ring (WS2812B), Touch sensor (TTP223), PWM fan, RESET_N |
| **MIPI RX (×2)** | RX | 4 | 2-lane MIPI inputs (reserved for expansion) |
| **SATA_1 / PCIe / USB3** | TX/RX | 4 | Secondary storage interface (mode-select via HW jumper) |
| **CAN / PDM** | TX/RX | 4 | Reserved for future CAN + digital mic array |
| **Reserved/NC** | — | ~64 | GND, signal integrity |

---

## 2. Pin Mapping — CM5 to Icarus Peripherals

### 2.1 I2S Bus (Audio Subsystem)
| Signal | CM5 Pin | CM5 Level | Icarus Component | Icarus Level | Connection |
|---|---|---|---|---|---|
| I2S_SCLK | JP3-? | 1.8V | MAX98357A (DIN pin 1) | 3.3V | Direct @ 1.8V (max-98357a rated) |
| I2S_LRCK | JP3-? | 1.8V | MAX98357A (DIN pin 3) | 3.3V | Direct @ 1.8V |
| I2S_SDO (speaker) | JP3-? | 1.8V | MAX98357A (DIN pin 5) | 3.3V | Direct @ 1.8V (output) |
| I2S_SDI (mic input) | JP3-? | 1.8V | INMP441 (DATA) | 3.3V | **Level shifter required** |
| Mic I2S_BCLK | JP3-? | 1.8V | INMP441 (CLK) | 3.3V | Level shifter (SN74LVC245 or equiv) |

**I2S Audio Path Details:**
- **MAX98357A:** Mono Class-D amp, 3.2W @ 4Ω, powered by 5V rail. DIN interface tolerates 1.8V logic.
- **INMP441:** MEMS PDM microphone, 3.3V supply. **PDM output = 3.3V logic** → requires level shifter to 1.8V input on CM5.
  - Alternative: Use direct PDM input on RK3588S (if available on JP3), bypassing shifter.
  - **ACTION:** Confirm CM5 PDM pin availability; if present, use PDM mode directly (no I2S_SDI shifter needed).
- **Shifter:** TI SN74LVC245 (octal, low-power) in 3.3V domain. Powered by CM5 3.3V output.

### 2.2 I2C Bus (Display & Sensors)
| Signal | CM5 Pin | Level | Icarus Component | Address | Pull-ups |
|---|---|---|---|---|---|
| I2C_SDA | JP3-? | 3.3V | SSD1306 OLED (pin 18) | 0x3C | 4.7kΩ to 3.3V |
| I2C_SCL | JP3-? | 3.3V | SSD1306 OLED (pin 19) | 0x3C | 4.7kΩ to 3.3V |

**I2C Details:**
- Standard 100 kHz mode (no fast-mode needed).
- SSD1306: 128×64 pixels, SPI/I2C selectable (use I2C). Powered by 3.3V from CM5.
- Pull-ups: 4.7kΩ resistors on PCB, sourced from CM5 3.3V output.
- No address conflicts expected (INMP441 has no I2C, MAX98357A is I2S only).

### 2.3 GPIO (Digital Control & LED Ring)
| Signal | CM5 Pin | Level | Icarus Component | Purpose | Interface |
|---|---|---|---|---|---|
| GPIO_LEDRING | JP3-? | 3.3V | WS2812B LED Ring (10 or 12 LEDs) | RGB control signal | SPI/1-wire protocol |
| GPIO_TOUCH | JP3-? | 3.3V | TTP223 Capacitive Sensor | Touch input | Digital GPIO (open-drain option) |
| GPIO_PWM_FAN | JP3-? | 3.3V | 5V Fan (PWM header) | Speed control | Level shifter 3.3V→5V |
| GPIO_RESET | JP3-? | 3.3V | Exposed test point | Soft reset trigger | Open-drain output |

**LED Ring Path (WS2812B):**
- CM5 GPIO (3.3V) → **74AHCT1G125 level shifter** (single gate, 3.3V→5V) → 470Ω series resistor → WS2812B DIN.
- Pull-down 100Ω resistor on WS2812B DIN for rising-edge shaping (optional but recommended for signal integrity).
- Data format: GRB, 800 kHz bitrate, 24 bits/LED.
- Supply: 5V rail (dedicated cap at ring connector).

**Touch Sensor (TTP223):**
- TTP223: Single-button capacitive sensor. Output is open-drain → can tie directly to CM5 GPIO with internal pull-up enabled.
- Pad size: ~16×16mm on PCB top layer. Mounted under 1.6mm acrylic or conformal coat for ESD protection.

**Fan Control:**
- PWM input on 5V fan → require level shift from CM5 3.3V GPIO.
- Use same 74AHCT1G125 or similar (can cascade multiple gates on same chip).
- Fan header: 2-pin (PWM, GND) or 3-pin (PWM, +5V, GND) depending on fan type.

### 2.4 HDMI Output (Constellation UI Display)
| Signal | CM5 Pin | Level | Icarus Connector | Notes |
|---|---|---|---|---|
| HDMI 2.1 D+/D- | JP2-? | LVDS (low-voltage) | HDMI Type-A connector (standard) | Standard 19-pin HDMI male, on PCB edge |
| DDC (I2C SDA/SCL) | JP2-? | 3.3V | HDMI pins 16/17 | Pull-ups on HDMI cable (typically) |
| CEC (optional) | JP2-? | 3.3V | HDMI pin 13 | Not required for initial design |

**HDMI Path:**
- RK3588S HDMI output is LVDS-based, requires no external swing adjustment.
- HDMI connector type: **Type-A male, flush-mount or right-angle (TBD based on PCB layout)**.
- Impedance: 100Ω differential for HDMI data, 100Ω for clock.
- **No HDCP required** (open-source Constellation UI, no content protection).
- DDC pull-ups: typically on display cable; if not present, add 4.7kΩ on Icarus for safety.

### 2.5 USB-C Connector (Power & Debug)
| Pin | Signal | Level | Icarus Circuit | Notes |
|---|---|---|---|---|
| 1,20 | GND | GND | USB-C shell → Main GND plane | |
| 4,9 | VBUS | 5V in | Schottky OR-gate (if barrel jack backup) or direct | Primary 5V source, 4A max |
| 2,3,10,11 | D+/D- | 3.3V | CP2102N USB-UART bridge | Debug serial port, also used for flashing via USB mass storage |
| 12-15 | DP0/DN0 (USB 3.0 SS) | 3.3V | Reserved for future USB 3.0 OTG | Not used in initial design |
| 18,19 | SBU1/SBU2 | — | No-connect (not needed) | |

**USB-C Power Input:**
- **5V fixed, no PD negotiation** — Icarus is a power sink only, not a source.
- Rated for 5V/4A = 20W max input (ample for 18W peak system draw).
- Connector: USB Type-C female, right-angle, 24-pin (full-featured, even if not all pins used).

### 2.6 UART Debug (Serial Console)
| Signal | CM5 Pin | Level | Icarus Component | Icarus Pin |
|---|---|---|---|---|
| UART_TX | JP3-? | 3.3V | CP2102N (RXD, pin 5) | Micro-USB or JST-SH connector |
| UART_RX | JP3-? | 3.3V | CP2102N (TXD, pin 4) | Micro-USB or JST-SH connector |
| GND | GND | — | CP2102N (pin 3) | — |

**CP2102N Details:**
- Silicon Labs USB-UART bridge, 3.3V logic, integrated DC-DC and oscillator.
- USB port: Micro-USB Type-B connector or JST-SH 4-pin (power, D+, D-, GND) for debug header.
- Baud rate: auto-detected or fixed at 1,500,000 bps (bootloader default for RK3588S).
- **Optional:** Add Reset and Boot0 push-buttons to Icarus for flashing without GUI tools (recommended for field updates).

### 2.7 Storage (M.2 or SATA SSD)
| Signal | CM5 Pin | Level | Icarus Connector | Notes |
|---|---|---|---|---|
| SATA0/PCIe2.0 TX/RX (×4) | JP1-? | LVDS/CML | M.2 Key M slot or SATA III connector | Mode selection: HW jumper or auto-detect |
| SATA1 (×4) | JP1-? | LVDS/CML | Optional secondary SATA or USB 3.0 (jumper selectable) | Future expansion |

**Storage Subsystem:**
- **Primary:** M.2 2280 (22mm × 80mm) NVMe SSD via PCIe 2.0 (×4 lanes = 250 MB/s).
  - Connector: standard M.2 Key M socket, PCB-mounted (90° angle recommended for compact form).
  - 3.3V power supply to M.2 module from CM5 3.3V rail.
- **Alternative:** SATA III if NVMe unavailable (e.g., legacy SSD). Separate mechanical design required.
- **Impedance:** 100Ω differential for PCIe TX/RX pairs.

### 2.8 Fan Control (PWM Header)
| Signal | CM5 Pin | Level | Header Pin | Notes |
|---|---|---|---|---|
| PWM | JP3-? | 3.3V (shifted→5V) | Pin 1 (signal) | Level shifted via 74AHCT1G125 |
| +5V | 5V rail | 5V | Pin 2 | Power directly from 5V rail (with inline fuse) |
| GND | GND | GND | Pin 3 | — |

**Fan Details:**
- Connector type: 3-pin JST-EH or Molex 4.2mm (standard PC fan header).
- Rated fan: 40mm or 50mm DC brushless, 5V, ~200 mA typical (assume peak 400mA for budget).
- PWM frequency: typically 25 kHz (CM5 can generate via GPIO or dedicated PWM pin).

### 2.9 Touch Sensor (Capacitive Button)
| Signal | CM5 Pin | Level | Icarus Component | Notes |
|---|---|---|---|---|
| TOUCH_OUT | JP3-? | 3.3V | TTP223 (INT pin) | Open-drain or CMOS output (TBD by variant) |
| GND | GND | — | TTP223 (GND) | — |

**TTP223 Configuration:**
- Single-button capacitive sensor IC, 2.4–5.5V supply (use 3.3V from CM5).
- Pad size on Icarus: **16×16mm square, top-layer copper, 1mm border for mechanical tolerance**.
- Output: active-low by default (INT goes low when touched).
- Mounting: soldered directly on Icarus PCB; protected by 1.6mm acrylic overlay or conformal coat.
- Optional: add bypass cap (0.1µF) on VDD near IC for noise filtering.

---

## 3. Power Architecture

### 3.1 Power Input & Distribution

**Primary Input: USB-C 5V @ 4A**
- Connector: USB Type-C female, right-angle, PCB-mounted.
- No power delivery (PD) negotiation; fixed 5V only.
- Inline fuse (Polyfuse): 6A hold current, 8A trip (60-second recovery).
- Input protection: TVS diode (SMAJ5.0A, SMD) across VBUS+GND for transient overvoltage.

**Optional Secondary Input: Barrel Jack 5V Backup**
- Connector: 5.5mm × 2.1mm, center-positive (standard).
- OR-gate: Schottky diodes (BAT54S or equiv) for 5V rail combining (VBUS and barrel jack in parallel).
  - Schottky forward drop: ~0.2V @ 2A (acceptable for system tolerance).
- **Action:** Decide during layout phase whether to include; recommended for field serviceability.

### 3.2 5V Rail (Primary Power Bus)
Supplies:
- **CM5 SOM:** 5V input via B2B connector (JP1), max 1800mA.
- **MAX98357A:** 5V speaker amp, ~2.5W continuous (peak 3.2W @ 4Ω).
- **WS2812B LED Ring:** ~0.6W @ 12 LEDs (60mA per full white).
- **5V Fan:** ~0.2–0.4W.
- **HDMI Connector:** ~0.1W (passive).
- **USB-C Connector:** Pull-up resistors, negligible (<0.01W).

**5V Rail Filtering:**
- Bulk capacitor (100µF, 6.3V), placed near USB-C input.
- Ceramic capacitors (10µF + 1µF) on CM5 side and near each active consumer (MAX98357A, fan).
- **Total allowance:** 20W (from 5V/4A USB-C input) is sufficient for system peak ~18W (see power budget below).

### 3.3 3.3V Rail (Logic & Sensors)
**Source:** CM5 SOM output, max 600mA.

Supplies:
- **SSD1306 OLED:** ~5mA @ 128×64 running.
- **INMP441 Microphone:** ~2mA @ 1.8V (but powered from 3.3V step-down or direct, TBD).
- **TTP223 Touch Sensor:** ~10µA sleep, ~5mA active.
- **Level Shifters (SN74LVC245, 74AHCT1G125):** ~5mA combined.
- **I2C pull-up resistors (2×4.7kΩ):** ~0.35mA @ 3.3V.
- **GPIO logic (UART, USB mux):** ~10mA.

**Total 3.3V budget:** ~35–40mA typical, well within 600mA CM5 output.

**3.3V Rail Filtering:**
- Ceramic capacitors (10µF + 1µF) distributed near major consumers.
- No additional inductor or DC-DC needed; CM5 output is clean.

### 3.4 1.8V Rail (CM5 I/O Reference)
**Source:** CM5 SOM output, max 600mA.

**Supplies:**
- **MAX98357A I2S logic:** ~5mA.
- **INMP441 (if powered from 1.8V variant):** ~2mA.
- **RK3588S internal I/O buffers:** already accounted in CM5 budget.

**1.8V Rail Filtering:**
- Ceramic capacitors (10µF + 1µF) near I2S interface.
- This rail is typically clean from CM5; minimal filtering required.

### 3.5 Power Budget Table

| Component | Voltage | Current (Typical) | Current (Peak) | Power (Typ) | Power (Peak) | Notes |
|---|---|---|---|---|---|
| **CM5 SOM** | 5V | 2000mA | 2400mA | 10.0W | 12.0W | RK3588S @ full load, Mali-G610, NPU |
| MAX98357A | 5V | 100mA | 650mA | 0.5W | 3.2W | Mono Class-D, 3.2W max into 4Ω load |
| INMP441 | 3.3V | 2mA | 2mA | 0.007W | 0.007W | MEMS PDM mic, stable draw |
| SSD1306 OLED | 3.3V | 5mA | 15mA | 0.017W | 0.05W | 128×64 display, varies by content |
| TTP223 Touch | 3.3V | 0.01mA | 5mA | <0.001W | 0.017W | Low-power capacitive sensor |
| WS2812B (12×) | 5V | 60mA | 360mA | 0.3W | 1.8W | Full white intensity (rare); typical ~0.3W avg |
| 5V Fan | 5V | 40mA | 200mA | 0.2W | 1.0W | 40mm DC fan, PWM modulated |
| Level Shifters | 3.3V | 5mA | 10mA | 0.017W | 0.033W | SN74LVC245, 74AHCT1G125 combined |
| UART/USB ICs | 3.3V | 10mA | 10mA | 0.033W | 0.033W | CP2102N oscillator + buffers |
| Passive (resistors, caps) | 3.3V/5V | 5mA | 5mA | 0.02W | 0.02W | Pull-ups, bypass caps, minor leakage |
| **SYSTEM TOTAL** | — | 2.2A (5V) | 3.6A (5V) | **11.1W** | **18.2W** | Peak occurs: CM5 + speaker + LEDs + fan simultaneous |

**Key Observations:**
- **5V input bus dominates:** 3.6A peak < 4A USB-C limit. Safe margin.
- **CM5 is the main load:** ~12W peak is ~67% of system budget.
- **LED ring peak (1.8W) is secondary:** rarely sustained; typical average ~0.3W.
- **Total system peak (18.2W) fits within 20W USB-C headroom.**

### 3.6 Power Sequencing & Soft Start
- **No special sequencing required:** CM5 handles its own internal rails; external 5V, 3.3V, 1.8V are passive outputs from SOM.
- **Soft-start:** CM5 powers on when 5V is applied. No manual startup circuit needed (SOM has internal POR logic).
- **Shutdown:** Pull POWER_ON signal (via test point or button) to put SOM into sleep mode (recommended for field shutdown).

---

## 4. PCB Design Constraints

### 4.1 Stackup & Layer Allocation
**4-Layer PCB (1.6mm total thickness):**

| Layer | Thickness | Purpose | Notes |
|---|---|---|---|
| **L1 (Top Signal)** | 0.15mm | Component placement, trace routing, high-speed signals (USB, HDMI) | 0.15mm minimum trace width |
| **L2 (GND Plane)** | 0.08mm | Ground reference plane, 2–4oz copper, solid except for via clearances | Via stitching every ~5mm |
| **L3 (Power Plane)** | 0.08mm | +5V and +3.3V distribution (can split or power zones with layer if needed) | Via stitching to L4 for power return |
| **L4 (Bottom Signal)** | 0.15mm | Component placement (optional), trace routing, return paths | Mostly GND return; secondary signal layer |

**Rationale:** 4-layer is minimum for mixed-signal board with audio (I2S) and USB 2.0 impedance control. 2-layer would require massive via density and is not recommended.

### 4.2 Impedance & High-Speed Routing

| Interface | Standard | Target Impedance | Trace Width (est.) | Via Clearance | Notes |
|---|---|---|---|---|---|
| **USB 2.0 (D+/D-)** | USB 2.0 Full-Speed | 90Ω differential | 0.20mm ± 0.05mm | 0.3mm min to signal | Tightly coupled pair, L2–L4 routing OK |
| **HDMI TX (×3 pairs + clock)** | HDMI 2.1 | 100Ω differential | 0.25mm ± 0.05mm | 0.4mm min to signal | May simplify to 100Ω single-ended if bandwidth allows |
| **PCIe 2.0 TX/RX (×4 lanes)** | PCIe 2.0 | 100Ω differential | 0.25mm ± 0.05mm | 0.4mm min to signal | Lower speed than PCIe 3.0; no exotic materials needed |
| **I2S (SCLK, LRCK, SDO/SDI)** | Audio I2S | 50–75Ω (not critical) | 0.30mm | 0.3mm | Low-frequency; not tightly routed |
| **I2C (SDA, SCL)** | I2C 100/400kHz | None (< 1 MHz) | 0.30mm | 0.3mm | Open-drain; no impedance control needed |

**Routing Rules:**
- **USB 2.0 pair:** Keep length-matched to within 2mm; route as tightly coupled pair on L1 with ground guard traces.
- **HDMI:** Similar to USB (3 data pairs + clock). Grouped routing, GND guard traces on sides.
- **Audio (I2S):** Route away from switching power supplies and LCD clock lines (no DC-DC or switcher in this design, so lower EMI risk).
- **Separation:** Keep analog audio (INMP441, MAX98357A) traces ≥5mm from digital high-speed (USB, HDMI) to minimize crosstalk.

### 4.3 Component Placement Rules

**Critical Placement (Non-Negotiable):**

| Component | Placement Rule | Reason | Board Location |
|---|---|---|---|
| **CM5 B2B Connectors (JP1, JP2, JP3)** | Exact center or offset per mounting hole pattern (55×40mm) | Mechanical fit with SOM; no tolerance for error | Center of board, aligned with holes |
| **USB-C Connector** | Edge of PCB, aligned with 5mm clearance to nearest B2B | Accessibility and cable routing | Top edge, center-right |
| **Barrel Jack (optional)** | Right edge of PCB, 10mm below USB-C | Visual separation, cable routing | Right edge |
| **M.2 Slot** | Parallel to board edge, 5mm clearance to nearest connector | Mechanical access for SSD insertion | Bottom edge, right side |
| **HDMI Connector** | Right-angle, flush to board edge, or 90° PCB edge connector | Display cable routing | Left or right edge |
| **CP2102N USB-UART** | Within 30mm of UART pins on JP3; input cap (0.1µF) and output cap (1µF) right-side placement | Minimize skew, reduce EMI | Bottom-left area |
| **MAX98357A** | Within 20mm of I2S pins; power cap (10µF + 1µF) and output LC filter adjacent | Minimize I2S trace length and parasitic inductance | Top-right area (near audio output) |
| **INMP441 Microphone** | ≥50mm from switching supplies (none here), ≥30mm from speaker amp | Acoustic isolation, reduce electrical crosstalk | Top-left or far corner from amp |
| **SSD1306 OLED** | Near I2C pins on JP3; decoupling cap (1µF) very close | Low-current display, minimal skew requirements | Any accessible area; top-left preferred for visibility |
| **TTP223 Touch Pad** | Front-center of board, visible for user touch access | Functional requirement | Center of top surface |
| **WS2812B Ring (10–12 LEDs)** | Arranged in circle, 30mm radius approx., centered on board | Aesthetic; light distribution around device | Perimeter of top surface |
| **Bulk Capacitors (100µF on 5V)** | Right at USB-C connector input | Minimize supply ripple at input | Top-left or top-right, next to USB connector |
| **Decoupling Caps** | Within 5mm of power input pin for each IC | Reduce voltage droop during transients | Adjacent to IC power pins |

**Recommended Layout Zones (100mm × 90mm board):**
```
  [USB-C]
    |
[5V BULK CAP] ... [HDMI or M.2] ... [Barrel Jack]
     |
  [JP2]----[JP1]----[M.2 Slot or SSD]
     |
  [CP2102N]
     |
  [JP3]
     |
[INMP441]   [TTP223 PAD]  [SSD1306 OLED display area]
     |           |
[MAX98357A]  [LED RING perimeter]
     |
  [FAN HEADER]
```

### 4.4 Via Strategy
- **Via size:** 0.3mm drill, 0.5mm pad (standard for 0.4mm pitch B2B tolerances).
- **Via stitching (GND):** Every ~5mm around power planes to maintain low impedance.
- **Thermal vias:** Under large ICs (MAX98357A, CP2102N), 4–9 vias per pad for thermal dissipation (not critical, but good practice).
- **Blind/buried vias:** Not required for 4-layer; standard through-vias sufficient.

# DESIGN HANDOFF: Icarus Carrier Board
**Orange Pi CM5 Custom Carrier for Just Monika AI Companion**

**Document Version:** 1.0  
**Date:** 2026-03-14  
**Target Form Factor:** ~100mm × 90mm  
**Layer Count:** 4-layer  
**Status:** Ready for Layout Phase

---

## Table of Contents
1. [B2B Connector Signal Allocation](#1-b2b-connector-signal-allocation)
2. [Pin Mapping — CM5 to Icarus Peripherals](#2-pin-mapping--cm5-to-icarus-peripherals)
3. [Power Architecture](#3-power-architecture)
4. [PCB Design Constraints](#4-pcb-design-constraints)
5. [Component Count Estimate](#5-component-count-estimate)
6. [Board Outline and Connector Placement](#6-board-outline-and-connector-placement)
7. [Risk Register](#7-risk-register)

---

## 1. B2B Connector Signal Allocation

### Overview
The Orange Pi CM5 uses **three 100-pin DF40C-100DP-0.4V(51) B2B connectors** at 0.4mm pitch. Signal assignments below reflect interface groupings; **exact pin numbers must be confirmed against Orange Pi CM5 official schematic (PENDING)**.

### Connector JP1 (Primary Power & Storage)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **POWER** | IN | 4 | +5V (2×), GND (2×), bulk input from USB-C/barrel jack |
| **SATA_0 / PCIe 2.0** | TX/RX | 4 | M.2 Key M NVMe or SATA SSD interface |
| **USB3.0** | TX/RX | 4 | Primary USB 3.0 host port |
| **Reserved/NC** | — | ~84 | For future expansion or GND planes |

### Connector JP2 (Multimedia & USB 2.0)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **HDMI 2.1 / eDP 1.3** | TX | 6 | Primary display output (HDMI preferred for Constellation UI) |
| **USB2.0 (×3)** | TX/RX | 12 | Flashing (via CP2102N), debug, future expansion |
| **TYPE-C ALT-MODE** | TX/RX | 2 | USB 2.0 data for flashing; 5V power on separate pins (via JP1) |
| **uSD Card** | TX/RX | 6 | μSD interface for boot/storage backup |
| **MIPI TX 4-lane** | TX | 4 | Camera/display serial interface (future) |
| **Reserved/NC** | — | ~64 | GND, routing flexibility |

### Connector JP3 (Audio, Control, & Misc I/O)
| Signal Group | Direction | Pin Count | Notes |
|---|---|---|---|
| **I2S Bus** | TX/RX | 4 | I2S_SCLK, I2S_LRCK, I2S_SDO (to amp), I2S_SDI (from mic) |
| **I2C Bus** | TX/RX | 2 | I2C_SDA/SCL for OLED (0x3C) and future sensors |
| **UART Debug** | TX/RX | 2 | UART to CP2102N USB bridge |
| **GPIO (Digital)** | TX/RX | 6 | LED Ring (WS2812B), Touch sensor (TTP223), PWM fan, RESET_N |
| **MIPI RX (×2)** | RX | 4 | 2-lane MIPI inputs (reserved for expansion) |
| **SATA_1 / PCIe / USB3** | TX/RX | 4 | Secondary storage interface (mode-select via HW jumper) |
| **CAN / PDM** | TX/RX | 4 | Reserved for future CAN + digital mic array |
| **Reserved/NC** | — | ~64 | GND, signal integrity |

---

## 2. Pin Mapping — CM5 to Icarus Peripherals

### 2.1 I2S Bus (Audio Subsystem)
| Signal | CM5 Pin | CM5 Level | Icarus Component | Icarus Level | Connection |
|---|---|---|---|---|---|
| I2S_SCLK | JP3-? | 1.8V | MAX98357A (DIN pin 1) | 3.3V | Direct @ 1.8V (max-98357a rated) |
| I2S_LRCK | JP3-? | 1.8V | MAX98357A (DIN pin 3) | 3.3V | Direct @ 1.8V |
| I2S_SDO (speaker) | JP3-? | 1.8V | MAX98357A (DIN pin 5) | 3.3V | Direct @ 1.8V (output) |
| I2S_SDI (mic input) | JP3-? | 1.8V | INMP441 (DATA) | 3.3V | **Level shifter required** |
| Mic I2S_BCLK | JP3-? | 1.8V | INMP441 (CLK) | 3.3V | Level shifter (SN74LVC245 or equiv) |

**I2S Audio Path Details:**
- **MAX98357A:** Mono Class-D amp, 3.2W @ 4Ω, powered by 5V rail. DIN interface tolerates 1.8V logic.
- **INMP441:** MEMS PDM microphone, 3.3V supply. **PDM output = 3.3V logic** → requires level shifter to 1.8V input on CM5.
  - Alternative: Use direct PDM input on RK3588S (if available on JP3), bypassing shifter.
  - **ACTION:** Confirm CM5 PDM pin availability; if present, use PDM mode directly (no I2S_SDI shifter needed).
- **Shifter:** TI SN74LVC245 (octal, low-power) in 3.3V domain. Powered by CM5 3.3V output.

### 2.2 I2C Bus (Display & Sensors)
| Signal | CM5 Pin | Level | Icarus Component | Address | Pull-ups |
|---|---|---|---|---|---|
| I2C_SDA | JP3-? | 3.3V | SSD1306 OLED (pin 18) | 0x3C | 4.7kΩ to 3.3V |
| I2C_SCL | JP3-? | 3.3V | SSD1306 OLED (pin 19) | 0x3C | 4.7kΩ to 3.3V |

**I2C Details:**
- Standard 100 kHz mode (no fast-mode needed).
- SSD1306: 128×64 pixels, SPI/I2C selectable (use I2C). Powered by 3.3V from CM5.
- Pull-ups: 4.7kΩ resistors on PCB, sourced from CM5 3.3V output.
- No address conflicts expected (INMP441 has no I2C, MAX98357A is I2S only).

### 2.3 GPIO (Digital Control & LED Ring)
| Signal | CM5 Pin | Level | Icarus Component | Purpose | Interface |
|---|---|---|---|---|---|
| GPIO_LEDRING | JP3-? | 3.3V | WS2812B LED Ring (10 or 12 LEDs) | RGB control signal | SPI/1-wire protocol |
| GPIO_TOUCH | JP3-? | 3.3V | TTP223 Capacitive Sensor | Touch input | Digital GPIO (open-drain option) |
| GPIO_PWM_FAN | JP3-? | 3.3V | 5V Fan (PWM header) | Speed control | Level shifter 3.3V→5V |
| GPIO_RESET | JP3-? | 3.3V | Exposed test point | Soft reset trigger | Open-drain output |

**LED Ring Path (WS2812B):**
- CM5 GPIO (3.3V) → **74AHCT1G125 level shifter** (single gate, 3.3V→5V) → 470Ω series resistor → WS2812B DIN.
- Pull-down 100Ω resistor on WS2812B DIN for rising-edge shaping (optional but recommended for signal integrity).
- Data format: GRB, 800 kHz bitrate, 24 bits/LED.
- Supply: 5V rail (dedicated cap at ring connector).

**Touch Sensor (TTP223):**
- TTP223: Single-button capacitive sensor. Output is open-drain → can tie directly to CM5 GPIO with internal pull-up enabled.
- Pad size: ~16×16mm on PCB top layer. Mounted under 1.6mm acrylic or conformal coat for ESD protection.

**Fan Control:**
- PWM input on 5V fan → require level shift from CM5 3.3V GPIO.
- Use same 74AHCT1G125 or similar (can cascade multiple gates on same chip).
- Fan header: 2-pin (PWM, GND) or 3-pin (PWM, +5V, GND) depending on fan type.

### 2.4 HDMI Output (Constellation UI Display)
| Signal | CM5 Pin | Level | Icarus Connector | Notes |
|---|---|---|---|---|
| HDMI 2.1 D+/D- | JP2-? | LVDS (low-voltage) | HDMI Type-A connector (standard) | Standard 19-pin HDMI male, on PCB edge |
| DDC (I2C SDA/SCL) | JP2-? | 3.3V | HDMI pins 16/17 | Pull-ups on HDMI cable (typically) |
| CEC (optional) | JP2-? | 3.3V | HDMI pin 13 | Not required for initial design |

**HDMI Path:**
- RK3588S HDMI output is LVDS-based, requires no external swing adjustment.
- HDMI connector type: **Type-A male, flush-mount or right-angle (TBD based on PCB layout)**.
- Impedance: 100Ω differential for HDMI data, 100Ω for clock.
- **No HDCP required** (open-source Constellation UI, no content protection).
- DDC pull-ups: typically on display cable; if not present, add 4.7kΩ on Icarus for safety.

### 2.5 USB-C Connector (Power & Debug)
| Pin | Signal | Level | Icarus Circuit | Notes |
|---|---|---|---|---|
| 1,20 | GND | GND | USB-C shell → Main GND plane | |
| 4,9 | VBUS | 5V in | Schottky OR-gate (if barrel jack backup) or direct | Primary 5V source, 4A max |
| 2,3,10,11 | D+/D- | 3.3V | CP2102N USB-UART bridge | Debug serial port, also used for flashing via USB mass storage |
| 12-15 | DP0/DN0 (USB 3.0 SS) | 3.3V | Reserved for future USB 3.0 OTG | Not used in initial design |
| 18,19 | SBU1/SBU2 | — | No-connect (not needed) | |

**USB-C Power Input:**
- **5V fixed, no PD negotiation** — Icarus is a power sink only, not a source.
- Rated for 5V/4A = 20W max input (ample for 18W peak system draw).
- Connector: USB Type-C female, right-angle, 24-pin (full-featured, even if not all pins used).

### 2.6 UART Debug (Serial Console)
| Signal | CM5 Pin | Level | Icarus Component | Icarus Pin |
|---|---|---|---|---|
| UART_TX | JP3-? | 3.3V | CP2102N (RXD, pin 5) | Micro-USB or JST-SH connector |
| UART_RX | JP3-? | 3.3V | CP2102N (TXD, pin 4) | Micro-USB or JST-SH connector |
| GND | GND | — | CP2102N (pin 3) | — |

**CP2102N Details:**
- Silicon Labs USB-UART bridge, 3.3V logic, integrated DC-DC and oscillator.
- USB port: Micro-USB Type-B connector or JST-SH 4-pin (power, D+, D-, GND) for debug header.
- Baud rate: auto-detected or fixed at 1,500,000 bps (bootloader default for RK3588S).
- **Optional:** Add Reset and Boot0 push-buttons to Icarus for flashing without GUI tools (recommended for field updates).

### 2.7 Storage (M.2 or SATA SSD)
| Signal | CM5 Pin | Level | Icarus Connector | Notes |
|---|---|---|---|---|
| SATA0/PCIe2.0 TX/RX (×4) | JP1-? | LVDS/CML | M.2 Key M slot or SATA III connector | Mode selection: HW jumper or auto-detect |
| SATA1 (×4) | JP1-? | LVDS/CML | Optional secondary SATA or USB 3.0 (jumper selectable) | Future expansion |

**Storage Subsystem:**
- **Primary:** M.2 2280 (22mm × 80mm) NVMe SSD via PCIe 2.0 (×4 lanes = 250 MB/s).
  - Connector: standard M.2 Key M socket, PCB-mounted (90° angle recommended for compact form).
  - 3.3V power supply to M.2 module from CM5 3.3V rail.
- **Alternative:** SATA III if NVMe unavailable (e.g., legacy SSD). Separate mechanical design required.
- **Impedance:** 100Ω differential for PCIe TX/RX pairs.

### 2.8 Fan Control (PWM Header)
| Signal | CM5 Pin | Level | Header Pin | Notes |
|---|---|---|---|---|
| PWM | JP3-? | 3.3V (shifted→5V) | Pin 1 (signal) | Level shifted via 74AHCT1G125 |
| +5V | 5V rail | 5V | Pin 2 | Power directly from 5V rail (with inline fuse) |
| GND | GND | GND | Pin 3 | — |

**Fan Details:**
- Connector type: 3-pin JST-EH or Molex 4.2mm (standard PC fan header).
- Rated fan: 40mm or 50mm DC brushless, 5V, ~200 mA typical (assume peak 400mA for budget).
- PWM frequency: typically 25 kHz (CM5 can generate via GPIO or dedicated PWM pin).

### 2.9 Touch Sensor (Capacitive Button)
| Signal | CM5 Pin | Level | Icarus Component | Notes |
|---|---|---|---|---|
| TOUCH_OUT | JP3-? | 3.3V | TTP223 (INT pin) | Open-drain or CMOS output (TBD by variant) |
| GND | GND | — | TTP223 (GND) | — |

**TTP223 Configuration:**
- Single-button capacitive sensor IC, 2.4–5.5V supply (use 3.3V from CM5).
- Pad size on Icarus: **16×16mm square, top-layer copper, 1mm border for mechanical tolerance**.
- Output: active-low by default (INT goes low when touched).
- Mounting: soldered directly on Icarus PCB; protected by 1.6mm acrylic overlay or conformal coat.
- Optional: add bypass cap (0.1µF) on VDD near IC for noise filtering.

---

## 3. Power Architecture

### 3.1 Power Input & Distribution

**Primary Input: USB-C 5V @ 4A**
- Connector: USB Type-C female, right-angle, PCB-mounted.
- No power delivery (PD) negotiation; fixed 5V only.
- Inline fuse (Polyfuse): 6A hold current, 8A trip (60-second recovery).
- Input protection: TVS diode (SMAJ5.0A, SMD) across VBUS+GND for transient overvoltage.

**Optional Secondary Input: Barrel Jack 5V Backup**
- Connector: 5.5mm × 2.1mm, center-positive (standard).
- OR-gate: Schottky diodes (BAT54S or equiv) for 5V rail combining (VBUS and barrel jack in parallel).
  - Schottky forward drop: ~0.2V @ 2A (acceptable for system tolerance).
- **Action:** Decide during layout phase whether to include; recommended for field serviceability.

### 3.2 5V Rail (Primary Power Bus)
Supplies:
- **CM5 SOM:** 5V input via B2B connector (JP1), max 1800mA.
- **MAX98357A:** 5V speaker amp, ~2.5W continuous (peak 3.2W @ 4Ω).
- **WS2812B LED Ring:** ~0.6W @ 12 LEDs (60mA per full white).
- **5V Fan:** ~0.2–0.4W.
- **HDMI Connector:** ~0.1W (passive).
- **USB-C Connector:** Pull-up resistors, negligible (<0.01W).

**5V Rail Filtering:**
- Bulk capacitor (100µF, 6.3V), placed near USB-C input.
- Ceramic capacitors (10µF + 1µF) on CM5 side and near each active consumer (MAX98357A, fan).
- **Total allowance:** 20W (from 5V/4A USB-C input) is sufficient for system peak ~18W (see power budget below).

### 3.3 3.3V Rail (Logic & Sensors)
**Source:** CM5 SOM output, max 600mA.

Supplies:
- **SSD1306 OLED:** ~5mA @ 128×64 running.
- **INMP441 Microphone:** ~2mA @ 1.8V (but powered from 3.3V step-down or direct, TBD).
- **TTP223 Touch Sensor:** ~10µA sleep, ~5mA active.
- **Level Shifters (SN74LVC245, 74AHCT1G125):** ~5mA combined.
- **I2C pull-up resistors (2×4.7kΩ):** ~0.35mA @ 3.3V.
- **GPIO logic (UART, USB mux):** ~10mA.

**Total 3.3V budget:** ~35–40mA typical, well within 600mA CM5 output.

**3.3V Rail Filtering:**
- Ceramic capacitors (10µF + 1µF) distributed near major consumers.
- No additional inductor or DC-DC needed; CM5 output is clean.

### 3.4 1.8V Rail (CM5 I/O Reference)
**Source:** CM5 SOM output, max 600mA.

**Supplies:**
- **MAX98357A I2S logic:** ~5mA.
- **INMP441 (if powered from 1.8V variant):** ~2mA.
- **RK3588S internal I/O buffers:** already accounted in CM5 budget.

**1.8V Rail Filtering:**
- Ceramic capacitors (10µF + 1µF) near I2S interface.
- This rail is typically clean from CM5; minimal filtering required.

### 3.5 Power Budget Table

| Component | Voltage | Current (Typical) | Current (Peak) | Power (Typ) | Power (Peak) | Notes |
|---|---|---|---|---|---|
| **CM5 SOM** | 5V | 2000mA | 2400mA | 10.0W | 12.0W | RK3588S @ full load, Mali-G610, NPU |
| MAX98357A | 5V | 100mA | 650mA | 0.5W | 3.2W | Mono Class-D, 3.2W max into 4Ω load |
| INMP441 | 3.3V | 2mA | 2mA | 0.007W | 0.007W | MEMS PDM mic, stable draw |
| SSD1306 OLED | 3.3V | 5mA | 15mA | 0.017W | 0.05W | 128×64 display, varies by content |
| TTP223 Touch | 3.3V | 0.01mA | 5mA | <0.001W | 0.017W | Low-power capacitive sensor |
| WS2812B (12×) | 5V | 60mA | 360mA | 0.3W | 1.8W | Full white intensity (rare); typical ~0.3W avg |
| 5V Fan | 5V | 40mA | 200mA | 0.2W | 1.0W | 40mm DC fan, PWM modulated |
| Level Shifters | 3.3V | 5mA | 10mA | 0.017W | 0.033W | SN74LVC245, 74AHCT1G125 combined |
| UART/USB ICs | 3.3V | 10mA | 10mA | 0.033W | 0.033W | CP2102N oscillator + buffers |
| Passive (resistors, caps) | 3.3V/5V | 5mA | 5mA | 0.02W | 0.02W | Pull-ups, bypass caps, minor leakage |
| **SYSTEM TOTAL** | — | 2.2A (5V) | 3.6A (5V) | **11.1W** | **18.2W** | Peak occurs: CM5 + speaker + LEDs + fan simultaneous |

**Key Observations:**
- **5V input bus dominates:** 3.6A peak < 4A USB-C limit. Safe margin.
- **CM5 is the main load:** ~12W peak is ~67% of system budget.
- **LED ring peak (1.8W) is secondary:** rarely sustained; typical average ~0.3W.
- **Total system peak (18.2W) fits within 20W USB-C headroom.**

### 3.6 Power Sequencing & Soft Start
- **No special sequencing required:** CM5 handles its own internal rails; external 5V, 3.3V, 1.8V are passive outputs from SOM.
- **Soft-start:** CM5 powers on when 5V is applied. No manual startup circuit needed (SOM has internal POR logic).
- **Shutdown:** Pull POWER_ON signal (via test point or button) to put SOM into sleep mode (recommended for field shutdown).

---

## 4. PCB Design Constraints

### 4.1 Stackup & Layer Allocation
**4-Layer PCB (1.6mm total thickness):**

| Layer | Thickness | Purpose | Notes |
|---|---|---|---|
| **L1 (Top Signal)** | 0.15mm | Component placement, trace routing, high-speed signals (USB, HDMI) | 0.15mm minimum trace width |
| **L2 (GND Plane)** | 0.08mm | Ground reference plane, 2–4oz copper, solid except for via clearances | Via stitching every ~5mm |
| **L3 (Power Plane)** | 0.08mm | +5V and +3.3V distribution (can split or power zones with layer if needed) | Via stitching to L4 for power return |
| **L4 (Bottom Signal)** | 0.15mm | Component placement (optional), trace routing, return paths | Mostly GND return; secondary signal layer |

**Rationale:** 4-layer is minimum for mixed-signal board with audio (I2S) and USB 2.0 impedance control. 2-layer would require massive via density and is not recommended.

### 4.2 Impedance & High-Speed Routing

| Interface | Standard | Target Impedance | Trace Width (est.) | Via Clearance | Notes |
|---|---|---|---|---|---|
| **USB 2.0 (D+/D-)** | USB 2.0 Full-Speed | 90Ω differential | 0.20mm ± 0.05mm | 0.3mm min to signal | Tightly coupled pair, L2–L4 routing OK |
| **HDMI TX (×3 pairs + clock)** | HDMI 2.1 | 100Ω differential | 0.25mm ± 0.05mm | 0.4mm min to signal | May simplify to 100Ω single-ended if bandwidth allows |
| **PCIe 2.0 TX/RX (×4 lanes)** | PCIe 2.0 | 100Ω differential | 0.25mm ± 0.05mm | 0.4mm min to signal | Lower speed than PCIe 3.0; no exotic materials needed |
| **I2S (SCLK, LRCK, SDO/SDI)** | Audio I2S | 50–75Ω (not critical) | 0.30mm | 0.3mm | Low-frequency; not tightly routed |
| **I2C (SDA, SCL)** | I2C 100/400kHz | None (< 1 MHz) | 0.30mm | 0.3mm | Open-drain; no impedance control needed |

**Routing Rules:**
- **USB 2.0 pair:** Keep length-matched to within 2mm; route as tightly coupled pair on L1 with ground guard traces.
- **HDMI:** Similar to USB (3 data pairs + clock). Grouped routing, GND guard traces on sides.
- **Audio (I2S):** Route away from switching power supplies and LCD clock lines (no DC-DC or switcher in this design, so lower EMI risk).
- **Separation:** Keep analog audio (INMP441, MAX98357A) traces ≥5mm from digital high-speed (USB, HDMI) to minimize crosstalk.

### 4.3 Component Placement Rules

**Critical Placement (Non-Negotiable):**

| Component | Placement Rule | Reason | Board Location |
|---|---|---|---|
| **CM5 B2B Connectors (JP1, JP2, JP3)** | Exact center or offset per mounting hole pattern (55×40mm) | Mechanical fit with SOM; no tolerance for error | Center of board, aligned with holes |
| **USB-C Connector** | Edge of PCB, aligned with 5mm clearance to nearest B2B | Accessibility and cable routing | Top edge, center-right |
| **Barrel Jack (optional)** | Right edge of PCB, 10mm below USB-C | Visual separation, cable routing | Right edge |
| **M.2 Slot** | Parallel to board edge, 5mm clearance to nearest connector | Mechanical access for SSD insertion | Bottom edge, right side |
| **HDMI Connector** | Right-angle, flush to board edge, or 90° PCB edge connector | Display cable routing | Left or right edge |
| **CP2102N USB-UART** | Within 30mm of UART pins on JP3; input cap (0.1µF) and output cap (1µF) right-side placement | Minimize skew, reduce EMI | Bottom-left area |
| **MAX98357A** | Within 20mm of I2S pins; power cap (10µF + 1µF) and output LC filter adjacent | Minimize I2S trace length and parasitic inductance | Top-right area (near audio output) |
| **INMP441 Microphone** | ≥50mm from switching supplies (none here), ≥30mm from speaker amp | Acoustic isolation, reduce electrical crosstalk | Top-left or far corner from amp |
| **SSD1306 OLED** | Near I2C pins on JP3; decoupling cap (1µF) very close | Low-current display, minimal skew requirements | Any accessible area; top-left preferred for visibility |
| **TTP223 Touch Pad** | Front-center of board, visible for user touch access | Functional requirement | Center of top surface |
| **WS2812B Ring (10–12 LEDs)** | Arranged in circle, 30mm radius approx., centered on board | Aesthetic; light distribution around device | Perimeter of top surface |
| **Bulk Capacitors (100µF on 5V)** | Right at USB-C connector input | Minimize supply ripple at input | Top-left or top-right, next to USB connector |
| **Decoupling Caps** | Within 5mm of power input pin for each IC | Reduce voltage droop during transients | Adjacent to IC power pins |

**Recommended Layout Zones (100mm × 90mm board):**
```
  [USB-C]
    |
[5V BULK CAP] ... [HDMI or M.2] ... [Barrel Jack]
     |
  [JP2]----[JP1]----[M.2 Slot or SSD]
     |
  [CP2102N]
     |
  [JP3]
     |
[INMP441]   [TTP223 PAD]  [SSD1306 OLED display area]
     |           |
[MAX98357A]  [LED RING perimeter]
     |
  [FAN HEADER]
```

### 4.4 Via Strategy
- **Via size:** 0.3mm drill, 0.5mm pad (standard for 0.4mm pitch B2B tolerances).
- **Via stitching (GND):** Every ~5mm around power planes to maintain low impedance.
- **Thermal vias:** Under large ICs (MAX98357A, CP2102N), 4–9 vias per pad for thermal dissipation (not critical, but good practice).
- **Blind/buried vias:** Not required for 4-layer; standard through-vias sufficient.

### 4.5 Trace Routing Guidelines
- **Minimum trace width:** 0.15mm (4mil) for high-speed; 0.30mm (12mil) for general digital; 0.25mm (10mil) for audio analog.
- **Minimum spacing (clearance):** 0.15mm (6mil) between traces; 0.3mm (12mil) from high-speed to analog.
- **Via clearance to trace:** 0.3mm minimum to high-speed traces.
- **Solder mask:** Standard 0.1mm (4mil) clearance around pads.

### 4.6 PCB Materials & Manufacturing
- **Substrate:** FR-4, 1.6mm thickness (standard 2-oz copper).
- **Dielectric constant (Dk):** ~4.5 typical for FR-4 (affects impedance calculations).
- **Loss tangent (Df):** ~0.02 typical (low-loss for USB/HDMI).
- **Finish:** ENIG (Electroless Nickel Immersion Gold) recommended for reliability and solderability.
- **Solder mask:** Liquid photoimageable (LPI) or dry film, green or blue (standard).
- **Silkscreen:** White or yellow, minimum 0.3mm text size for readability.

---

## 5. Component Count Estimate

### 5.1 Components on Icarus (Carrier Board)

| Category | Component | Qty | Part Number (Reference) | Supplier | Notes |
|---|---|---|---|---|
| **Connectors** | USB-C female (right-angle) | 1 | TUSB2077I2ZRSLPGM | TI (USB SoC) *or* Hirose, Molex | USB 2.0 Type-C |
| | B2B Connectors (100-pin, 0.4mm pitch) | 3 | DF40C-100DP-0.4V(51) | Hirose | Matches CM5 |
| | M.2 2280 Key M Socket | 1 | 67910-1410 or equiv | Molex | For NVMe SSD |
| | HDMI Type-A (19-pin) | 1 | HDMI-A-F-RA (right-angle) | Generic | Video output |
| | 3-pin JST-EH Fan Header | 1 | SM03B-SRSS or equiv | JST | 5V fan connector |
| | DC Barrel Jack (5.5×2.1mm, optional) | 1 | PJ-002A | CUI Devices | Backup power input |
| | Debug Header (JST-SH 4-pin, optional) | 1 | SM04B-SRSS | JST | UART (alternative to micro-USB) |
| **ICs** | CP2102N USB-UART Bridge | 1 | CP2102N-A01-GQFR | Silicon Labs | QFN-28, 3.3V logic, integrated oscillator |
| | SN74LVC245 Level Shifter | 1 | SN74LVC245APWR | TI | TSSOP-20, for I2S and PWM shifting |
| | 74AHCT1G125 Buffer/Shifter | 2 | 74AHCT1G125GW | Nexperia | SOT-353 (single gate), 3.3V→5V for LED/PWM |
| **Audio ICs** | MAX98357A Class-D Amp | 1 | MAX98357AEVS | Maxim | QFN-16, stereo (use mono), 5V, I2S input |
| | INMP441 MEMS Mic | 1 | INMP441ACEZ-R7 | InvenSense | BGA-6, 3.3V, PDM output |
| **Displays & Sensors** | SSD1306 OLED (128×64 module, optional breakout) | 1 | SSD1306 + display assembly | Generic | 0.96" I2C-compatible, 3.3V |
| | TTP223 Capacitive Touch Sensor IC | 1 | TTP223-BA6 | TonTouchPad | SOP-8, 2.4–5.5V, GPIO open-drain output |
| | WS2812B RGB LED (addressable, 5050 package) | 12 | WS2812B-F8 | APA102 or Adafruit stock | 5V, integrated controller, daisy-chainable |
| **Passive — Resistors** | 4.7kΩ pull-up (I2C) | 2 | 4.7K 0603 (thick-film) | Generic | Standard tol. ±5%, for SDA/SCL |
| | 10kΩ pull-up (GPIO reset test point) | 1 | 10K 0603 | Generic | Optional, for reset line |
| | 470Ω series (LED ring) | 1 | 470 0603 | Generic | Current-limit resistor on WS2812B DIN |
| | 100Ω pull-down (optional, LED ring) | 1 | 100 0603 | Generic | Optional, for signal shaping |
| **Passive — Capacitors** | 100µF / 6.3V bulk (5V rail) | 1 | 100µ 0805 X5R | Generic | Electrolytic or ceramic (X5R) |
| | 10µF / 6.3V decoupling | 5 | 10µ 0603 X7R | Generic | Near CM5, MAX98357A, others |
| | 1µF / 6.3V bypass | 8 | 1µ 0603 X7R | Generic | Signal integrity caps near each IC |
| | 0.1µF / 6.3V high-freq bypass | 10 | 0.1µ 0603 X7R | Generic | Near power pins, standard digital bypass |
| **Protection** | Polyfuse (5V input, 6A hold) | 1 | MF-R600/6A or equiv | Belfuse, Littelfuse | Resettable, SMD 1206 footprint |
| | TVS Diode (5V, bidirectional) | 1 | SMAJ5.0A | STMicroelectronics | SMD, transient over-voltage protection |
| | Schottky Diode (OR-gate for barrel jack, optional) | 2 | BAT54S | ON Semiconductor | SOT-23, low forward drop (~0.2V @ 2A) |
| **Other** | Ferrite Bead (USB D+/D- pair, optional) | 1 | MURATA BLM15BD102SN1 | Murata | Reduces EMI on USB lines |
| | Mechanical Mounting Spacers | 3 | M2.5 hex standoff, nylon | Generic | For CM5 clearance above PCB |
| **Enclosure (optional)** | 3D-printed or machined housing | 1 | Custom STL (TBD) | — | ~100×90×30mm outline |

**Total Component Count (Icarus alone):** ~60 unique components, ~100+ individual parts.

### 5.2 Components on CM5 SOM (Already Integrated)
| Feature | Component | Notes |
|---|---|---|
| **Main SoC** | RK3588S | Quad A76 + Quad A55, Mali-G610, 6 TOPS NPU |
| **Memory** | 8GB LPDDR4X | Soldered on SOM |
| **Storage** | 32GB eMMC | Soldered on SOM (or blank variant for external storage only) |
| **Wireless** | 2T2R WiFi 6 (802.11ax) + BT 5.2 | Onboard module, external antenna options |
| **Power Regulators** | Multi-phase buck (5V → 1.2V core, 0.9V GPU, etc.) | Integrated on SOM |
| **Clocks & Oscillators** | 24MHz crystal, PLL circuits | Integrated on SOM |
| **USB 2.0 PHY, HDMI PHY, PCIe PHY** | Multiple interface transceivers | Integrated on SOM |
| **DRAM Termination, ESD Arrays** | Passive arrays, TVS diodes | Integrated on SOM |

**Icarus adds:** Peripherals (audio, display, LEDs, microphone, touch, storage interface) and system-level connectors.

---

## 6. Board Outline and Connector Placement

### 6.1 Board Dimensions
- **Target size:** 100mm × 90mm (slightly larger than official Orange Pi base board 90mm × 66mm to accommodate extras).
- **Thickness:** 1.6mm (standard PCB).
- **Corners:** Rounded 2mm (optional, for aesthetic finish).
- **Mounting holes:** 3× M2.5 (aligned with CM5 hole pattern at 55mm × 40mm spacing).

### 6.2 ASCII Layout (Top View, Not to Scale)
```
                      100mm (width)
    ┌──────────────────────────────────────────────┐
    │                                              │ 10mm
    │   [USB-C]                    [BARREL JACK]  │
    │                                              │
    │                                              │
    │   [5V BULK CAP]                             │
    │                                              │ 45mm
    │   ┌──────────────────────────────────────┐  │
    │   │  [JP2]      [CM5]      [JP1]         │  │
    │   │  100-pin    55×40mm    100-pin       │  │
    │   │  (USB,      ┌────┐     (Power,       │  │
    │   │   HDMI)     │ SOM│     Storage)      │  │
    │   │             └────┘                   │  │
    │   │  [JP3]      [M.2 SLOT]               │  │
    │   │  100-pin    (NVMe SSD)               │  │
    │   │  (Audio,    ┌────────┐               │  │
    │   │   I2C,      │ 2280   │               │  │
    │   │   GPIO)     └────────┘               │  │
    │   └──────────────────────────────────────┘  │
    │                                              │ 80mm
    │   [INMP441]      [TTP223 PAD]               │
    │   (Mic IC)      (Touch Button)              │
    │                                              │
    │   [MAX98357A]   [SSD1306 OLED]              │
    │   (Amp IC)      (Display)                   │
    │                                              │ 10mm
    │   [FAN HEADER]  [LED RING PERIMETER]        │
    │                 (12× WS2812B)               │
    │                                              │
    └──────────────────────────────────────────────┘
                        90mm (height)

Key Connectors on Edges:
  TOP:    USB-C (center-right), Barrel Jack (right), HDMI (left)
  RIGHT:  M.2 Socket (flush edge), Debug Header (optional, lower right)
  BOTTOM: Fan Header (left), other test points
  LEFT:   Reserved for future expansion
```

### 6.3 Connector Details & Edge Placement

| Connector | Type | Edge | Position | Orientation | Clearance |
|---|---|---|---|---|---|
| **USB-C** | Type-C female, 24-pin | Top | Center-right (x=65mm from left) | Horizontal flush | 5mm to nearest trace |
| **Barrel Jack** | 5.5×2.1mm (optional) | Top | Right edge (x=90mm) | Horizontal | 5mm to USB-C |
| **HDMI** | Type-A 19-pin (right-angle) | Left | Center (y=45mm from top) | Angled outward | 3mm to PCB edge |
| **M.2 Socket** | 67910-1410 key M | Bottom | Right side (x=80mm) | Perpendicular to edge | 2mm clearance for SSD thickness (3.8mm) |
| **Fan Header** | JST-EH 3-pin | Bottom | Left side (x=10mm) | Vertical | 2mm to edge |
| **Debug Header** (optional) | JST-SH 4-pin | Bottom-right | Lower right (x=85mm, y=85mm) | Horizontal | 3mm to M.2 slot |

### 6.4 Component Placement on Top Surface

| Component | Footprint | Location | Notes |
|---|---|---|---|
| **CP2102N** | QFN-28 (5×5mm) | Bottom-left quadrant (x=12, y=75) | Decoupling caps immediately adjacent |
| **MAX98357A** | QFN-16 (4×4mm) | Bottom-right quadrant (x=80, y=75) | Audio output connector area |
| **SN74LVC245** | TSSOP-20 (6.5×7mm) | Center (x=45, y=70) | Between I2S sources and destinations |
| **74AHCT1G125** (×2) | SOT-353 (1.5×2.5mm each) | Near LED ring and fan (x=20, y=15 and x=70, y=15) | Minimal trace length to shifting nodes |
| **INMP441** | BGA-6 (2.8×2.8mm) | Top-left corner (x=10, y=15) | Far from MAX98357A for acoustic isolation |
| **TTP223** | SOP-8 (5.3×5.3mm) | Center-top (x=50, y=20) | Visible for user interaction |
| **SSD1306** | 0.96" module (27×27mm) or bare IC (SOC-20) | Top-center (x=35, y=25) | Optional; can be standalone breakout |
| **WS2812B LEDs** | 5050 (5×5mm each) | Ring perimeter (radius ~30mm from center) | 12 units arranged in circle |
| **Resistors & Caps** | 0603, 0805, 1206 | Distributed near their associated ICs | Standard SMD placement rules |
| **Polyfuse & TVS** | 1206, SOT-23 | Near USB-C input (top-left area) | Protection circuit entry point |
| **Schottky Diodes** (optional) | SOT-23 | Top-right (if barrel jack included) | OR-gate for dual-input power |

---

## 7. Risk Register

### Overview
Identified risks during design phase, with mitigation strategies. All are manageable with standard engineering practices.

| Risk ID | Description | Severity | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| **R1** | **I2S Level Mismatch (INMP441 3.3V → CM5 1.8V)** | Medium | High | Audio input clipping or data loss | Confirm PDM mode availability on RK3588S; if yes, use PDM directly (no I2S shifter). If no, add SN74LVC245 level shifter (1.8V→3.3V). Test with scope. | HW Lead | In Review |
| **R2** | **USB Impedance Margin (90Ω ±10%)** | Low | Medium | Signal integrity failure on USB 2.0 flashing | PCB stackup must be verified in Gerber review. Use field solver (e.g., Hyperlynx) if available. Tolerance ±5% is achievable with FR-4 Dk=4.5±0.1. Prototype test with signal analyzer. | PCB Lead | Pending Fabr. |
| **R3** | **Thermal (CM5 Peak 12W on 5V)** | Medium | Medium | Overheating under sustained load or in sealed enclosure | Ensure 5V supply can deliver 2.4A stable (USB-C 4A is sufficient). Recommend active airflow (5V fan recommended, now in BOM). Heatsink on RK3588S is optional but encouraged. Add thermal simulation for enclosure TBD. | Mech Lead | In Progress |
| **R4** | **microSD Card Slot Reliability** | Low | Low | SD card detection failures (moisture, contact wear) | Use 8-pin push-push microSD connector (TE Connectivity or equiv) with gold contacts. Conformal coat connector if exposed to humidity. Test insertion/removal cycles (100+ cycles). | HW Lead | Pending Prototype |
| **R5** | **I2C Address Collision** | Low | Low | Multiple devices fighting for same I2C address (e.g., SSD1306 at 0x3C, future sensor also 0x3C) | SSD1306 at 0x3C (fixed by HW). Reserve next device addresses (0x3D, 0x4x–0x7x). Firmware must enumerate on boot. Avoid hot-plugging devices without address conflict checks. | Firmware | Not Started |
| **R6** | **GPIO Availability for LED Ring & Touch** | Low | Medium | Not enough GPIO pins on CM5 for WS2812B + TTP223 + PWM fan + test points | RK3588S has ≥100 GPIO. Confirm allocation in device tree. PWM fan shares pin with LED ring only if multiplexed in firmware (not recommended); provide separate GPIO. Test GPIO matrix in u-boot. | Firmware | Pending Sch. |
| **R7** | **Power Loss During M.2 Write** | Low | Medium | SSD corruption if 5V rail browns out during NVMe flush | Add 100µF bulk cap at USB-C input to ride through micro-interruptions (< 100ms). Test with load transient (switch LED ring on/off while writing). Monitor 5V rail with scope. Firmware should handle power-loss gracefully (ext4 fsync). | HW + FW | In Progress |
| **R8** | **HDMI Cable Shorts** | Medium | Low | User connects incompatible adapter; damages HDMI PHY on CM5 | No hardware mitigation (HDMI is standardized). Recommend only certified cables in user docs. Add ESD protection (Schottky clamp) if budget allows (not in BOM, optional). Test with ESD gun (±8kV air discharge per IEC 61000-4-2). | HW + Docs | Pending |
| **R9** | **CP2102N Oscillator Jitter** | Low | Low | UART baud rate inaccuracy (e.g., 1.5M bps deviates >5%) | CP2102N integrates oscillator ±2% tolerance (typical). Test with known bitrate source (function gen). If jitter observed, consider external 24MHz crystal on L4 as fallback (not included in BOM). | FW Validation | Pending Prototype |
| **R10** | **WS2812B Timing Sensitivity** | Low | Medium | LED flicker or color shifts due to bitstream jitter | WS2812B requires strict 800kHz ±5% bitrate and sub-µs rise/fall times. Use DMA or hardware SPI on RK3588S (check if available in CM5 device tree). Firmware must disable interrupts during bit transmission. Test timing with logic analyzer. | Firmware | Not Started |
| **R11** | **INMP441 Acoustic Crosstalk** | Medium | Medium | Speaker audio bleeds into microphone; echo during recording | Place INMP441 ≥50mm from MAX98357A. Use separate GND return paths (minimize loop area). Conformal coat INMP441 to reduce acoustic coupling. Add software HPF in firmware to suppress < 100Hz noise. Prototype testing recommended. | HW + FW | In Progress |
| **R12** | **Mechanical Fit (B2B Connectors)** | High | Medium | CM5 SOM not mating properly; poor electrical contact | Connectors (DF40C-100DP-0.4V) are spec'd by Orange Pi. Verify exact mounting hole locations (55mm × 40mm, M2.5). Test fit with mechanical proto. Spacers must be exact height (TBD from SOM thickness + standoff height). | Mech Lead | Pending Sch. |
| **R13** | **USB-C Polarity & Power Delivery** | Medium | Low | User plugs into USB PD source expecting negotiation; damage or fire | Icarus has NO PD support (fixed 5V only). Mark USB-C clearly "5V Power Input Only" on silkscreen and docs. Consider adding resistor dividers on CC lines to present "power sink only" profile (optional; not in BOM). Test with common PD chargers (anecdotal reports of 9V injection). | HW + Docs | Pending |
| **R14** | **Layout Underestimation** | Medium | High | PCB layout cannot fit all components in 100×90mm; design must squeeze or go 2-sided | 4-layer with careful placement is sufficient (estimate ~600–700 components' worth of real estate). Early layout mockup (CAD) strongly recommended. If needed, can extend to 110×100mm (still portable). | PCB Lead | In Progress |
| **R15** | **Firmware Bring-up Delays** | Low | High | CM5 lacks u-boot/kernel support for Icarus peripherals; delayed time-to-market | RK3588S u-boot/kernel are upstream (mainline Linux support strong). I2S, I2C, GPIO, USB are mature. Peripheral drivers (SSD1306, INMP441, TTP223) are community standard. Worst case: 2–3 weeks driver porting. Recommend starting firmware early. | Firmware | Not Started |

---

## 8. Design Sign-Off Checklist

- [ ] CM5 SOM official schematic and mechanical drawing obtained and reviewed.
- [ ] B2B connector pin mapping validated against Orange Pi documentation.
- [ ] Audio level-shifting strategy confirmed (PDM vs I2S with SN74LVC245).
- [ ] Power budget simulation completed; 5V/4A USB-C input confirmed sufficient.
- [ ] PCB stackup and impedance control plan finalized (field solver optional).
- [ ] Component datasheets reviewed for voltage ratings, thermal dissipation, and pinouts.
- [ ] Bill of Materials (BOM) finalized and priced; all components in stock or short lead-time.
- [ ] Schematic capture phase completed with full ERC checks.
- [ ] Layout mockup (CAD) confirms mechanical fit within 100×90mm target.
- [ ] Gerber review and DFM (Design for Manufacturability) checks passed.
- [ ] Prototype PCB ordered and scheduled for assembly.
- [ ] Test plan drafted (power, USB flashing, audio, display, LEDs, touch, storage).
- [ ] Risk mitigation tasks assigned and tracked.
- [ ] Documentation (user manual, driver setup, assembly guide) started.

---

## Appendix A: Reference Documents

- **Orange Pi CM5 Documentation:** https://github.com/orangepi-xunlong/OrangePiRK3588 (device tree, schematics TBD)
- **RK3588S Datasheet:** Rockchip official (contact Rockchip for NDA).
- **DF40C-100DP-0.4V(51) Connector:** Hirose DF40 series (0.4mm pitch).
- **MAX98357A Audio Amp:** Maxim Integrated, I2S interface, 3.2W Class-D.
- **INMP441 Microphone:** InvenSense PDM/I2S MEMS mic, 3.3V.
- **SSD1306 OLED:** 128×64, I2C interface, typical 0.96" module.
- **TTP223 Touch Sensor:** TonTouchPad, capacitive single-button IC.
- **WS2812B LED:** Addressable RGB (GRB), 5V, 800kHz bitstream.
- **CP2102N UART Bridge:** Silicon Labs, USB-UART converter, 3.3V.

---

## Appendix B: Glossary & Abbreviations

| Term | Definition |
|---|---|
| **B2B** | Board-to-Board connector |
| **CM5** | Orange Pi Compute Module 5 |
| **Icarus** | Custom Icarus carrier board (this design) |
| **RK3588S** | Rockchip SoC, quad A76 + quad A55 ARM cores |
| **NPU** | Neural Processing Unit (6 TOPS on RK3588S) |
| **eMMC** | Embedded MultiMediaCard (32GB onboard CM5) |
| **HDMI 2.1** | High-Definition Multimedia Interface rev. 2.1 |
| **MIPI** | Mobile Industry Processor Interface (CSI, DSI) |
| **I2S** | Inter-IC Sound (audio protocol) |
| **I2C** | Inter-Integrated Circuit (low-speed serial bus) |
| **UART** | Universal Asynchronous Receiver-Transmitter (debug console) |
| **PCIe** | PCI Express (for M.2 NVMe SSD) |
| **SSD** | Solid State Drive |
| **LVDS** | Low-Voltage Differential Signaling |
| **PDM** | Pulse Density Modulation (digital audio format) |
| **DMA** | Direct Memory Access |
| **TVS** | Transient Voltage Suppression (protection diode) |
| **ESD** | Electrostatic Discharge |
| **DFM** | Design For Manufacturability |
| **ENIG** | Electroless Nickel Immersion Gold (PCB finish) |
| **FR-4** | Fiberglass-reinforced epoxy PCB material |

---

**Document prepared by:** Hardware Design Team  
**Last updated:** 2026-03-14  
**Next review:** Post-schematic capture (target: 2026-03-28)

