# Just Monika: Modular Compute Platform (v2)

> **"She remembers you because she reads your notes, not because a corporation is mining your chats."**

Just Monika is an anti-laziness AI companion built on a **10-module stackable compute platform**. The project is designed for 100% on-device inference, ensuring total privacy while pushing the user toward intellectual growth through Socratic interaction.

---

## ⚠️ Project Status & Ground Truth (April 2026)

The project has recently undergone a major architectural pivot. **The v2 10-module stacked architecture is the current ground truth.**

- **Current Ground Truth:** `just-monika-v2` repository, specifically `CLAUDE.md` and `JOURNAL.md` (updated April 20, 2026).
- **Stale Repositories:** `just-monika2`, `monika11`, and the nested `just-monika` clones are **v1-era artifacts**. They contain valuable software concepts (Swarm, Constellation UI) but target obsolete hardware (ESP32-P4) and must be re-validated/re-ported.
- **Deadline:** Stasis Hackathon, May 15, 2026.

---

## 🏗️ Hardware Architecture: The v2 Stack

The v2 platform moves away from a single-board design to a **standardized 40-pin stacking bus** (2×20 headers, 0.1" pitch). This modularity allows for independent swapping of any subsystem.

### Module Breakdown

| Module | Purpose | Key Components | Layers |
| :--- | :--- | :--- | :--- |
| **M1** | **Processor** | ESP32-S3-WROOM-1 (16MB Flash, 8MB PSRAM), OV2640 Cam | 4L |
| **M2** | **Power** | HUSB238 USB-C PD, TPS63020 Buck-Boost, 18650 Cell | 4L |
| **M3/M3A**| **Sensors/Audio** | ESP32-C6 (WiFi6/BLE), BME280, 2× INMP441 Mics, MAX98357A | 4L |
| **M4** | **FPGA** | **Lattice ECP5-45F BGA-256**, DDR2 SODIMM, 64MB HyperRAM | **6L** |
| **M5** | **USB 2.0 Hub** | USB2514B 4-port hub | **6L** |
| **M6** | **I/O Expansion** | MCP23017 I2C GPIO expander | 2L |
| **M7** | **Coral Carrier** | Dedicated USB 3.0 path for Google Coral Accelerator | 4L |
| **M8** | **High-Speed** | TUSB8020B USB 3.0 Hub, PCIe x1 Edge Connector | **6L** |
| **M9** | **Display** | 2.13" E-Ink FeatherWing, microSD | 2L |

### The 40-Pin Bus
The backbone of the system provides:
- **Power:** 3.3V and 5V rails (Sourced by M2).
- **Data:** 2× I2C, 2× UART, 3× SPI (CS0-2), 4× I2S Audio.
- **High-Speed:** USB 2.0 (D+/D-) and USB 3.0 (TX±/RX±) differential pairs.
- **Control:** 3× Interrupts, System Reset, 2× GPIO.

---

## 🧠 AI & Software Stack

The "Just Monika" persona is a multi-agent swarm designed to discourage intellectual laziness.

- **Swarm Orchestration:** A Python-based runtime (originally in `monika11`) that coordinates specialized agents: *Reasoning Validator*, *Emotion Classifier*, *Memory Manager*, and the *Monika Persona*.
- **Memory (RAG):** Local ChromaDB instance that indexes your **Obsidian Vault** in real-time using `watchdog`.
- **Inference:** Local LLM (Llama 3.2 3B) via Ollama.
- **Visuals:** A "Constellation UI" that animates agent handoffs and "thought flows" as a live galaxy of stars.
- **Firmware:** ESP-IDF based. **Note:** Currently being re-ported from the obsolete ESP32-P4 target to the v2 M1 (ESP32-S3).

---

## 🛠️ Development & Tooling

- **Hardware:** KiCad 9.0 for schematics and 6-layer impedance-controlled layouts.
- **FPGA:** Yosys + nextpnr-ecp5 for audio DSP and Whisper acceleration.
- **Manufacturing:** JLCPCB (PCBs + SMT Assembly with BGA X-ray for M4).
- **Backend:** FastAPI + WebSockets for the Constellation UI and Obsidian integration.

---

## 📂 Repository Guide (Chronological)

1. **`just-monika-v2` (Current):** The active v2 hardware design and project ground truth.
2. **`monika11` / `marihacks-monika` (April 2026):** The working software demo from MariHacks. Contains the Constellation UI and Obsidian Indexer.
3. **`just-monika2` (Obsolete):** The v1-era hardware and firmware (ESP32-P4). Do not use for hardware reference.
4. **`just-monika` (Stale):** Original roadmap and concept docs.

---

*Built for Stasis / MariHacks 2026. Just Monika runs offline, remembers you, and keeps your data where it belongs: on your own stack.*
