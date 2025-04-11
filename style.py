"""
Spotify-inspired styling for the SuSheProcessor application.
This module contains all style definitions, colors, and custom widget classes.
"""

from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt

# Spotify color palette
SPOTIFY_BLACK = "#121212"
SPOTIFY_DARK_GRAY = "#212121"
SPOTIFY_MEDIUM_GRAY = "#535353"
SPOTIFY_LIGHT_GRAY = "#b3b3b3"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_GREEN = "#1DB954"
SPOTIFY_GREEN_HOVER = "#1ED760"
SPOTIFY_FONT = "Gotham"  # Spotify uses Gotham, but we'll fall back to system fonts

# Style sheets for different widgets
MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {SPOTIFY_BLACK};
}}
"""

CENTRAL_WIDGET_STYLE = f"""
QWidget {{
    background-color: {SPOTIFY_BLACK};
    color: {SPOTIFY_WHITE};
}}
QLabel {{
    color: {SPOTIFY_WHITE};
    font-size: 13px;
}}
QLineEdit {{
    background-color: {SPOTIFY_DARK_GRAY};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
    border-radius: 4px;
    padding: 8px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {SPOTIFY_GREEN};
}}
"""

TITLE_LABEL_STYLE = f"""
color: {SPOTIFY_WHITE}; 
margin-bottom: 10px;
"""

SUBTITLE_STYLE = f"""
color: {SPOTIFY_LIGHT_GRAY}; 
font-size: 14px; 
margin-bottom: 20px;
"""

SEPARATOR_STYLE = f"""
background-color: {SPOTIFY_MEDIUM_GRAY}; 
max-height: 1px;
"""

SECTION_HEADER_STYLE = f"""
color: {SPOTIFY_WHITE}; 
margin-top: 20px;
"""

SCROLL_AREA_STYLE = f"""
QScrollArea {{
    border: none;
    background-color: {SPOTIFY_BLACK};
}}
QScrollBar:vertical {{
    background-color: {SPOTIFY_BLACK};
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {SPOTIFY_MEDIUM_GRAY};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

FILES_FRAME_STYLE = f"""
QFrame {{
    background-color: {SPOTIFY_DARK_GRAY};
    border-radius: 8px;
    padding: 5px;
}}
"""

STATUS_LABEL_STYLE = f"""
color: {SPOTIFY_LIGHT_GRAY}; 
font-size: 12px;
"""

FILE_ENTRY_STYLE = f"""
QFrame {{
    background-color: {SPOTIFY_DARK_GRAY};
    border-radius: 6px;
    padding: 10px;
}}
"""

FILE_NAME_STYLE = f"""
color: {SPOTIFY_WHITE};
"""

USERNAME_LABEL_STYLE = f"""
color: {SPOTIFY_LIGHT_GRAY};
"""

USERNAME_INPUT_SUCCESS_STYLE = f"""
QLineEdit {{
    background-color: #192d1e;
    color: {SPOTIFY_WHITE};
    border: 1px solid #1DB954;
    border-radius: 4px;
    padding: 8px;
}}
QLineEdit:focus {{
    border: 2px solid {SPOTIFY_GREEN};
}}
"""

USERNAME_INPUT_ERROR_STYLE = f"""
QLineEdit {{
    background-color: #2d1919;
    color: {SPOTIFY_WHITE};
    border: 1px solid #B33A3A;
    border-radius: 4px;
    padding: 8px;
}}
QLineEdit:focus {{
    border: 2px solid #FF5C5C;
}}
"""

MESSAGE_BOX_STYLE = f"""
QMessageBox {{
    background-color: {SPOTIFY_BLACK};
    color: {SPOTIFY_WHITE};
}}
QLabel {{
    color: {SPOTIFY_WHITE};
}}
QPushButton {{
    background-color: {SPOTIFY_GREEN};
    color: {SPOTIFY_BLACK};
    border-radius: 16px;
    padding: 8px 16px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {SPOTIFY_GREEN_HOVER};
}}
"""

FILE_DIALOG_STYLE = f"""
QFileDialog {{
    background-color: {SPOTIFY_BLACK};
    color: {SPOTIFY_WHITE};
}}
QLabel {{
    color: {SPOTIFY_WHITE};
}}
QListView, QTreeView {{
    background-color: {SPOTIFY_DARK_GRAY};
    color: {SPOTIFY_WHITE};
    selection-background-color: {SPOTIFY_GREEN};
    selection-color: {SPOTIFY_BLACK};
}}
QComboBox {{
    background-color: {SPOTIFY_DARK_GRAY};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
    border-radius: 4px;
    padding: 5px;
}}
QLineEdit {{
    background-color: {SPOTIFY_DARK_GRAY};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
    border-radius: 4px;
    padding: 5px;
}}
QPushButton {{
    background-color: {SPOTIFY_DARK_GRAY};
    color: {SPOTIFY_WHITE};
    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
    border-radius: 4px;
    padding: 5px 15px;
}}
QPushButton:hover {{
    background-color: {SPOTIFY_MEDIUM_GRAY};
}}
"""


class SpotifyStyleButton(QPushButton):
    """Custom button class with Spotify styling."""
    
    def __init__(self, text, parent=None, primary=True):
        super().__init__(text, parent)
        self.primary = primary
        self.setFont(QFont(SPOTIFY_FONT, 10, QFont.Weight.DemiBold))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(40)
        
        if primary:
            # Green primary button
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SPOTIFY_GREEN};
                    color: {SPOTIFY_BLACK};
                    border-radius: 20px;
                    border: none;
                    padding: 8px 32px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {SPOTIFY_GREEN_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {SPOTIFY_GREEN};
                }}
                QPushButton:disabled {{
                    background-color: {SPOTIFY_MEDIUM_GRAY};
                    color: {SPOTIFY_LIGHT_GRAY};
                }}
            """)
        else:
            # Secondary dark button
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {SPOTIFY_WHITE};
                    border-radius: 20px;
                    border: 1px solid {SPOTIFY_LIGHT_GRAY};
                    padding: 8px 32px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {SPOTIFY_MEDIUM_GRAY};
                    border: 1px solid {SPOTIFY_WHITE};
                }}
                QPushButton:pressed {{
                    background-color: {SPOTIFY_MEDIUM_GRAY};
                }}
                QPushButton:disabled {{
                    color: {SPOTIFY_MEDIUM_GRAY};
                    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
                }}
            """)