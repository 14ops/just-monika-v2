# M9 — Display Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 2L. Footprint target: 60x50mm.

## Purpose
Low-speed user interface board with the e-ink display and microSD breakout.

## Key parts
- E-Ink FeatherWing 2.13in (250x122)
- MicroSD card slot breakout
- 2x20 stacking header
- 2-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- SPI_CLK / MOSI / MISO on pins 9/10/11.
- SPI_CS0 for the display and SPI_CS1 for microSD, per bus contract.

## Layout notes
- Keep the display footprint aligned to the chosen FeatherWing mechanical outline.
- Keep the board low-speed and simple; 2-layer is sufficient.
- Put the microSD breakout close to the bus header to keep SPI short.

## Open questions
- Confirm the exact FeatherWing footprint and mounting-hole geometry for the chosen display part.
