# Screen On Time Tracker

> A lightweight Windows terminal dashboard for tracking screen-on time and battery usage.

The Screen On Time Tracker monitors your laptop display and power state while you use your computer on battery. It records screen-on time, detects charging and sleep events, and estimates total screen-on time from the battery used during the current session.

![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-add%20your%20license-lightgrey?style=flat-square)

## Features

- Live terminal dashboard with screen time, battery level, battery used, and estimates.
- Tracks screen-on time only while the internal display is active.
- Detects display on/off and dimmed states through Windows power notifications.
- Detects unplugging, plugging in, suspend, and resume events.
- Pauses tracking when the display is off, the computer is suspended, or AC power is connected.
- Starts a new battery session when the charger is unplugged.
- Detects charging that occurred while the computer was suspended.
- Keeps a timestamped event log in the dashboard.

## Requirements

- Windows 10 or later
- Python 3.8 or later
- A battery-powered Windows laptop or tablet for battery tracking
- `pywin32` (installed from `requirements.txt`)

`ctypes`, `json`, `datetime`, `os`, `threading`, `time`, and `uuid` are Python standard-library modules. They do not need to be installed separately.

## Installation

### 1. Get the project

Clone the repository and open its folder:

```powershell
git clone https://github.com/<your-username>/<your-repository>.git
cd Screen_On_Time
```

Alternatively, use **Code > Download ZIP** on GitHub, extract the archive, and open the extracted folder in a terminal.

### 2. Create a virtual environment

Using a virtual environment keeps this project's packages separate from other Python projects:

```powershell
py -3 -m venv .venv
```

If the `py` command is unavailable, use:

```powershell
python -m venv .venv
```

### 3. Activate the environment

In PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

In Command Prompt:

```bat
.venv\Scripts\activate.bat
```

If PowerShell blocks activation, run this once in PowerShell for your user account, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Tracker

With the virtual environment active, run:

```powershell
python main.py
```

The dashboard refreshes in the terminal. Press `Ctrl+C` to stop the tracker and display the final screen-on time.

You can also use `SOT_Calculator_Terminal.bat`. Before using it on another computer, edit its `cd /d` line so it points to the folder where you placed this project. For example:

```bat
@echo off
cd /d "C:\Users\YourName\Projects\Screen_On_Time"
call .venv\Scripts\activate.bat
python main.py
pause
```

The batch file expects the virtual environment to be named `.venv` and to be located in the project folder.

## Creating a Shortcut

You can place a shortcut to the batch file on the **Desktop**, in the **Start Menu**, or in both locations.

### Create the shortcut

1. Open the project folder in File Explorer.
2. Right-click `SOT_Calculator_Terminal.bat`.
3. Select **Show more options** if necessary, then choose **Create shortcut**.
4. Windows may create the shortcut in the project folder with a name such as `SOT_Calculator_Terminal - Shortcut`.
5. Rename it if desired, for example, `Screen On Time Tracker`.

### Put it on the Desktop

Drag the new shortcut to the Desktop, or right-click it and choose **Send to > Desktop (create shortcut)**.

### Put it in the Start Menu

1. Press `Win + R`.
2. Enter `shell:programs` and press **Enter**. This opens your personal Start Menu Programs folder.
3. Move or copy the shortcut into that folder.
4. Open Start and search for **Screen On Time Tracker**.

For a shortcut available to every user on the computer, enter `shell:common programs` instead. Windows may ask for administrator permission.

### Optional shortcut settings

Right-click the shortcut, select **Properties**, and use the **Shortcut** tab to:

- Set **Start in** to the project folder.
- Choose **Change Icon...** if you want a custom icon.
- Set **Run** to **Minimized** if you prefer the terminal window to open minimized.

The batch file already changes to the project directory, but setting **Start in** makes the shortcut's working directory explicit.

## Configuration

On first launch, the tracker identifies the primary internal display and stores its monitor prefix in `config.json`. This lets the tracker distinguish the laptop's built-in display from external monitors.

If the internal display is replaced or the stored monitor information becomes outdated, close the tracker, delete `config.json`, and start the application again. A new configuration file will be generated automatically.

## Troubleshooting

### `'python' is not recognized`

Install Python from [python.org](https://www.python.org/downloads/windows/) and enable **Add Python to PATH** during installation. Then open a new terminal.

### `ModuleNotFoundError: No module named 'win32api'`

Activate the virtual environment and reinstall the dependency:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### The batch file closes or cannot find `.venv`

Confirm that `.venv` exists in the project folder and that the `cd /d` path in `SOT_Calculator_Terminal.bat` points to the correct project location.

### The dashboard reports the wrong display

Delete `config.json` and run the tracker again while the intended internal display is connected and active.

### The estimate says `Calculating...`

The tracker needs measurable battery drain before it can estimate total screen-on time. This is expected when the battery percentage has not changed yet.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Runs the dashboard and coordinates tracking. |
| `time_tracker.py` | Tracks elapsed screen-on time and calculates estimates. |
| `power_listener.py` | Receives Windows display and suspend/resume notifications. |
| `display_utils.py` | Finds and checks the primary internal display. |
| `requirements.txt` | Lists Python dependencies. |
| `config.json` | Stores the detected internal display prefix. |
| `SOT_Calculator_Terminal.bat` | Activates the virtual environment and starts the tracker. |
| `Archives/` | Contains older project files kept for reference. |

## Limitations

- This project currently supports Windows only.
- Battery percentage is reported by Windows in whole numbers, so estimates become more useful after some battery has been consumed.
- The tracker is designed for a terminal window and does not provide a graphical desktop interface.

## License

Add your preferred license here before publishing the repository, such as [MIT](https://choosealicense.com/licenses/mit/).