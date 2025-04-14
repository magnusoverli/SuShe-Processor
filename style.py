"""
Spotify-inspired styling for the SuSheProcessor application.
This module contains all style definitions, colors, and custom widget classes.
"""

from PyQt6.QtWidgets import QPushButton, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt, QSize

# Spotify color palette
SPOTIFY_BLACK = "#121212"
SPOTIFY_DARK_GRAY = "#181818"  # Slightly lighter than pure black for cards
SPOTIFY_CARD_BORDER = "#282828"  # Border color for cards
SPOTIFY_MEDIUM_GRAY = "#535353"
SPOTIFY_LIGHT_GRAY = "#b3b3b3"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_GREEN = "#1DB954"
SPOTIFY_GREEN_HOVER = "#1ED760"
SPOTIFY_FONT = "Gotham"  # Spotify uses Gotham, but we'll fall back to system fonts

# Gradients
HEADER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1D1D1D, stop:1 #121212)"
BUTTON_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1ED760, stop:1 #1DB954)"
BUTTON_HOVER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1ED760, stop:1 #1ED760)"

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

HEADER_STYLE = f"""
background: {HEADER_GRADIENT};
border-radius: 8px;
padding: 24px;
margin-bottom: 20px;
"""

TITLE_LABEL_STYLE = f"""
color: {SPOTIFY_WHITE}; 
font-weight: bold;
"""

SUBTITLE_STYLE = f"""
color: {SPOTIFY_LIGHT_GRAY}; 
font-size: 14px; 
margin-top: 5px;
"""

SEPARATOR_STYLE = f"""
background-color: {SPOTIFY_MEDIUM_GRAY}; 
max-height: 1px;
margin: 15px 0;
"""

SECTION_HEADER_STYLE = f"""
color: {SPOTIFY_WHITE}; 
margin-top: 10px;
margin-bottom: 15px;
font-weight: bold;
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
    border: 1px solid {SPOTIFY_CARD_BORDER};
    border-radius: 8px;
    padding: 5px;
}}
"""

STATUS_LABEL_STYLE = f"""
color: {SPOTIFY_LIGHT_GRAY}; 
font-size: 12px;
margin-top: 10px;
"""

FILE_ENTRY_STYLE = f"""
QFrame {{
    background-color: {SPOTIFY_DARK_GRAY};
    border-radius: 4px;
    border: none;
    margin: 1px 0;
}}
QFrame:hover {{
    background-color: #252525;
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
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border: 1px solid {SPOTIFY_GREEN};
}}
"""

USERNAME_INPUT_ERROR_STYLE = f"""
QLineEdit {{
    background-color: #2d1919;
    color: {SPOTIFY_WHITE};
    border: 1px solid #B33A3A;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border: 1px solid #FF5C5C;
}}
"""

EMPTY_STATE_STYLE = f"""
QLabel {{
    color: {SPOTIFY_LIGHT_GRAY};
    font-size: 14px;
    padding: 20px;
    qproperty-alignment: AlignCenter;
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
    
    def __init__(self, text, parent=None, primary=True, icon=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setFont(QFont(SPOTIFY_FONT, 10, QFont.Weight.DemiBold))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(44)
        
        # Add icon if provided
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))
        
        if primary:
            # Green primary button
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {BUTTON_GRADIENT};
                    color: {SPOTIFY_BLACK};
                    border-radius: 22px;
                    border: none;
                    padding: 10px 32px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {BUTTON_HOVER_GRADIENT};
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
                    background-color: rgba(255, 255, 255, 0.1);
                    color: {SPOTIFY_WHITE};
                    border-radius: 22px;
                    border: 1px solid {SPOTIFY_LIGHT_GRAY};
                    padding: 10px 32px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid {SPOTIFY_WHITE};
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.15);
                }}
                QPushButton:disabled {{
                    color: {SPOTIFY_MEDIUM_GRAY};
                    border: 1px solid {SPOTIFY_MEDIUM_GRAY};
                }}
            """)


class EmptyStateWidget(QWidget):
    """Widget to display when no files are loaded."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 40)  # More space
        layout.setSpacing(20)  # Increased spacing
        
        # Simple clean icon
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)  # Smaller size
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("🎵")  # Simple emoji
        icon_label.setFont(QFont(SPOTIFY_FONT, 24))
        icon_label.setStyleSheet(f"color: {SPOTIFY_LIGHT_GRAY}; background-color: transparent;")
        
        # Simple message
        empty_message = QLabel("No files loaded")
        empty_message.setFont(QFont(SPOTIFY_FONT, 14))
        empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_message.setStyleSheet(f"color: {SPOTIFY_WHITE}; background-color: transparent;")
        
        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty_message, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)