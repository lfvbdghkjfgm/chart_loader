# Chart Loader Installer

Windows installer:

- `installers/windows/install.bat`

## What it does

- downloads repository archive from GitHub
- installs the app from downloaded `src` into `C:\Program Files\ChartLoader\current`
- creates a Python virtual environment and installs dependencies
- creates global launcher command `chart-loader`
- adds install folder to system `PATH`
- creates `uninstall.bat` in the install folder

## How to run

```cmd
cd chart_loader\installers\windows
install.bat
```

Run installer as Administrator.

After installation, open a new terminal and run:

```cmd
chart-loader
```

Default source URL:

```text
https://github.com/lfvbdghkjfgm/chart_loader/archive/refs/heads/main.zip
```

To override source URL:

```cmd
set CHART_LOADER_REPO_ZIP_URL=https://github.com/<owner>/<repo>/archive/refs/heads/main.zip
install.bat
```
