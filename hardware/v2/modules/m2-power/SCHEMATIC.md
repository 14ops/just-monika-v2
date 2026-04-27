# M2 — Power Module (Schematic Plan)

> **Status:** draft / not yet in KiCad. This doc is the pin-level contract we'll implement.
> **Layers:** 4L. **Footprint:** 60×50mm. **BOM subtotal:** $15.10.

M2 is the **only** module on the stack that sources 3V3 and 5V to the bus. It handles USB-C PD negotiation, Li-ion charging, battery protection, current telemetry, and 3V3/5V regulation.

## Power tree

```
          USB-C VBUS (5/9/12/15/20V PD)
                      │
                 ┌────┴────┐
                 │ HUSB238 │  (I2C-configured PDO selection)
                 └────┬────┘
                      │  VBUS_PD  (nominal 5V, but PDO-dependent)
         ┌────────────┼────────────┐
         │            │            │
    ┌────┴────┐  ┌────┴────┐       │
    │  TP4056 │  │TPS63020 │       │  (INA219 sits in-line on V5_BUS
    │ charger │  │ buck-   │       │   high-side shunt — see below)
    └────┬────┘  │  boost  │       │
         │       └────┬────┘       │
    VBAT_CHG          │            │
         │          V5_BUS ────────┤──→ bus pins 2, 4
    ┌────┴────┐       │            │
    │ DW01A + │       │            │
    │ FS8205A │       │       ┌────┴─────┐
    │ protect │       │       │AP2112K-33│
    └────┬────┘       │       │  LDO     │
         │            │       └────┬─────┘
       VBAT           │            │
         │            │        V3V3_BUS ──→ bus pins 1, 3
      [18650]         │
                      │
                   TPS63020 input: VBAT (when USB detached) OR VBUS_PD (when attached)
                   → OR-ing handled by TPS63020 input MUX + ideal diode (see "Power path" §)
```

## Power path — USB vs battery

TPS63020 draws from whichever is higher between VBUS_PD and VBAT_PROT, via a low-Vf Schottky OR diode pair (or ideal-diode controller if we can spare ~$0.50 — optional).

- **USB attached:** VBUS_PD (≥5V) ≫ VBAT (3.0–4.2V), so TPS63020 runs from USB. TP4056 charges battery in parallel. Current into TPS63020 + charge current ≤ negotiated PD current.
- **USB detached:** TPS63020 runs from VBAT_PROT (3.0–4.2V → boost to 5V). TP4056 idle.
- **USB attached, battery full:** TP4056 enters standby, TPS63020 runs from VBUS_PD.

## PD negotiation (HUSB238)

HUSB238 is a USB-C PD sink controller configured over I2C. On boot:
1. HUSB238 reads available PDOs from source.
2. M1 (ESP32-S3) reads HUSB238 status register over primary I2C (addr `0x08`).
3. M1 writes selected PDO to HUSB238 (target: 5V @ 3A minimum; opportunistically 9V or 12V if headroom is needed and TPS63020 can handle the Vin range — it's rated 1.8V–5.5V input, so **cap PD negotiation at 5V** unless we add a pre-regulator).

> ⚠️ **Design lock:** TPS63020 Vin ≤ 5.5V. Firmware MUST NOT select 9V+ PDO or the TPS63020 dies. Enforce in HUSB238 init.

## Battery protection (DW01A + FS8205A)

Standard Li-ion protection pair:
- **DW01A** monitors VBAT, toggles OC/OD gates on FS8205A.
- **FS8205A** is dual N-MOSFET in one package — one for charge path, one for discharge.
- Thresholds: overcharge 4.25V, over-discharge 2.4V, overcurrent ~3A.
- Protection sits between 18650 `+` terminal and `VBAT_PROT` rail feeding both TP4056 (charge return) and TPS63020 (discharge).

## Current monitoring (INA219)

INA219 on primary I2C (addr `0x40`, configurable via A0/A1 pads).

- **Shunt:** 0.01Ω 1% 1W on V5_BUS high side (after TPS63020 output).
- Reports: V5_BUS voltage, shunt current (→ V5_BUS current), V5_BUS power.
- Reason: lets firmware log stack-wide 5V current over time, detect which modules spike, estimate battery life.
- **Does NOT monitor VBAT directly** — battery SoC is inferred from VBAT voltage via M1 ADC tap (pin TBD on M1 header breakout, not on bus).

## 3V3 regulator

**AP2112K-3.3** LDO:
- Vin: V5_BUS. Vout: 3.3V @ 600mA max.
- Quiescent: 55µA typ.
- Dropout: 250mV @ 600mA.

> ⚠️ **Headroom concern:** 600mA is the rated max. Back-of-envelope load across the stack: M1 ~350mA (S3 + OV2640 + PSRAM burst), M3 ~150mA, M3A ~100mA, M4 I/O ~50mA, M5 ~50mA, M6 ~10mA, M9 ~50mA → **~760mA peak, ~300mA typical**. AP2112K is under-rated for worst case.
>
> **Options** (open question — pick before schematic freeze):
> 1. Swap to **TLV62569** buck (1.5A, ~92% eff) — saves 1.5W heat vs LDO, costs ~$0.50 more, needs 2.2µH inductor. **Recommended.**
> 2. Keep AP2112K, cap peak loads in firmware. Risky.
> 3. Two AP2112Ks in parallel with ballast resistors. Hacky.

Draft assumes **TLV62569** going forward; change if BOM demands otherwise.

## Pin-level netlist (draft)

### U1 — HUSB238 (QFN-14 or SOP-10 depending on package choice)

| Pin | Signal | Connection |
|----|----|----|
| VBUS | VBUS_USB | USB-C VBUS via 10µF + 100nF decoupling |
| CC1 | USB-C CC1 | to USB-C receptacle CC1 |
| CC2 | USB-C CC2 | to USB-C receptacle CC2 |
| OUT | VBUS_PD | post-PD output to power path (10µF bulk) |
| SDA | HUSB238_SDA | → primary I2C SDA (bus pin 15) |
| SCL | HUSB238_SCL | → primary I2C SCL (bus pin 16) |
| GND | GND | star ground |

### U2 — TPS63020 (QFN-10)

| Pin | Signal | Connection |
|----|----|----|
| VIN | TPS_IN | OR'd VBUS_PD / VBAT_PROT via Schottky pair |
| L1 | SW1 | inductor node 1 (1.5µH typ.) |
| L2 | SW2 | inductor node 2 |
| VOUT | V5_BUS | regulated 5V out (22µF bulk + 100nF local) |
| FB | V5_BUS via R-divider | sets 5.0V output |
| PS/SYNC | GND | force PWM mode, or tie high for PFM |
| EN | VBUS_PD \| VBAT_PROT | enable whenever any source present |
| PGND | GND | |
| AGND | GND | star to PGND |

### U3 — TP4056 (SOP-8)

| Pin | Signal | Connection |
|----|----|----|
| VCC | VBUS_PD | charge input |
| BAT | VBAT_CHG | → 18650 `+` via DW01A/FS8205A protection |
| PROG | to GND via 1.2kΩ | sets 1A charge current |
| STDBY | LED_STDBY | green LED indicator |
| CHRG | LED_CHRG | red LED indicator |
| TEMP | GND via 10kΩ | NTC thermistor disabled (tie to GND if no thermistor) |
| CE | VCC | always enabled |
| GND | GND | |

### U4 — DW01A + U5 FS8205A (protection pair)

| DW01A pin | Signal | Connection |
|----|----|----|
| VDD | VBAT | battery `+` terminal direct |
| GND | BAT_NEG | battery `−` terminal (floating, not stack GND yet!) |
| OD | FS8205A G1 | discharge FET gate |
| OC | FS8205A G2 | charge FET gate |
| CS | junction between FS8205A S1/S2 | current sense |
| VM | VBAT_PROT | protected `+` output |
| TD | 100nF to GND | delay cap |

> ⚠️ **Grounds:** battery `−` is NOT stack GND until after FS8205A. Only `VBAT_PROT` side rejoins stack GND via FS8205A source.

### U6 — AP2112K-3.3 OR TLV62569 (pending decision)

**If AP2112K-3.3 (SOT-23-5):**

| Pin | Signal | Connection |
|----|----|----|
| VIN | V5_BUS | 1µF input cap |
| EN | VIN | always on |
| GND | GND | |
| NC | — | — |
| VOUT | V3V3_BUS | 1µF output cap → bus pins 1, 3 |

**If TLV62569 (SOT-23-6):** add 2.2µH inductor between SW and VOUT, 10µF output cap.

### U7 — INA219 (MSOP-10)

| Pin | Signal | Connection |
|----|----|----|
| VIN+ | V5_BUS (shunt high side) | before 0.01Ω shunt |
| VIN− | V5_BUS (shunt low side) | after 0.01Ω shunt, feeds bus pins 2, 4 |
| VS | V3V3_BUS | IC supply |
| SDA | INA_SDA | → primary I2C SDA (bus pin 15) |
| SCL | INA_SCL | → primary I2C SCL (bus pin 16) |
| A0 | GND | addr bit 0 |
| A1 | GND | addr bit 1 → final addr `0x40` |
| GND | GND | |

### J1 — USB-C receptacle (16 or 24 pin)

Minimum pins used: VBUS (×4), GND (×4), CC1, CC2, D+, D−. USB 3.0 SS pairs NOT routed from M2 — USB 3.0 lives on M8. M2 only handles power + USB 2.0 data passthrough for M1 firmware flashing via CH340C.

| USB-C pin | Signal | Connection |
|----|----|----|
| A4, A9, B4, B9 | VBUS | → HUSB238 VBUS (combined) |
| A1, A12, B1, B12 | GND | stack GND |
| A5 | CC1 | → HUSB238 CC1 |
| B5 | CC2 | → HUSB238 CC2 |
| A6 | D+ | → bus pin 23 (USB_D+) |
| A7 | D− | → bus pin 24 (USB_D-) |
| B6, B7 | D+/D− alt | tie to A6/A7 (flip support) OR leave NC if single-orient |

### J2 — 18650 battery holder

| Pad | Signal |
|----|----|
| + | VBAT (to DW01A VDD + FS8205A drain) |
| − | BAT_NEG (to DW01A GND + FS8205A source before current sense) |

### J3 — 40-pin bus header (2×20 @ 0.1")

| Bus pin | Signal | M2 net |
|----|----|----|
| 1, 3 | 3V3 | V3V3_BUS |
| 2, 4 | 5V | V5_BUS (post-shunt) |
| 5, 6, 7, 8, 39, 40 | GND | stack GND |
| 15 | I2C_SDA | I2C_SDA (to HUSB238 + INA219) |
| 16 | I2C_SCL | I2C_SCL |
| 23 | USB_D+ | from USB-C A6/B6 |
| 24 | USB_D− | from USB-C A7/B7 |
| 32 | RESET_N | 10kΩ pull-up to V3V3_BUS here (bus-wide pull-up lives on M2) |
| all others | — | NC (leave unrouted but preserve GND return under header) |

## I2C pull-ups

Per BUS.md, primary I2C pull-ups live on M2 only.

- **SDA (bus pin 15):** 4.7kΩ to V3V3_BUS.
- **SCL (bus pin 16):** 4.7kΩ to V3V3_BUS.

## Decoupling

- Every IC: 100nF ceramic at power pin + 10µF bulk per rail per IC.
- Bus header: 10µF bulk + 100nF on each of 3V3 and 5V at the header pins.
- TPS63020 output: 22µF + 100nF + 22µF (split for noise).
- USB-C VBUS: 10µF + 100nF.

## LEDs / indicators (optional)

- Red: TP4056 CHRG (charging).
- Green: TP4056 STDBY (charge complete).
- Blue: V3V3_BUS present (3V3 power good — via 1kΩ to GND).

## Test points

- `TP_VBUS_PD` — post-PD rail, pre-TPS63020
- `TP_V5_BUS` — 5V rail before shunt
- `TP_V5_BUS_OUT` — 5V rail after shunt (what goes to bus)
- `TP_V3V3_BUS` — 3V3 rail
- `TP_VBAT` — raw battery (handy for SoC debug)
- `TP_VBAT_PROT` — protected battery

## Layout notes (advisory — for when we hit KiCad)

1. **USB-C receptacle on the edge** of the 60×50mm board, opposite the bus header.
2. **HUSB238 within 10mm** of USB-C VBUS pin.
3. **TPS63020 inductor loop** tight — SW1→L→SW2 return via bottom GND plane, total loop ≤5mm.
4. **18650 holder on the top side**, oriented long-axis parallel to the bus header so the battery doesn't overhang adjacent modules.
5. **INA219 shunt** in-line on V5_BUS trace, 4-wire Kelvin sense to INA219 VIN±.
6. **TP4056 thermal pad** needs copper fill on both layers with ≥4 stitching vias — it gets hot at 1A charge.
7. **Keep the 3V3 LDO/buck close to bus header** so the bus-side decoupling is within 5mm.

## Open questions (resolve before KiCad)

1. **3V3 regulator choice** — AP2112K-3.3 (simple, under-rated) vs TLV62569 (buck, 1.5A, recommended). Affects BOM + layout footprint.
2. **Ideal-diode OR vs Schottky pair** for USB/battery power path. Ideal diode = 100mV savings, costs $0.50 and one part.
3. **Battery SoC:** read VBAT via INA219 bus voltage (VIN− pin) with auxiliary divider, or via dedicated M1 ADC tap? If via INA219, we save a wire but lose resolution at battery voltages (INA219 VIN range caps at 26V so resolution is fine, but the VIN pin measures post-shunt which is V5_BUS, not VBAT). **Cleanest: add a second INA219 on VBAT** — +$1.20, or skip and use MCU ADC for SoC.
4. **USB-C orientation support:** do we route both A6/A7 and B6/B7 (supports flip), or only one orientation (simpler, users learn)? Flip support = 2 extra traces + 4 resistors for CC steering, no IC cost.
5. **Fuse:** add a PTC resettable fuse (e.g. 2A trip) between USB-C VBUS and HUSB238? Protects against source faults. Cost ~$0.30.

## What this module does NOT do

- Does NOT provide USB 3.0 — that's M5/M8.
- Does NOT provide the 1.1V FPGA core rail — that's local to M4 (AP2112K-1.1).
- Does NOT monitor per-module current — only stack-wide V5_BUS current via INA219.
- Does NOT include a power switch — the stack powers on whenever USB-C is plugged OR battery is connected via BATT_EN jumper on the 18650 holder footprint. (Add a soft-latch pushbutton circuit if user-facing power button is desired — open question.)

## Next steps

1. Resolve open questions #1–#5 above.
2. Create KiCad project `hardware/v2/modules/m2-power/m2-power.kicad_pro`.
3. Import `hardware/v2/lib/` symbols: 40-pin stacking header, M2.5 mounting-hole pattern.
4. Place ICs per this netlist, wire per the power tree.
5. Run ERC → resolve → export DSN for FreeRouting.
6. Layout pass → DRC → Gerbers → fab.
