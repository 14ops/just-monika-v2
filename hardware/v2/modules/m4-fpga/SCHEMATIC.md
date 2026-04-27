# M4 — FPGA Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 6L. Footprint target: 60x50mm.

## Purpose
High-speed logic module with the solder-down ECP5, HyperRAM, flash, and DDR2 expansion.

## Key parts
- Lattice ECP5 LFE5U-45F BGA-256
- IS66WVH8M8BLL 64MB HyperRAM
- W25Q128JVS SPI flash
- AP2112K-1.1 LDO
- SN74CBTLV3257 PMOD mux
- 2x PMOD headers
- DDR2 SODIMM socket
- JTAG header
- 2x20 female stacking header
- 6-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- SPI_CS2 is the bus hook for FPGA flash / bitstream-related access.
- UART2 may be used for a console link if needed.

## Layout notes
- Keep the ECP5 and DDR2 routing on the controlled-impedance 6L stackup.
- Put the HyperRAM and flash close to the FPGA balls.
- Keep the JTAG header accessible without crossing high-speed traces.

## Open questions
- Confirm final DDR2 socket orientation and mechanical clearance.
- Decide whether HyperRAM is the primary working memory or a secondary scratch space.
