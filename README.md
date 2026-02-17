# TFS - Modbus RTU Slave with Excel Integration

A robust Python desktop application that acts as a Modbus RTU Slave, converting values from an Excel file (`data.xlsx`) into Modbus registers for PLCs to read.

## Features
- **Modbus RTU Slave**: Communicates over RS485/Serial.
- **Excel Integration**: dynamically reads values from `.xlsx` files without locking them.
- **Headless Mode**: Automatically switches to console interface if GUI (Tkinter) is unavailable.
- **Thread-safe**: Dedicated threads for Modbus Server, Excel Polling, and Logging.
- **Configurable**: JSON-based configuration for registers and serial settings.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/parth1512/TFS.git
    cd TFS
    ```

2.  **Set up Virtual Environment** (Recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you want the GUI on macOS, you might need `brew install python-tk`.*

## Configuration (`config.json`)

Edit `config.json` to match your hardware and register map.

```json
{
    "serial": {
        "port": "COM3",      // Change to /dev/ttyUSB0 or /dev/tty.usbserial... on Linux/Mac
        "baudrate": 9600,
        "parity": "N",
        "stopbits": 1,
        "slave_id": 1
    },
    "register_map": [
        {
            "excel_cell": "A1",
            "register": 40001,
            "type": "U16"
        },
        {
            "excel_cell": "A4",
            "register": 40005,
            "type": "FLOAT"
        }
    ]
}
```

## Usage

1.  **Run the application**:
    ```bash
    python main.py
    ```

2.  **Interact**:
    - **GUI Mode**: Click "Start Server".
    - **Headless Mode** (Terminal): Type `start` and press Enter.

3.  **Update Data**:
    - Open `data.xlsx`.
    - Change values in mapped cells (e.g., A1).
    - Save the file.
    - Watch the logs in the app; values will update in the Modbus registers instantly.

## Building Executable (.exe)

To package for Windows/Mac distribution:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "TFS_Modbus" --add-data "config.json;." --add-data "data.xlsx;." --hidden-import "pymodbus.datastore.context" main.py
```
*(On Mac/Linux replace `;` with `:` in `--add-data`)*

## Troubleshooting
- **Port Invalid**: Check `config.json` for the correct COM port.
- **Import Errors**: Ensure you have installed packages from `requirements.txt`.
