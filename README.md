# IoT Workshop Receiver

A cross-platform desktop **Receiver Application** for IoT workshops, built with
**Python**, **PySide6 (Qt)**, **WebSocket** and **asyncio**.

When the application starts it connects to the cloud server. The server assigns
a unique **receiver code** (e.g. `RX-A31F9D`) which is displayed prominently.
Students use that code inside their own web applications to route messages to
this receiver. Whenever a message arrives it appears **instantly** in the live
logs.

---

## Features

- **Cloud connection** via WebSocket with auto-reconnect and heartbeat/ping
  latency measurement.
- **Prominent receiver code** display with one-click copy.
- **Live statistics**: messages received, connected since, last message, server
  latency.
- **Live logs** table (newest first) with timestamp, device, message type and
  pretty-printed JSON data.
- **Formatted message cards** for known types: `temperature`, `humidity`,
  `gps`, `alert`, `custom`.
- **Settings**: cloud URL, dark mode, auto reconnect, maximum logs — saved
  locally.
- **Export** logs as **JSON** or **TXT**.
- **Security**: received data is never executed, everything is treated as text,
  JSON is validated, message size is limited, malformed messages are rejected.
- **PyInstaller** build support for Windows executable generation.
- Designed for **30–100 concurrent receiver connections**.

---

## Screenshots

> Screenshots will be added here.

![Main Window](docs/screenshot_main.png)
![Settings](docs/screenshot_settings.png)

---

## Project Structure

```
IoT-Workshop-Receiver/
├── receiver/
│   ├── ui/            # Main window, settings dialog, message cards
│   ├── network/       # Async WebSocket client
│   ├── models/        # Data models (message, settings, log entry)
│   ├── services/      # Settings persistence, log store, export
│   └── resources/     # Stylesheets (light / dark)
├── main.py            # Application entry point
├── requirements.txt
├── receiver.spec      # PyInstaller spec
├── build.ps1          # Windows build script
├── build.sh           # Linux build script
└── README.md
```

---

## Installation

### Prerequisites

- Python **3.10+**
- pip

### Steps

```bash
git clone https://github.com/aswindatha/IoT-Workshop-Receiver.git
cd IoT-Workshop-Receiver

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

## Running

```bash
python main.py
```

The application window opens and immediately attempts to connect to the
configured cloud server.

---

## Connecting

1. Open **Settings** (top-right button).
2. Enter the **Cloud URL** of the workshop server (e.g.
   `wss://iot-workshop-server.example.com/ws/receiver`).
3. Enable **Auto reconnect** if desired.
4. Click **Save** — the receiver reconnects using the new URL.
5. Once connected, the server assigns a **receiver code** (e.g. `RX-A31F9D`)
   shown at the top-right of the header.
6. Click **Copy Receiver Code** and share it with students.

The connection indicator in the header shows **Online** / **Offline** /
**Connecting…**. Server latency is updated on every heartbeat ping/pong cycle.

---

## Workshop Usage

1. **Instructor** launches one (or more) receiver instances.
2. Each instance receives a unique **receiver code**.
3. **Students** open their own web applications and send messages to the cloud
   server using their assigned receiver code, for example:

   ```json
   {
     "receiver": "RX-A31F9D",
     "device": "sensor-01",
     "type": "temperature",
     "timestamp": "2026-07-18T09:00:00Z",
     "data": {
       "value": 26.4,
       "unit": "celsius"
     }
   }
   ```

4. Messages appear **instantly** in the receiver's live logs with formatted
   JSON cards.
5. Use **Export Logs** to save the session as JSON or TXT for grading or
   review.

The application is designed to handle **30–100 concurrent receiver
connections** thanks to the lightweight asyncio WebSocket client.

---

## Settings

| Setting        | Description                                      | Default                                   |
|----------------|--------------------------------------------------|-------------------------------------------|
| Cloud URL      | WebSocket URL of the workshop server             | `wss://iot-workshop-server.example.com/ws/receiver`|
| Dark mode      | Toggle dark / light theme                        | Enabled                                   |
| Auto reconnect | Automatically reconnect after disconnection     | Enabled                                   |
| Maximum logs   | Number of log entries kept in memory             | 500                                       |

Settings are persisted to:
- Windows: `%APPDATA%\IoTWorkshopReceiver\settings.json`
- Linux: `~/.IoTWorkshopReceiver/settings.json` (or `$HOME`)

---

## Security

- Received data is **never executed** — everything is treated as text.
- JSON payloads are **validated**; non-JSON payloads are stored as raw text.
- Message size is **limited** to 64 KiB; oversized messages are rejected.
- Malformed messages are handled gracefully without crashing the app.

---

## Export

Click **Export Logs** and choose a format:

- **JSON** — structured array of all log entries.
- **TXT** — human-readable plain text.

---

## Build (Windows executable)

### Using the build script (PowerShell)

```powershell
.\build.ps1
# or with a clean rebuild:
.\build.ps1 -Clean
```

### Manual PyInstaller

```bash
pip install pyinstaller
pyinstaller --noconfirm receiver.spec
```

The executable is generated under `dist/IoT-Workshop-Receiver/`.

### Linux

```bash
bash build.sh
# or:
bash build.sh --clean
```

---

## Tech Stack

| Layer       | Technology            |
|-------------|-----------------------|
| Language    | Python 3.10+          |
| UI          | PySide6 (Qt 6)        |
| Transport   | WebSocket (`websockets`) |
| Concurrency | asyncio               |
| Packaging   | PyInstaller           |
| Platforms   | Windows (first), Linux|

---

## License

Released for workshop / educational use.
