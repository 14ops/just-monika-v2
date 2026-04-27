# M7 — Coral Carrier Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 4L. Footprint target: 60x50mm.

## Purpose
Dedicated USB 3.0 carrier for the Google Coral accelerator.

## Key parts
- USB-A receptacle for Coral
- TPD4E05U06 ESD protection
- 2x20 stacking header
- 4-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4 as needed.
- GND on pins 5/6/7/8/39/40.
- USB3_TX+/-, USB3_RX+/- on pins 25-28.

## Layout notes
- Keep the USB3 path short and straight between the bus header and the receptacle.
- Place ESD protection immediately adjacent to the connector.
- Preserve clean reference planes through the stack.

## Open questions
- Confirm the exact mechanical placement of the Coral plug-in and whether the path is fully bus-routed or needs an inter-board jumper.
