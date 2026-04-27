# M3 — Sensor Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 4L. Footprint target: 60x50mm.

## Purpose
Sensor companion board with its own MCU for environmental and motion polling.

## Key parts
- ESP32-C6-MINI-1
- MPU6050 6-axis IMU
- BH1750 light sensor
- BME280 environmental sensor
- 2x20 stacking header
- 4-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- Primary I2C on pins 15/16.
- Secondary I2C on pins 17/18, owned by M3.
- INT0 reserved for motion wake / IMU interrupt.

## Layout notes
- Keep the ESP32-C6 antenna clear of sensor cans and any ground-shield overhang.
- Group the I2C sensors together and keep the bus traces short.
- Treat the board as a low-speed module; no impedance-controlled routing needed.

## Open questions
- Confirm whether M3 forwards sensor summaries over I2C2, UART2, or both.
