# 🐕🤚 Unitree Go2 Hand Gesture Control

> **Control your robotic dog with just a wave of your hand** ✨

Transform your Unitree Go2 into an obedient companion that responds to hand gestures! This project combines computer vision, AI gesture recognition, and robotics to create an intuitive human-robot interface. No remote controls, no complex commands—just natural hand movements that your robot dog understands.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)]()
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)]()
[![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)]()
[![MediaPipe](https://img.shields.io/badge/MediaPipe-00D4FF?style=for-the-badge&logo=google&logoColor=white)]()

## 📋 Table of Contents

- [✨ Features](#-features)
- [🎯 How It Works](#-how-it-works)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🎮 Usage](#-usage)
- [🤖 Supported Gestures](#-supported-gestures)
- [🛠️ Development](#️-development)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

## ✨ Features

- 🎯 **Real-time Gesture Recognition** - Powered by MediaPipe for lightning-fast hand detection
- 🤖 **Seamless Robot Control** - Direct integration with Unitree Go2 SDK
- 📺 **Live Video Stream** - Web interface to monitor your robot's perspective
- 🔋 **Battery Monitoring** - Real-time battery level display with color-coded alerts
- 🐳 **Docker Ready** - Containerized deployment for easy setup
- 🔧 **Debug Mode** - Test gestures using your computer's webcam
- 📊 **Multi-threaded Performance** - Smooth gesture detection without blocking robot control

## 🎯 How It Works

```
Your Hand Gesture → MediaPipe AI → Gesture Classification → Robot Action
       👋               🧠                  📝                  🐕
```

The system captures video frames from the Unitree Go2's camera, processes them through a trained gesture recognition model, and translates detected gestures into robot commands. It's like teaching your dog new tricks, except this dog is made of metal and responds instantly!

## 🚀 Quick Start

**Prerequisites:** Docker, Docker Compose, and a Unitree Go2 robot (obviously! 😄)

```bash
# Clone the repository
git clone https://github.com/DellerbaRobotics/hand_gesture_unitree.git
cd hand_gesture_unitree

# Set your network interface
export NET_IFACE=eth0  # Replace with your actual interface

# Launch the system
docker compose up --build
```

That's it! Your gesture-controlled robot is now ready to respond to your commands.

## 📦 Installation

### System Requirements

- **Hardware**: Unitree Go2 robot with camera access
- **OS**: Linux (Ubuntu 22.04 recommended)
- **Network**: Robot and host on the same network
- **Dependencies**: Docker & Docker Compose

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DellerbaRobotics/hand_gesture_unitree.git
   cd hand_gesture_unitree
   ```

2. **Network Configuration**
   ```bash
   # Find your network interface
   ip addr show
   
   # Set the interface (replace eth0 with your interface)
   export NET_IFACE=eth0
   ```

3. **Build and Run**
   ```bash
   docker compose up --build
   ```

4. **Access the Video Stream**
   - Open your browser and navigate to `http://localhost:5000/video`
   - You should see the live feed from your robot's perspective!

## 🎮 Usage

### Basic Operation

Once the system is running, simply perform gestures in front of the robot's camera:

```python
# The robot will automatically detect and respond to:
👋 Open Hand    → `Hello` animation
✊ Closed Fist  → `Front Pounce` action  
✌️ Victory     → `Heart` gesture
👍 Thumbs Up   → `Stand Up` command
👎 Thumbs Down → `Damp` (lie down) action
👆 Point Up    → `Stretch` routine
```

### Debug Mode

Want to test without the robot? Enable debug mode:

```bash
# Use your computer's webcam instead
DEBUG=1 docker compose up --build
```

Perfect for developing new gestures or testing the recognition accuracy!

### Monitoring

- **Video Feed**: `http://localhost:5000/video`
- **Battery Status**: Displayed on the video overlay
  - 🟢 Green: >60% battery
  - 🟠 Orange: 25-60% battery  
  - 🔴 Red: <25% battery

## 🤖 Supported Gestures

| Gesture | Robot Action | Description |
|---------|--------------|-------------|
| 👋 **Open Palm** | `Hello()` | Friendly greeting animation |
| ✊ **Closed Fist** | `FrontPounce()` | Playful pouncing motion |
| ✌️ **Victory** | `Heart()` | Cute heart shape with front paws |
| 👍 **Thumbs Up** | `StandUp()` | Stand up from any position |
| 👎 **Thumbs Down** | `Damp()` | Lie down gracefully |
| 👆 **Point Up** | `Stretch()` | Full body stretch routine |

*Confidence threshold: 50% (adjustable in `hand_reader.py`)*

## 🛠️ Development

### Project Structure

```
unitree-gesture-control/
├── 🐳 docker compose.yml          # Multi-container orchestration
├── gesture_recognition/
│   ├── unitreesdk2/               # Unitree Go2 SDK
│       └── 📦 ...                 # SDK modules and libraries
│   ├── 📱 app.py                  # Main gesture control logic
│   ├── 👁️ hand_reader.py          # MediaPipe gesture recognition
│   ├── 🤖 gesture_recognizer.task # Pre-trained gesture model
│   ├── 📋 requirements.txt        # Python dependencies
│   └── 🐳 Dockerfile               # Container build instructions
├── web/
│   ├── 🌐 app.py                  # Flask video streaming server
│   ├── 📋 requirements.txt        # Web server dependencies
│   └── 🐳 Dockerfile               # Container build instructions
└── 📖 README.md                   # You are here!
```

### Adding New Gestures

1. **Train a New Model** 📚:
   ```bash
   # You'll need to create a new dataset with your gesture
   # and train a new MediaPipe gesture recognition model
   # This generates a new gesture_recognizer.task file
   # See MediaPipe documentation for training custom gestures
   ```

2. **Update the Enum**:
   ```python
   # hand_reader.py
   class DogState(enum.Enum):
       YourNewGesture = 8  # Add your gesture
   ```

3. **Map to Robot Action**:
   ```python
   # app.py
   self.dog_moves = {
       DogState.YourNewGesture: self.client.YourRobotMethod,
   }
   ```

4. **Update Recognition Logic**:
   ```python
   # hand_reader.py
   def ConvTextToEnum(str):
       if str == "Your_Gesture_Name":
           return DogState.YourNewGesture
   ```

5. **Replace the Model File**:
   ```bash
   # Replace the old model with your newly trained one
   cp your_new_gesture_recognizer.task gesture_recognition/gesture_recognizer.task
   ```

### Testing

```bash
# Test with webcam (debug mode)
DEBUG=1 docker compose up --build
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🙏 Acknowledgments

- **Unitree Robotics** for creating such a <s>not really</s> awesome robotic platform
- **Google MediaPipe** for the incredible hand tracking technology
- **OpenCV** for reliable computer vision tools
- **Docker** for making deployment a breeze

---

<div align="center">

### 🌟 **Ready to give your robot dog some serious hand-eye coordination?**

**Star this repo** if you found it useful, and **share** your gesture-controlled robot videos with us!

[⭐ Star this repo](https://github.com/DellerbaRobotics/hand_gesture_unitree) • [🐛 Report Bug](https://github.com/DellerbaRobotics/hand_gesture_unitree/issues)

---

*Made with ❤️ by lousy developers*

</div>