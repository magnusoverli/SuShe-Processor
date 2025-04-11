# SuSheProcessor

A utility application for processing JSON lists exported from SuShe and generating comprehensive HTML reports with data visualizations.

## Features

- Load and process multiple JSON data files containing album information
- Automatically map usernames from filenames using standardized mappings
- Generate interactive HTML reports with:
  - Data tables of all albums
  - Geographic distribution of albums on a world map
  - Genre distribution visualizations
  - User contribution statistics
  - Artist popularity charts
  - Monthly genre trends
- Image processing and optimization for album covers

## Installation

### Prerequisites

- Windows OS (7/8/10/11)
- 64-bit system

### Installation Options

#### Option 1: Installer (Recommended)

1. Download the latest installer from the [Releases](https://github.com/yourusername/SuShe-Processor/releases) page
2. Run the installer and follow the instructions
3. SuSheProcessor will be available in your Start Menu and Desktop after installation

#### Option 2: Portable Version

1. Download the latest ZIP file from the [Releases](https://github.com/yourusername/SuShe-Processor/releases) page
2. Extract the ZIP file to any location on your computer
3. Run `SuSheProcessor.exe` to start the application

## Usage

1. Start SuSheProcessor
2. Click "Load JSON Data" to select one or more JSON files exported from SuShe
3. Verify or edit the usernames associated with each file
4. Click "Generate HTML Report" to create an interactive HTML report
5. The report will be saved to your Desktop and opened automatically in your default browser

## Development

### Requirements

- Python 3.9+
- Required packages listed in `requirements.txt`

### Setup Development Environment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/SuShe-Processor.git
   cd SuShe-Processor
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application in Development Mode

```
python main.py
```

### Building the Application

The application can be built using PyInstaller with the included spec file:

```
pyinstaller SuSheProcessor.spec -- [build option]
```

Build options:
- `--exe`: Build executable only (default)
- `--installer`: Build executable and installer
- `--release`: Build executable, installer, and create GitHub release

## Project Structure

- `main.py` - Main application code
- `template.html` - HTML template for report generation
- `username_mappings.json` - Standardized username mappings
- `SuSheProcessor.spec` - PyInstaller specification file
- `ProcessorInstaller.iss` - Inno Setup installer script
- `logos/` - Application icons and graphics
- `version.txt` - Application version information

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.