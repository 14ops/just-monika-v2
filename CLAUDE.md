# Modular Compute Platform (v2)

## Project Overview
10-module stackable compute platform for a local AI companion ("Just Monika" — anti-laziness personality, 100% on-device). **Modularity > processing > everything else.** $300 budget, Stasis hackathon May 2026 deadline.

Ground truth: `C:\Users\Seth\Downloads\modular_compute_platform_bom_v2.xlsx` + `C:\Users\Seth\Downloads\modular_pcb_framework_files\`.

All prior docs (old CLAUDE.md claiming 8-layer single-board ESP32-P4 + BGA ECP5, `just-monika2` repo, `monika11`, nested clone at `just-monika/just-monika/`) are **stale** and should not be used as a reference without explicit re-confirmation.

## Architecture
10 PCB modules stacked via a standardized **40-pin bus** (2×20 headers, 0.1" pitch) + M2.5×11mm brass standoffs. Assumed module footprint 60×50mm (from v1 framework files; confirm for v2). Design goal: any module is independently swappable.

### Module breakdown (v2 BOM)

| # | Module | Layers | Key parts | Subtotal |
|---|---|---|---|---|
| M1 | Processor | 4L | **ESP32-S3-WROOM-1-N16R8** (16MB flash, 8MB PSRAM), OV2640 camera (DVP), CH340C USB-UART | $11.45 |
| M2 | Power | 4L | HUSB238 USB-C PD (5/9/12/15/20V), TPS63020 buck-boost → 3.3V, TP4056 + DW01A/FS8205A, INA219, 18650 | $15.10 |
| M3 | Sensor | 4L | **ESP32-C6-MINI-1** (WiFi6/BLE/Thread), MPU6050, BH1750, BME280 (all I2C) | $13.80 |
| M3A | Audio | 4L | 2× INMP441 MEMS mics (I2S stereo), MAX98357A Class-D amp | $12.50 |
| M4 | FPGA | **6L** | **Lattice ECP5 LFE5U-45F BGA-256** (44K LUTs, direct solder, no ZIF), 64MB HyperRAM (IS66WVH8M8BLL), W25Q128 flash, AP2112K-1.1 LDO, 2× PMOD, **1× DDR2 SODIMM socket**, JTAG | $41.00 |
| M5 | USB 2.0 Hub | **6L** | USB2514B 4-port hub, 24LC02B EEPROM, 12 MHz xtal, 4× TPD4E05U06 ESD, 2× expansion USB-A (peripherals, **not** Coral) | $16.20 |
| M6 | I/O Expansion | **2L** | MCP23017 I2C GPIO expander (replaces old ATmega328P — zero firmware), 2× Grove I2C, 2× 1×8 GPIO | $6.20 |
| M7 | Coral Carrier | 4L | USB-A receptacle + TPD4E05U06 ESD. Dedicated USB 3.0 path for Coral. | $6.00 |
| M8 | High-Speed Data | **6L** | TUSB8020B USB 3.0 hub, PCIe x1 edge connector | $16.00 |
| M9 | Display | **2L** | 2.13" E-Ink FeatherWing (250×122, SPI), microSD breakout | $37.00 |

Standalone/shared: Coral USB Accelerator ($59.99), passives kit, jumper kit, 32GB microSD, u.FL WiFi antenna, 18650 cell + holder, 12× standoffs, 12× screws. Subtotal **$90.69**.

**Grand total: $265.94 / $300** (remaining $34.06). User owns 2× DDR2 (1 used, 1 spare) + 2× DDR4 (reserved for future CertusPro-NX / Artix-7 upgrade — **ECP5 cannot drive DDR4**).

### 40-pin bus pinout (2×20, 0.1")

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | 3V3 | 2 | 5V |
| 3 | 3V3 | 4 | 5V |
| 5,7 | GND | 6,8 | GND |
| 9 | SPI_CLK | 10 | SPI_MOSI |
| 11 | SPI_MISO | 12 | SPI_CS0 |
| 13 | SPI_CS1 | 14 | SPI_CS2 |
| 15 | I2C_SDA | 16 | I2C_SCL |
| 17 | I2C2_SDA | 18 | I2C2_SCL |
| 19 | UART_TX | 20 | UART_RX |
| 21 | UART2_TX | 22 | UART2_RX |
| 23 | USB_D+ | 24 | USB_D- |
| 25 | USB3_TX+ | 26 | USB3_TX- |
| 27 | USB3_RX+ | 28 | USB3_RX- |
| 29 | INT0 | 30 | INT1 |
| 31 | INT2 | 32 | RESET_N |
| 33 | I2S_BCLK | 34 | I2S_LRCLK |
| 35 | I2S_DIN | 36 | I2S_DOUT |
| 37 | GPIO_A | 38 | GPIO_B |
| 39,40 | GND | | |

Allocation: 4× power, 6× GND, 6× SPI, 4× I2C (2 buses), 4× UART (2 buses), 6× USB (2.0 + 3.0), 4× I2S, 3× interrupt, 1× reset, 2× GPIO.

## Current Status (2026-04-20)
- **BOM v2:** DONE (spreadsheet above)
- **Framework guide:** draft exists; all fabrication/wiring/bring-up/assembly steps marked *"(not yet generated)"*
- **Per-module schematic scaffolds:** DONE for all 10 modules
- **Per-module KiCad project skeletons:** DONE for all 10 modules
- **Per-module KiCad schematics:** scaffolded against v2
- **Per-module PCB placeholders:** DONE for all 10 modules
- **PCB layouts:** NOT STARTED
- **Gerber generation:** NOT STARTED
- **Fab order:** NOT PLACED
- **Firmware:** NOT STARTED against v2 (old `just-monika2` repo has firmware targeting ESP32-P4 — now obsolete since M1 is ESP32-S3)

## Routing Priority (per-module, once layout begins)
1. **Power rails** — 5V, 3.3V, 1.1V (M4 core), GND pours. Thick traces on M2.
2. **M4 DDR2** — impedance-controlled, length-matched. Reason M4 is 6L.
3. **M5 USB 2.0 diff pairs** — 90Ω differential. Reason M5 is 6L.
4. **M8 USB 3.0 + PCIe** — 90Ω USB3 diff, 85Ω PCIe diff. Reason M8 is 6L.
5. **M7 Coral USB path** — USB 3.0 from M8 through M7 to Coral socket.
6. **40-pin bus traces** — keep signal integrity across stacking headers (watch stub lengths).
7. **Low-speed** (I2C, I2S, SPI, UART, GPIO) — everything else.

## Key Constraints
- **Coral gets USB 3.0** via dedicated M7 carrier, not shared with peripherals.
- **ECP5-45F is solder-down BGA-256** (no ZIF socket — that was cut as unreliable).
- **DDR4 sockets are cut**; only DDR2 is supported by ECP5.
- M6 and M9 are 2-layer only — keep them to I2C/low-speed SPI.
- Every module has a 2×20 stacking header and 4 mounting holes for M2.5 standoffs.
- Budget ceiling: $300. Current: $265.94 with $34.06 of headroom for resistor/cap overruns or fab upcharges.

## AI Stack (carried over, needs re-validation against v2)
- Whisper STT, Kokoro/Edge TTS, Llama 3.2 3B via Ollama (server-side over WiFi, per old `just-monika2/firmware/esp-idf/components/llm_client.c`)
- Personality/memory system was written for ESP32-P4 in `just-monika2`. **Needs re-port to ESP32-S3** (less PSRAM — 8MB vs 32MB on P4).
- FPGA (M4 ECP5-45F) likely hosts audio DSP (I2S routing / Whisper acceleration) — architecture not yet re-specified for v2.

## Tools
- KiCad 9.0 (per-module schematic + layout)
- FreeRouting v2.1.0 (autorouter, DSN/SES workflow) — may be overkill for 4L/2L modules
- JLCPCB (fabrication, SMT assembly; BGA X-ray for M4 ECP5)
- ESP-IDF (firmware — now targeting ESP32-S3 on M1 and ESP32-C6 on M3)
- Lattice Diamond or open-source Yosys + nextpnr-ecp5 (FPGA synthesis for M4)

## File Structure
```
C:\Users\Seth\just-monika\
├── CLAUDE.md                    # This file
├── JOURNAL.md
├── hardware/
│   ├── DESIGN-HANDOFF.md        # Stale — describes old 8-layer single-board design
│   └── python.code-workspace
├── just-monika/                 # ⚠️ Nested clone of 14ops/just-monika2 (stale v1 project)
├── skidl_REPL.erc, *.log        # SKiDL artifacts
└── (v2 KiCad projects: not yet created)

C:\Users\Seth\Downloads\
├── modular_compute_platform_bom_v2.xlsx     # ← v2 ground truth
└── modular_pcb_framework_files\
    ├── modular_pcb_framework_BOM.csv        # v1 framework BOM (4 modules — stale)
    ├── modular_pcb_framework_CONFIG.json    # Component/footprint specs (partially applicable)
    ├── modular_pcb_framework_ELECTRICAL_CONNECTIONS.json
    ├── modular_pcb_framework_MECHANICAL_CONNECTIONS.json
    ├── modular_pcb_framework_GUIDE.md       # Assembly steps (all "not yet generated")
    └── modular_pcb_framework_VISUAL.png     # Render of stacked cube
```

## Known Open Questions (flag before assuming)
1. Module footprint for v2 — is it still 60×50mm like v1, or re-sized to accommodate M4 BGA-256 + DDR2 socket + M8 PCIe edge?
2. Vertical stack order — old viz showed M1 top → M4 bottom. With 10 modules, stack order + thermal strategy (TP4056, TPS63020, ECP5) needs a new ADR.
3. Where does Monika persona/memory code live across M1 (ESP32-S3) vs. host inference over WiFi? ESP32-S3's 8MB PSRAM is a constraint.
4. M4 SODIMM socket orientation: does it fit within the module footprint above the header, or overhang?
5. Is Module 5 (USB 2.0 hub) actually needed if M7 gives Coral its own USB3 and M1 only has DVP/SPI peripherals? — worth re-examining.

## Common Tasks You Might Help With
- Generating per-module KiCad schematics from the v2 BOM
- Designing the 40-pin bus distribution + stacking order
- Impedance stackup for 6L modules (M4/M5/M8) against JLCPCB 6L templates
- Porting old ESP-IDF firmware from ESP32-P4 → ESP32-S3 (8MB PSRAM budget)
- Yosys/nextpnr build for ECP5-45F (audio DSP pipeline)
- Thermal simulation for the stacked cube (TPS63020 + ECP5 + USB hubs)
