 🎵 ESP32 Spotify Deck

An ESP32-based Spotify desktop controller that displays currently playing music information on a **0.96-inch SSD1306 OLED display**.

This project uses Python and Windows Media Control APIs to retrieve music metadata and send it to an ESP32 over serial communication.

## ✨  Features

- 🎵 Displays currently playing song title
- 🎤 Displays artist and album information
- ▶️ Shows playback status (Playing / Paused)
- ⏱️ Displays track duration and playback progress
- 🎮 Keyboard controls for music playback
- 📟 Compact 0.96-inch OLED interface
- 🔌 Serial communication between Python and ESP32

## 🛠️ Hardware Requirements

| Component | Specification |
|---|---|
| Microcontroller | ESP32 Development Board |
| Display | 0.96-inch OLED |
| Display Driver | SSD1306 |
| Resolution | 128 × 64 |
| Communication | I2C |
| USB-to-Serial | CP2102 |

## 🔌 Circuit Connections

Connect the OLED display to the ESP32:

| OLED Pin | ESP32 Pin |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

**I2C Address:** `0x3C`

## 💻 Software Requirements

- Arduino IDE
- Python 3.11 or later
- ESP32 board package for Arduino IDE
- Adafruit SSD1306 Library
- Adafruit GFX Library
- PySerial
- WinRT Windows Media Control

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/aryayuvraj007/ESP32-Spotify-Deck.git
```

```bash
cd ESP32-Spotify-Deck
```

### 2. Install Python dependencies

```bash
py -m pip install pyserial winrt-Windows.Media.Control
```

### 3. Install Arduino libraries

Open Arduino IDE and install:

- Adafruit SSD1306
- Adafruit GFX Library

### 4. Upload ESP32 firmware

1. Open `firmware/spotify_deck_oled.ino`.
2. Select your ESP32 board.
3. Select the correct COM port.
4. Upload the firmware.

### 5. Run the Python application

Connect your ESP32 and run:

```bash
py python/spotify_deck_oled.py --port COM3
```

Replace `COM3` with your ESP32's actual serial port.

### 6. Play music

1. Open Spotify Desktop on Windows.
2. Play a song.
3. The ESP32 OLED should display the available track information.

## 🎮 Keyboard Controls

| Key | Action |
|---|---|
| `Space` | Play / Pause |
| `N` | Next Track |
| `P` | Previous Track |
| `Q` | Quit Application |

## ⚙️ How It Works

```text
       Spotify Desktop
              |
              v
    Windows Media Control
              |
              v
       Python Application
              |
              v
       Serial Communication
              |
              v
          ESP32 Board
              |
              v
       SSD1306 OLED Display
```

1. Spotify publishes playback information through Windows Media Session.
2. Python retrieves the available song metadata and playback information.
3. Python sends the information to ESP32 through serial communication.
4. ESP32 processes the received data.
5. OLED displays the song information and playback progress.

## 🚀 Future Improvements

- [ ] Album artwork support using a compatible display
- [ ] Physical buttons for music control
- [ ] Improved OLED animations
- [ ] Volume control
- [ ] Custom UI themes
- [ ] Wi-Fi-based controls

## ⚠️ Notes

- This project is designed for Windows.
- Spotify metadata availability depends on Windows Media Session support.
- Album artwork is not displayed on the current monochrome SSD1306 OLED.
- Close Arduino Serial Monitor before running the Python application.
---

**Built with ❤️ using ESP32, Python, and Arduino.**
