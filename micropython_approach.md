# MicroPython Approach - Using Official CyberBrick Repository

Based on the official [CyberBrick Controller Core repository](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core), we can modify the existing MicroPython RC application to add Pi communication.

## Key Discovery

The CyberBrick Controller Core runs **MicroPython** and the source code is available! This means we can:

1. **Extend existing RC application** instead of replacing it
2. **Add serial communication** to the existing `control.py` 
3. **Keep Water+Turret.json compatibility** completely intact
4. **Maintain RF functionality** while adding Pi control

## Repository Structure

From the [official repo](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core):

```
src/app_rc/          # RC controller application code
├── control.py       # Main control logic  
├── parser.py        # Configuration parser (Water+Turret.json)
└── ...

tools/               # Visualization tools
docs/                # Documentation
```

## Our Approach

### 1. Clone and Modify Existing Code

```bash
# Get the official CyberBrick code
git clone https://github.com/CyberBrick-Official/CyberBrick_Controller_Core.git
cd CyberBrick_Controller_Core/src/app_rc/
```

### 2. Add Pi Communication to control.py

Extend the existing RC application with a Pi command interface:

```python
# Add to existing control.py
import uart
import json

class PiInterface:
    def __init__(self, control_system):
        self.control = control_system
        self.uart = uart.UART(baudrate=115200)
        self.auto_mode = False
        
    def process_pi_commands(self):
        """Process commands from Raspberry Pi"""
        if self.uart.available():
            try:
                command = self.uart.readline().decode().strip()
                
                if command == "MODE:AUTO":
                    self.auto_mode = True
                    self.uart.write("MODE:AUTO_OK\n")
                    
                elif command == "MODE:MANUAL":
                    self.auto_mode = False
                    self.uart.write("MODE:MANUAL_OK\n")
                    
                elif command.startswith("MOVE:") and self.auto_mode:
                    # Parse: MOVE:PWM1=90,PWM2=90,PWM3=90
                    self.parse_move_command(command)
                    
            except Exception as e:
                print(f"Pi command error: {e}")
                
    def parse_move_command(self, command):
        """Parse Pi movement commands using existing control logic"""
        params = command.split(":")[1]
        
        # Extract PWM values
        for param in params.split(","):
            if "PWM1=" in param:
                value = int(param.split("=")[1])
                # Use existing control system to set PWM1
                self.control.set_pwm1(value)
                
            elif "PWM2=" in param:
                value = int(param.split("=")[1])
                self.control.set_pwm2(value)
                
            elif "PWM3=" in param:
                value = int(param.split("=")[1])
                self.control.set_pwm3(value)

# Modify main loop in control.py
def main_loop():
    pi_interface = PiInterface(control_system)
    
    while True:
        # Process Pi commands first
        pi_interface.process_pi_commands()
        
        # Process RF input only if not in auto mode
        if not pi_interface.auto_mode:
            process_rf_input()  # Existing RF processing
            
        # Update outputs (same for both RF and Pi)
        update_servos_and_leds()  # Existing output logic
        
        time.sleep(0.01)
```

### 3. Upload Modified Code

```bash
# Convert to bytecode for better performance
mpy-cross control.py
mpy-cross parser.py

# Upload to Controller Core filesystem
# (using official CyberBrick upload method)
```

## Benefits of This Approach

✅ **Uses Official Code** - Based on actual CyberBrick repository  
✅ **Maintains Compatibility** - Existing Water+Turret.json works unchanged  
✅ **Keeps RF Functionality** - Manual mode unchanged  
✅ **Minimal Changes** - Just add Pi interface to existing code  
✅ **Future Updates** - Can sync with official repository updates  
✅ **Proven Stable** - Uses existing tested control logic

## Communication Protocol

**Pi → Controller Core:**
```
MODE:AUTO                    # Enable Pi control
MODE:MANUAL                  # Enable RF control  
MOVE:PWM1=90,PWM2=90,PWM3=90 # Set servo positions
STATUS                       # Get current state
```

**Controller Core → Pi:**
```
MODE:AUTO_OK                 # Mode switched to auto
MODE:MANUAL_OK               # Mode switched to manual
MOVE:OK                      # Movement completed
STATUS:AUTO,90,90,90         # Current mode and positions
```

## Implementation Steps

### 1. Download Official Code
```bash
git clone https://github.com/CyberBrick-Official/CyberBrick_Controller_Core.git
```

### 2. Study Existing RC Application
- Understand how `control.py` processes RF input
- Learn how `parser.py` handles Water+Turret.json
- Identify where to add Pi communication

### 3. Add Pi Interface
- Extend main loop with Pi command processing
- Add mode switching logic
- Integrate with existing servo control

### 4. Test and Upload
- Test modified code locally if possible
- Upload to Controller Core using official method
- Verify RF and Pi control both work

## Updated Pi Controller

Our Pi controller becomes much simpler:

```python
class SimpleTurretController:
    def __init__(self):
        self.cyberbrick = serial.Serial('/dev/ttyUSB0', 115200)
        
    def enable_auto_mode(self):
        self.cyberbrick.write(b"MODE:AUTO\n")
        response = self.cyberbrick.readline()
        return b"AUTO_OK" in response
        
    def move_turret(self, pwm1=90, pwm2=90, pwm3=90):
        cmd = f"MOVE:PWM1={pwm1},PWM2={pwm2},PWM3={pwm3}\n"
        self.cyberbrick.write(cmd.encode())
        
    def fire_sequence(self):
        self.move_turret(pwm3=0)   # Fire
        time.sleep(0.5)
        self.move_turret(pwm3=20)  # Stop (from Water+Turret.json)
```

## Next Steps

1. **Clone repository**: Get the official CyberBrick code
2. **Study existing code**: Understand current RC application structure  
3. **Add Pi interface**: Extend control.py with serial communication
4. **Test integration**: Verify RF and Pi control work together
5. **Upload and test**: Deploy to Controller Core and test functionality

This approach gives us the best of both worlds - we keep all existing functionality while adding intelligent Pi control through the official, proven codebase. 