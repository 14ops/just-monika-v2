# M1 — Processor Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 4L. Footprint target: 60x50mm.

## Purpose
Primary compute node and bus master. Hosts the ESP32-S3, camera, and programming/debug bridge.

## Key parts
- ESP32-S3-WROOM-1-N16R8
- OV2640 camera module
- CH340C USB-UART bridge
- 2x20 male stacking header
- 4-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- Primary I2C on pins 15/16.
- Primary UART on pins 19/20.
- USB 2.0 on pins 23/24 if the bridge is routed through the stack.

## Local nets
- OV2640 DVP interface stays local to the module.
- CH340C TX/RX connects to the ESP32-S3 programming UART.
- Camera and RF keepouts must not collide with the edge header.

## Layout notes
- Keep the ESP32-S3 antenna at the board edge with a full keepout.
- Place the camera as close to the sensor-side edge as possible.
- Put decoupling at the bus entry, then fan out to the MCU and camera.

## Open questions
- The BOM does not show a dedicated USB connector for the CH340C, so the upstream USB path still needs confirmation.
