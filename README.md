# Water Turret Auto/Manual Controller

Intelligent water turret system with RF manual control and Pi-based auto tracking.

## 🎯 Overview

This project adds automatic target tracking to an existing CyberBrick-controlled water turret while preserving full manual RF control functionality.

**Manual Mode**: RF Transmitter → Receiver → Controller Core → Servos (unchanged)  
**Auto Mode**: Pi → Controller Core → Servos (intelligent tracking)

## 📁 Project Structure

### Core Files
- **`final_turret_controller.py`** - Main Pi controller (ready to use)
- **`raspberry_pi_receiver.py`** - Arduino sensor interface
- **`requirements.txt`** - Python dependencies

### Documentation  
- **`FINAL_SOLUTION.md`** - Complete implementation guide
- **`micropython_approach.md`** - Technical details

### Configuration
- **`Water+Turret.json`** - Existing CyberBrick configuration (unchanged)
- **`todo.txt`** - Project progress tracking
- **`partslist.txt`** - Hardware components

### Hardware Code
- **`Arduino/`** - Sensor code for Arduino
- **`datasheets/`** - Component documentation

## 🚀 Quick Start

1. **Modify CyberBrick firmware** (see `FINAL_SOLUTION.md`)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Connect USB-C cable** between Pi and Controller Core
4. **Run controller**: `python3 final_turret_controller.py`
5. **Press Enter** to toggle Manual/Auto mode

## 🔗 Based On

- [CyberBrick Controller Core Repository](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core)
- Existing Water+Turret.json configuration
- Arduino HC-SR04 + MAX4466 sensor system

## ✅ Features

- ✅ **Preserves RF control** - Manual mode unchanged
- ✅ **Simple mode switching** - Press Enter to toggle
- ✅ **Auto target tracking** - Distance-based aiming
- ✅ **Smart firing** - Sound + proximity confirmation
- ✅ **Minimal hardware** - Just one USB-C cable

Perfect for keeping cats out of your garden! 🐱💦 