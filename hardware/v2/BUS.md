# 40-Pin Stacking Bus — Design Contract

Every v2 module speaks this bus. Break this contract on one module and the stack stops working.

Source: `C:\Users\Seth\Downloads\modular_compute_platform_bom_v2.xlsx`, sheet "40-Pin Bus Pinout".

## Physical
- **Connector:** 2×20 header, 0.1" (2.54 mm) pitch, 40 pins total.
- **Mating:** Female-on-top / male-on-bottom stacking headers on interior modules; male-only on the terminal top module; female-only on the terminal bottom module (the one with no neighbor below).
- **Pin 1 convention:** top-left when the module's primary-component side faces you and the bus header is at the bottom edge. Mark pin 1 with a square pad and silkscreen triangle.
- **Mechanical registration:** 4× M2.5 mounting holes at the corners — proposed `(3,3), (57,3), (3,47), (57,47)` if the 60×50mm footprint carries over from v1. Confirm per-module during layout.

## Pinout

| Pin | Signal | Type | Pin | Signal | Type |
|-----|--------|------|-----|--------|------|
| 1 | 3V3 | Power | 2 | 5V | Power |
| 3 | 3V3 | Power | 4 | 5V | Power |
| 5 | GND | Ground | 6 | GND | Ground |
| 7 | GND | Ground | 8 | GND | Ground |
| 9 | SPI_CLK | SPI Bus | 10 | SPI_MOSI | SPI Bus |
| 11 | SPI_MISO | SPI Bus | 12 | SPI_CS0 | SPI Bus |
| 13 | SPI_CS1 | SPI Bus | 14 | SPI_CS2 | SPI Bus |
| 15 | I2C_SDA | I2C Bus | 16 | I2C_SCL | I2C Bus |
| 17 | I2C2_SDA | I2C Bus 2 | 18 | I2C2_SCL | I2C Bus 2 |
| 19 | UART_TX | UART | 20 | UART_RX | UART |
| 21 | UART2_TX | UART 2 | 22 | UART2_RX | UART 2 |
| 23 | USB_D+ | USB 2.0 | 24 | USB_D- | USB 2.0 |
| 25 | USB3_TX+ | USB 3.0 | 26 | USB3_TX- | USB 3.0 |
| 27 | USB3_RX+ | USB 3.0 | 28 | USB3_RX- | USB 3.0 |
| 29 | INT0 | Interrupt | 30 | INT1 | Interrupt |
| 31 | INT2 | Interrupt | 32 | RESET_N | System |
| 33 | I2S_BCLK | I2S Audio | 34 | I2S_LRCLK | I2S Audio |
| 35 | I2S_DIN | I2S Audio | 36 | I2S_DOUT | I2S Audio |
| 37 | GPIO_A | General | 38 | GPIO_B | General |
| 39 | GND | Ground | 40 | GND | Ground |

**Allocation:** 4× power, 6× GND, 6× SPI (1 clk/mosi/miso + 3 chip-selects), 4× I2C (2 independent buses), 4× UART (2 independent), 6× USB (1× USB2.0 D+/D−, 1× USB3.0 TX±/RX±), 4× I2S, 3× interrupt, 1× reset, 2× GPIO.

## Bus master / slave allocation

| Signal group | Master | Notes |
|---|---|---|
| SPI primary (CLK/MOSI/MISO + CS0/CS1/CS2) | **M1 ESP32-S3** | CS0 reserved for M9 E-Ink, CS1 for M9 microSD, CS2 for M4 FPGA SPI flash / bitstream load. |
| I2C primary | **M1 ESP32-S3** | Talks to INA219 (M2), MCP23017 (M6), all M3 sensors. Shared bus. |
| I2C2 | **M3 ESP32-C6-MINI-1** | Keeps M3 sensor polling off the primary bus. |
| UART primary | **M1 ESP32-S3** | Console + CH340C bridge. |
| UART2 | Open | Candidate: M1 ↔ M3 direct link, or M1 ↔ M4 FPGA UART console. |
| USB 2.0 (D+/D−) | **M5 USB2514B hub** | M1 can act as USB-OTG device to the hub if needed. |
| USB 3.0 | **M8 TUSB8020B hub** | Routes to M7 Coral carrier + M8 expansion. |
| I2S | **M3 ESP32-C6-MINI-1 or M4 FPGA** | TBD — depends on whether audio DSP runs on FPGA. |
| INT0/1/2 | **M1 ESP32-S3** input | For MPU6050 motion, MCP23017 change, generic module wake. |
| RESET_N | **M1 ESP32-S3** drives (open-drain) | Bus-wide reset. Every module pulls up to 3V3, any module can assert. |
| GPIO_A/B | **M1 ESP32-S3** | Board-level flags. Soft-defined. |

## Electrical constraints

### Power
- **5V rail** sourced by **M2 only** via TPS63020 buck-boost or USB-C PD passthrough. Budget: 3A peak (TPS63020 spec).
- **3V3 rail** sourced by **M2 only**. Regulate from 5V via LDO/buck on M2 → bus. All modules draw from the bus.
- **M4 FPGA 1.1V core** is local to M4 (AP2112K-1.1 LDO) — never appears on the bus.
- Every module **must** decouple each power rail at the header with ≥10µF bulk + 0.1µF local per IC.

### Signal integrity
- **USB 3.0 diff pairs (25/26, 27/28):** 90Ω differential, ≤5mm mismatch within pair, ≤10mm between TX and RX pairs. Reference continuous GND on adjacent layer — this is why M8 is 6L.
- **USB 2.0 diff pair (23/24):** 90Ω differential, ≤5mm mismatch. 6L for M5 (hub module) to ensure clean reference plane under the IC; 4L is acceptable for modules that only pass USB2 through the bus.
- **I2C (15–18):** pull-ups (4.7kΩ typ.) on **M2 only** for primary, **M3 only** for I2C2. Other modules must not add pull-ups or the bus loading breaks.
- **SPI (9–14):** bus-based, not daisy-chained. CS lines are dedicated per-module. ≤20cm total bus length across full stack (stub + trace) to stay under 40MHz comfortably.
- **I2S (33–36):** only one master at a time. Guard with bus ownership in firmware, not hardware.
- **RESET_N (32):** open-drain, 10kΩ pull-up on M2. Any module can assert low to reset the whole stack.

### Stub length
- Headers add ≈3mm of stub per module per signal. Across a 10-module stack, worst-case SPI stub = 30mm → SPI should stay ≤25 MHz unless we shorten. Acceptable for W25Q128 bitstream load, marginal for high-speed peripherals.
- Keep USB3, USB2, and I2S traces ≤15mm on each module from the header to the silicon.

## What a module MUST do

1. Expose the 2×20 header at the **same position** on every module — proposed `(30, 25)mm` centered on a 60×50mm footprint. Verify in lib/.
2. Connect **pin 1 and pin 3** to the module's 3V3 net (star to the local decoupling cap).
3. Connect **pin 2 and pin 4** to the 5V net (same).
4. Tie **all 6 GND pins** to the module ground pour.
5. **NOT drive** 3V3 or 5V (only M2 may source these).
6. **NOT add pull-ups** to I2C/I2C2 (only M2/M3 respectively).
7. Expose M2.5 mounting holes at the same 4 corner positions on every module.

## What a module MAY skip
- Unused bus signals (e.g., an M6 GPIO expander doesn't need USB3 pins connected — leave them NC, but still route GND pours under the header for return path continuity).
- UART2, GPIO_A/B if unused.

## Open questions (reserve pins for these before they bite)
- **Interrupt routing:** INT0/1/2 pre-assigned? Currently undecided. Provisional: INT0 = MPU6050 motion (M3), INT1 = MCP23017 change (M6), INT2 = user button / generic.
- **FPGA JTAG:** not on the 40-pin bus; exposed on a local 2×5 1.27mm header on M4 only.
- **Coral USB3 routing:** from M8 hub → M7 carrier. Via the bus (pins 25–28) or a separate dedicated wire between M7 and M8? If bus-routed, M7 cannot be physically between M8 and another USB3 consumer.
