# M3A — Audio Module (v2 Schematic Scaffold)

Status: scaffolded from the v2 BOM; KiCad capture/layout still pending.
Layers: 4L. Footprint target: 60x50mm.

## Purpose
Independent audio module for stereo capture and speaker drive.

## Key parts
- 2x INMP441 MEMS microphones
- MAX98357A I2S audio amplifier
- 2x20 stacking header
- 4-layer PCB

## Bus connections
- 3V3 and 5V on pins 1/3 and 2/4.
- GND on pins 5/6/7/8/39/40.
- I2S_BCLK on pin 33.
- I2S_LRCLK on pin 34.
- I2S_DIN on pin 35.
- I2S_DOUT on pin 36.

## Layout notes
- Keep the two microphones separated enough for stereo pickup.
- Route I2S as a tight local cluster with a clean ground return.
- Isolate the amplifier output from the microphone area.

## Open questions
- The BOM does not name a speaker connector or load, so the amplifier output termination still needs finalization.
- I2S master ownership is shared with the rest of the stack and must be defined at firmware bring-up.
