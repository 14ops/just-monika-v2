# M6 — I/O Expander Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 2L. Footprint target: 60x50mm.

## Purpose
Low-speed GPIO breakout with no firmware on the module itself.

## Key parts
- MCP23017 I2C GPIO expander
- 2x Grove I2C connectors
- 2x GPIO headers (1x8)
- 2x20 female stacking header
- 2-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- Primary I2C on pins 15/16.
- INT pin can be used for GPIO-change notification back to M1.

## Layout notes
- Keep the board simple and local; 2-layer is sufficient.
- Avoid adding bus pull-ups; primary pull-ups stay on M2 only.
- Place the Grove headers on opposite edges if possible to simplify cable routing.

## Open questions
- Confirm the MCP23017 address strap and the interrupt line mapping into the stack.
