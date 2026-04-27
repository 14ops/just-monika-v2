# M5 — USB 2.0 Hub Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 6L. Footprint target: 60x50mm.

## Purpose
USB 2.0 fanout and peripheral expansion board.

## Key parts
- USB2514B 4-port hub controller
- 24LC02B EEPROM
- 12 MHz crystal
- 4x TPD4E05U06 ESD protectors
- 2x expansion USB-A headers
- 2x20 stacking header
- 6-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- USB_D+ / USB_D- on pins 23/24 for the hub upstream path.

## Layout notes
- Keep the hub controller centered between the upstream bus path and the downstream ports.
- Put the ESD parts right at the connector edges.
- Treat the board as an impedance-controlled USB2 design with continuous reference planes.

## Open questions
- Confirm the downstream port allocation for the two expansion USB-A headers.
- Confirm whether one downstream port is reserved for an internal service path.
