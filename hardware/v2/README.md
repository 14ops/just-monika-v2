# Icarus v2 — Modular Compute Platform (Hardware)

Target: Stasis hackathon, May 15 2026. 10 PCB modules stacked on a 40-pin bus. $265.94 BOM against $300 budget.

Authoritative architecture + BOM: [`../../CLAUDE.md`](../../CLAUDE.md).

## Directory layout
```
hardware/v2/
├── README.md           # This file
├── BUS.md              # 40-pin bus spec + design rules (contract all modules follow)
├── STACKUP.md          # JLCPCB 2L/4L/6L stackups (TODO)
├── lib/                # Shared KiCad symbols + footprints
│   └── (TODO: 40-pin stacking header, M2.5 mounting-hole pattern, ECP5-45F BGA-256 if not in stdlib)
├── panel/              # Multi-module panelization scripts (TODO)
└── modules/
    ├── m1-processor/    # ESP32-S3-WROOM-1-N16R8 + OV2640 + CH340C
    ├── m2-power/        # HUSB238 USB-C PD + TPS63020 + TP4056 + INA219 + 18650
    ├── m3-sensor/       # ESP32-C6-MINI-1 + MPU6050 + BH1750 + BME280
    ├── m3a-audio/       # 2× INMP441 + MAX98357A
    ├── m4-fpga/         # ECP5 LFE5U-45F BGA-256 + HyperRAM + W25Q128 + DDR2 SODIMM (6L)
    ├── m5-usb2-hub/     # USB2514B + ESD + 2× USB-A (6L)
    ├── m6-io-expander/  # MCP23017 + Grove I2C + GPIO (2L)
    ├── m7-coral-carrier/# USB-A for Coral (USB 3.0 path)
    ├── m8-highspeed/    # TUSB8020B USB 3.0 hub + PCIe x1 edge (6L)
    └── m9-display/      # E-Ink FeatherWing + microSD (2L)
```

## Module quick-reference

| # | Dir | Layers | Purpose | Primary IC(s) | Subtotal |
|---|---|---|---|---|---|
| M1 | `modules/m1-processor/` | 4L | Main MCU, camera, debug | ESP32-S3-WROOM-1-N16R8, OV2640 | $11.45 |
| M2 | `modules/m2-power/` | 4L | PD negotiation, rails, battery mgmt | HUSB238, TPS63020, TP4056 | $15.10 |
| M3 | `modules/m3-sensor/` | 4L | I2C sensor hub, WiFi6/BLE | ESP32-C6-MINI-1, BME280, MPU6050 | $13.80 |
| M3A | `modules/m3a-audio/` | 4L | I2S stereo mic + amp | INMP441 ×2, MAX98357A | $12.50 |
| M4 | `modules/m4-fpga/` | **6L** | Programmable logic + DDR2 | ECP5 LFE5U-45F BGA-256 | $41.00 |
| M5 | `modules/m5-usb2-hub/` | **6L** | USB 2.0 peripheral expansion | USB2514B | $16.20 |
| M6 | `modules/m6-io-expander/` | 2L | I2C GPIO + Grove | MCP23017 | $6.20 |
| M7 | `modules/m7-coral-carrier/` | 4L | Dedicated USB 3.0 to Coral | USB-A + ESD | $6.00 |
| M8 | `modules/m8-highspeed/` | **6L** | USB 3.0 hub + PCIe x1 | TUSB8020B | $16.00 |
| M9 | `modules/m9-display/` | 2L | E-Ink + microSD | E-Ink FeatherWing | $37.00 |

## Recommended implementation order
1. **`lib/`** — shared 40-pin stacking header symbol + footprint, M2.5 mounting-hole pattern. Every module imports these.
2. **M2 (Power)** — simplest module with real parts, proves the bus convention end-to-end before committing to BGA work.
3. **M6 or M7** — both trivially small; finish the bus-bringup pattern.
4. **M1 (Processor)** — first module with an MCU, validates firmware toolchain against v2 pinout.
5. **M3, M3A, M9** — low-speed modules, relatively independent.
6. **M5, M8** — 6L USB diff-pair modules, need impedance-controlled stackup from STACKUP.md.
7. **M4 (FPGA)** — last because it's the biggest risk (BGA-256 + DDR2 + 6L) and depends on bus signal integrity already proven.

## Current status
- [x] Scaffold directories
- [x] 40-pin bus spec (`BUS.md`) — done
- [ ] JLCPCB stackup choices (`STACKUP.md`)
- [ ] Shared KiCad library (`lib/`)
- [x] Per-module schematic scaffolds (`modules/*/SCHEMATIC.md`)
- [x] Per-module KiCad project skeletons (`modules/*/*.kicad_pro`)
- [x] Per-module KiCad schematic skeletons (`modules/*/*.kicad_sch`)
- [x] Per-module PCB placeholders (`modules/*/*.kicad_pcb`)
- [ ] Per-module layouts (all 10)
- [ ] Panel + Gerbers

Module folders now contain schematic scaffold docs. KiCad projects will be created per-module as we go.

## Do NOT reuse from v1
- `hardware/DESIGN-HANDOFF.md` (single 8-layer board description)
- Anything under the nested `just-monika/just-monika/hardware/` clone (boardsmith panels, old 4-module ESP32-P4 Gerbers)
- Schematics referencing ESP32-WROOM-32, ESP32-P4, SSD1306, SSD1680, CELUS symbol library
