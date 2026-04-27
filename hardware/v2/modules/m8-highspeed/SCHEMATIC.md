# M8 — High-Speed Data Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 6L. Footprint target: 60x50mm.

## Purpose
USB 3.0 hub and PCIe x1 edge-connect module.

## Key parts
- TUSB8020B USB 3.0 hub controller
- PCIe x1 edge connector
- 2x20 female stacking header
- 6-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- USB3_TX+/-, USB3_RX+/- on pins 25-28.

## Layout notes
- Treat the board as a strict impedance-control design.
- Keep the hub controller and the edge connector in a short, symmetric path.
- Reserve a clean internal plane stack for USB3 and PCIe return paths.

## Open questions
- Confirm the PCIe edge connector pinout and intended endpoint behavior.
- Confirm whether any USB2 fallback routing is needed on this module.
