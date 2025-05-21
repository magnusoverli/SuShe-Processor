import os
import sys
import platform
import json
from typing import Tuple, Dict, Optional, Any

import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QFileDialog, QMessageBox, QLineEdit, QLabel, QScrollArea, QFrame, QStyle,
    QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QFontDatabase
from jinja2 import Environment, FileSystemLoader
import webbrowser
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path

import style

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    """
    Main application window for the SuSheProcessor.
    
    This application loads JSON data files containing album information,
    processes the data, and generates an HTML report with visualizations.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuSheProcessor")
        self.setGeometry(100, 100, 800, 600)
        
        # Set window icon - ADD THIS CODE
        icon_path = resource_path('logos/sushe_processor.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        # Apply Spotify theme to the entire application
        self.apply_spotify_theme()
        
        # Initialize data structures
        self.loaded_files = []  # List to store tuples of (file_path, username_widget)
        self.username_map = {}  # Dictionary to map variations to standard usernames
        
        # Load username mappings
        self.load_username_mappings()
        
        # Setup UI
        self.setup_ui()
    
    def apply_spotify_theme(self):
        """Apply the Spotify-inspired theme to the application."""
        # Set dark background color to the main window
        self.setStyleSheet(style.MAIN_WINDOW_STYLE)
    
    def setup_ui(self):
        """Set up the main user interface components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)  # Reduced spacing
        main_layout.setContentsMargins(30, 20, 30, 20)  # Reduced top/bottom margins
        
        # Header section with integrated load button
        header_section = QWidget()
        header_layout = QHBoxLayout(header_section)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label = QLabel("SuSheProcessor")
        title_label.setFont(QFont(style.SPOTIFY_FONT, 24, QFont.Weight.Bold))
        title_label.setStyleSheet(style.TITLE_LABEL_STYLE)
        header_layout.addWidget(title_label)
        
        # Add spacer to push title to left and button to right
        header_layout.addStretch()
        
        # Load JSON Button with icon - moved up
        self.load_button = style.SpotifyStyleButton(
            "Import lists", 
            primary=True,
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart)
        )
        self.load_button.clicked.connect(self.load_json)
        header_layout.addWidget(self.load_button)
        
        main_layout.addWidget(header_section)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(style.SEPARATOR_STYLE)
        main_layout.addWidget(separator)
        
        # Files section with improved styling - expanded to use more space
        files_section = QFrame()
        files_layout = QVBoxLayout(files_section)
        files_layout.setContentsMargins(0, 0, 0, 0)
        
        # Files section header with better spacing
        files_header_layout = QHBoxLayout()
        files_header_layout.setContentsMargins(5, 0, 5, 5)
        
        files_header = QLabel("Loaded Files")
        files_header.setFont(QFont(style.SPOTIFY_FONT, 16, QFont.Weight.Bold))
        files_header.setStyleSheet(style.SECTION_HEADER_STYLE)
        files_header_layout.addWidget(files_header)
        
        files_header_layout.addStretch()
        files_layout.addLayout(files_header_layout)
        
        # Create a stacked widget to switch between empty state and file list
        self.files_stack = QStackedWidget()
        
        # Empty state widget (shown when no files are loaded)
        self.empty_state = style.EmptyStateWidget()
        
        # Content widget with file list only (header moved outside)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area for loaded files
        self.files_scroll_area = QScrollArea()
        self.files_scroll_area.setWidgetResizable(True)
        self.files_scroll_area.setStyleSheet(style.SCROLL_AREA_STYLE)
        
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setSpacing(2)  # Reduced spacing between items
        self.files_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        self.files_scroll_area.setWidget(self.files_container)
        
        content_layout.addWidget(self.files_scroll_area)
        
        # Add both widgets to the stack
        self.files_stack.addWidget(self.empty_state)
        self.files_stack.addWidget(content_widget)
        self.files_stack.setCurrentIndex(0)  # Start with empty state
        
        # Wrap stack in a styled frame
        files_frame = QFrame()
        files_frame.setStyleSheet(style.FILES_FRAME_STYLE)
        files_frame.setMinimumHeight(300)  # Increased height to use more available space
        files_frame_layout = QVBoxLayout(files_frame)
        files_frame_layout.setContentsMargins(10, 10, 10, 10)
        files_frame_layout.addWidget(self.files_stack)
        
        files_layout.addWidget(files_frame)
        main_layout.addWidget(files_section, 1)  # Add stretch factor to make this section expand
        
        # Action buttons layout with better spacing
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 10, 0, 10)
        
        # Generate HTML Button
        self.generate_button = style.SpotifyStyleButton(
            "Generate HTML Report", 
            primary=True,
            icon=QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        )
        self.generate_button.clicked.connect(self.generate_html)
        self.generate_button.setEnabled(False)
        buttons_layout.addWidget(self.generate_button)
        
        # Exit Button
        self.exit_button = style.SpotifyStyleButton(
            "Exit", 
            primary=False,
            icon=QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        )
        self.exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Status message label with simpler design
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.NoFrame)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        # Blue info circle icon
        status_icon = QLabel()
        status_icon.setFixedSize(16, 16)
        status_pixmap = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation).pixmap(12, 12)
        status_icon.setPixmap(status_pixmap)
        status_layout.addWidget(status_icon)
        
        # Status text
        self.status_label = QLabel("Ready to process files")
        self.status_label.setStyleSheet(style.STATUS_LABEL_STYLE)
        self.status_label.setFont(QFont(style.SPOTIFY_FONT, 9))  # Smaller font
        status_layout.addWidget(self.status_label, 1)  # 1 = stretch factor
        
        # Add extra stretch to ensure status stays on left
        status_layout.addStretch(3)
        
        main_layout.addWidget(status_frame)
        
        # Set main layout to central widget
        container = QWidget()
        container.setStyleSheet(style.CENTRAL_WIDGET_STYLE)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_username_mappings(self, mapping_file='username_mappings.json'):
        """
        Load username mappings from a JSON file.
        Each mapping contains a standardized username and its possible variations.
        
        Args:
            mapping_file (str): Path to the mapping file
        """
        try:
            mapping_path = resource_path(mapping_file)  # Use resource_path
            with open(mapping_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            # Create a dictionary for quick lookup
            for entry in mappings:
                standard = entry['standard']
                for variation in entry['variations']:
                    # Normalize variation to lowercase for case-insensitive matching
                    self.username_map[variation.lower()] = standard
        except FileNotFoundError:
            self.show_error("Mapping File Not Found", 
                          f"The mapping file '{mapping_file}' was not found.")
            self.username_map = {}
        except json.JSONDecodeError as e:
            self.show_error("Invalid Mapping File",
                          f"Failed to parse '{mapping_file}':\n{e}")
            self.username_map = {}

    def show_error(self, title: str, message: str):
        """Show an error message box with the given title and message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(style.MESSAGE_BOX_STYLE)
        msg_box.exec()
        
    def show_info(self, title: str, message: str):
        """Show an information message box with the given title and message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(style.MESSAGE_BOX_STYLE)
        msg_box.exec()
        
    def show_warning(self, title: str, message: str):
        """Show a warning message box with the given title and message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(style.MESSAGE_BOX_STYLE)
        msg_box.exec()

    def load_json(self):
        """Load multiple JSON files and display them with username input fields."""
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet(style.FILE_DIALOG_STYLE)
        
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Open JSON Files", "", "JSON Files (*.json)"
        )
        
        if not file_paths:
            return
            
        for path in file_paths:
            if any(f[0] == path for f in self.loaded_files):
                self.show_warning("Duplicate File", f"'{os.path.basename(path)}' is already loaded.")
                continue
                
            try:
                # Attempt to load JSON to validate
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except Exception as e:
                self.show_error("Invalid JSON", f"Failed to load '{os.path.basename(path)}':\n{e}")
                continue
            
            # Extract username from file name based on the mapping
            username = self.extract_username_from_filename(os.path.basename(path))
            
            # Create file entry widget with the extracted username
            file_widget = self.create_file_entry_widget(path, default_username=username)
            self.files_layout.addWidget(file_widget)
            
            # If username was not extracted, inform the user
            if not username:
                self.show_info("Username Not Found", 
                            f"No matching username found in the file name '{os.path.basename(path)}'. Please enter it manually.")
            
            # Store the file path and username widget
            username_input = file_widget.findChild(QLineEdit)
            username_input.textChanged.connect(self.update_generate_button_state)
            self.loaded_files.append((path, username_input))
        
        # Update UI state - switch to file list view if files were loaded
        if self.loaded_files and self.files_stack.currentIndex() == 0:
            self.files_stack.setCurrentIndex(1)
            
        self.update_generate_button_state()
        self.status_label.setText(f"{len(self.loaded_files)} files loaded")

    def create_file_entry_widget(self, file_path: str, default_username: str = "") -> QWidget:
        """
        Create a widget representing a loaded JSON file with an icon and username input.
        
        Args:
            file_path (str): Path to the JSON file
            default_username (str): Default username to display
            
        Returns:
            QWidget: A widget containing file information and username input
        """
        widget = QFrame()
        widget.setStyleSheet(style.FILE_ENTRY_STYLE)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)  # Reduced vertical padding
        layout.setSpacing(10)  # Slightly reduced spacing
        widget.setLayout(layout)
        
        # File icon
        icon_label = QLabel()
        pixmap = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon).pixmap(16, 16)  # Smaller icon
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)
        
        # File name with ellipsis for long names
        file_name = os.path.basename(file_path)
        name_label = QLabel(file_name)
        name_label.setFont(QFont(style.SPOTIFY_FONT, 9))  # Smaller font
        name_label.setStyleSheet(style.FILE_NAME_STYLE)
        name_label.setFixedWidth(200)
        name_label.setToolTip(file_path)  # Show full path on hover
        # Enable text elision
        name_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(name_label)
        
        # Username input - simplified to take less space
        username_input = QLineEdit()
        username_input.setPlaceholderText("Username")
        username_input.setText(default_username)
        username_input.setMinimumWidth(120)
        username_input.setMaximumWidth(150)  # Limit width
        
        if default_username:
            username_input.setToolTip("Username auto-filled from file name.")
            username_input.setStyleSheet(style.USERNAME_INPUT_SUCCESS_STYLE)
        else:
            username_input.setToolTip("Please enter a username.")
            username_input.setStyleSheet(style.USERNAME_INPUT_ERROR_STYLE)
        layout.addWidget(username_input)
        
        # Add stretch to fill space (but not a spacer widget)
        layout.addStretch()
        
        return widget

    def extract_username_from_filename(self, filename: str) -> str:
        """
        Extract the username from the filename based on known variations.
        
        Args:
            filename (str): Filename to extract username from
            
        Returns:
            str: The standardized username or an empty string if no match is found
        """
        # Normalize filename to lowercase for case-insensitive matching
        normalized_filename = filename.lower()
        
        # Iterate through all variations to find a match
        for variation, standard in self.username_map.items():
            if variation in normalized_filename:
                # Return the standardized username
                return standard
        return ""

    def update_generate_button_state(self):
        """Enable the Generate button only if all usernames are filled."""
        if not self.loaded_files:
            self.generate_button.setEnabled(False)
            return
        
        for _, username_widget in self.loaded_files:
            if not username_widget.text().strip():
                self.generate_button.setEnabled(False)
                self.status_label.setText("Enter all usernames to generate the report")
                return
                
        self.generate_button.setEnabled(True)
        self.status_label.setText("Ready to generate report")

    def resize_image(self, img_str: str, max_size=(100, 100)) -> str:
        """
        Resize base64-encoded images to optimize performance.
        
        Args:
            img_str (str): Base64-encoded image string
            max_size (tuple): Maximum width and height
            
        Returns:
            str: Resized base64-encoded image string
        """
        try:
            img_data = base64.b64decode(img_str)
            image = Image.open(BytesIO(img_data))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Image processing error: {e}")
            return img_str  # Return original if there's an error

    def load_and_combine_data(self) -> Optional[pd.DataFrame]:
        """
        Load and combine data from all selected JSON files.
        
        Returns:
            DataFrame or None: Combined data from all files, or None if there was an error
        """
        if not self.loaded_files:
            self.show_warning("No Data", "Please load JSON data first.")
            return None
            
        combined_data = []
        
        for file_path, username_widget in self.loaded_files:
            username = username_widget.text().strip()
            if not username:
                self.show_warning("Input Required", 
                               f"Username required for '{os.path.basename(file_path)}'.")
                return None
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for album in data:
                            album['username'] = username
                        combined_data.extend(data)
                    else:
                        raise ValueError(f"Invalid JSON format in {file_path}. Expected a list.")
            except Exception as e:
                self.show_error("Data Loading Error", f"Error loading {file_path}: {e}")
                return None
                
        if not combined_data:
            self.show_warning("No Data Loaded", "No valid data was loaded from the JSON files.")
            return None
            
        return pd.DataFrame(combined_data)

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess and clean the data.
        
        Args:
            df (DataFrame): Raw combined data
            
        Returns:
            DataFrame: Processed data ready for visualization
        """
        # Remove 'rating' and 'comments' if present
        if 'rating' in df.columns:
            df.drop(columns=['rating'], inplace=True)
        if 'comments' in df.columns:
            df.drop(columns=['comments'], inplace=True)

        # Convert columns
        df['release_date'] = pd.to_datetime(df['release_date'], format='%d-%m-%Y', errors='coerce')
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        df['rank'] = df['rank'].astype(pd.Int64Dtype())
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
        df['points'] = df['points'].astype(pd.Int64Dtype())

        # Resize images
        if 'cover_image' in df.columns:
            df['cover_image'] = df['cover_image'].apply(self.resize_image)

        # Aggregate points
        points_agg = df.groupby('album')['points'].sum().reset_index().rename(columns={'points': 'total_points'})
        df_agg = df.merge(points_agg, on='album', how='left')

        # Unique album rows
        df_unique = df_agg.drop_duplicates(subset=['album'])

        # Contributors
        contributors = df.groupby('album')[['username', 'rank']].apply(
            lambda x: "; ".join(f"{u} ({r})" for u, r in zip(x['username'], x['rank']) if pd.notnull(r))
        ).reset_index(name='contributors')
        df_unique = df_unique.merge(contributors, on='album', how='left')
        df_unique.sort_values(by='total_points', ascending=False, inplace=True)

        # Date columns
        df_unique['year'] = df_unique['release_date'].dt.year
        df_unique['month'] = df_unique['release_date'].dt.month

        # Add row numbers
        df_unique.reset_index(drop=True, inplace=True)
        df_unique["row_number"] = df_unique.index + 1
        
        return df_unique

    def validate_year(self, df: pd.DataFrame) -> Optional[int]:
        """
        Validate that all entries have the same year.
        
        Args:
            df (DataFrame): Processed data
            
        Returns:
            int or None: The common year if valid, None otherwise
        """
        unique_years = df['year'].dropna().unique()
        
        if len(unique_years) > 1:
            self.show_warning("Year Mismatch", f"Multiple years found: {unique_years}.")
            return None
        elif len(unique_years) == 1:
            return int(unique_years[0])
        else:
            self.show_warning("No Valid Year", "No valid release dates found.")
            return None

    def calculate_statistics(self, df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Calculate basic statistics from the data.
        
        Args:
            df (DataFrame): Processed data
            
        Returns:
            Tuple[dict, DataFrame]: Dictionary of statistics and genre counts DataFrame
        """
        # Basic stats
        stats = {
            'total_albums': len(df),
            'unique_artists': df['artist'].nunique(),
            'countries': df['country'].nunique(),
            'unique_users': df['username'].nunique()
        }
        
        # Genre counts
        genre_counts = pd.concat([df['genre_1'], df['genre_2']]).value_counts().reset_index()
        genre_counts.columns = ['genre', 'count']
        stats['unique_genres'] = genre_counts['genre'].nunique()
        
        # Calculate top country (instead of top artist)
        country_counts = df['country'].value_counts()
        stats['top_country'] = country_counts.index[0] if not country_counts.empty else "N/A"
        
        # Calculate average points
        stats['avg_points'] = round(df['total_points'].mean(), 1) if len(df) > 0 else 0
        
        # Calculate top genre
        stats['top_genre'] = genre_counts.iloc[0]['genre'] if not genre_counts.empty else "N/A"
        
        return stats, genre_counts

    def create_genre_treemap(self, genre_counts: pd.DataFrame) -> str:
        """Create a treemap visualization of genre distribution."""
        fig = px.treemap(
            genre_counts,
            path=['genre'],
            values='count',
            labels={'genre': 'Genre', 'count': 'Count'}
        )
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, title=None)
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_country_choropleth(self, df: pd.DataFrame) -> str:
        """Create a choropleth map of albums by country with improved readability."""
        country_agg = df.groupby('country').agg(
            num_albums=('album', 'count'),
            total_points=('total_points', 'sum')
        ).reset_index()
        
        fig = px.choropleth(
            country_agg,
            locations="country",
            locationmode='country names',
            color="num_albums",
            hover_name="country",
            projection="natural earth",
            labels={'num_albums': 'Number of Albums'},
            color_continuous_scale="Viridis"  # Better color scale for dark theme
        )
        fig.update_traces(
            customdata=country_agg[['total_points']],
            hovertemplate="<b>%{location}</b><br>Albums: %{z}<br>Points: %{customdata[0]}<extra></extra>",
            marker_line_width=0.8,
            marker_line_color="white"
        )
        fig.update_layout(
            title={
                'text': 'Geographic Distribution of Albums',
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'color': '#1DB954', 'size': 18}
            },
            margin=dict(t=50, l=0, r=0, b=0),
            coloraxis_colorbar=dict(
                title="Number of Albums",
                tickfont=dict(color="#b3b3b3"),
                titlefont=dict(color="#b3b3b3")
            ),
            geo=dict(
                showframe=False, 
                showcoastlines=True, 
                coastlinecolor="LightGrey", 
                projection_scale=0.95,
                bgcolor='rgba(30, 30, 30, 0)'
            ),
            paper_bgcolor='rgba(30, 30, 30, 0)',
            plot_bgcolor='rgba(30, 30, 30, 0)',
            font=dict(color="#b3b3b3")
        )
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_release_timeline(self, df: pd.DataFrame) -> str:
        """Create a timeline of album releases throughout the year."""
        monthly_counts = df.groupby('month').size().reset_index(name='count')
        monthly_counts['month_name'] = monthly_counts['month'].apply(lambda m: pd.Timestamp(f"2023-{m}-01").strftime('%B'))
        monthly_counts = monthly_counts.sort_values('month')
        
        fig = px.bar(
            monthly_counts,
            x='month_name', 
            y='count',
            labels={'month_name': 'Month', 'count': 'Number of Albums'},
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            title={
                'text': 'Album Releases by Month',
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'color': '#1DB954', 'size': 18}
            },
            margin=dict(t=50, l=50, r=50, b=50),
            paper_bgcolor='rgba(30, 30, 30, 0)',
            plot_bgcolor='rgba(30, 30, 30, 0)',
            font=dict(color="#b3b3b3"),
            xaxis=dict(title_font=dict(color="#b3b3b3"), tickfont=dict(color="#b3b3b3")),
            yaxis=dict(title_font=dict(color="#b3b3b3"), tickfont=dict(color="#b3b3b3"))
        )
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_user_agreement_chart(self, df: pd.DataFrame) -> str:
        """Create a chart showing albums ranked by multiple users (consensus picks)."""
        # Parse the contributors column to count users
        def count_users(contributors_str):
            if not isinstance(contributors_str, str):
                return 0
            # Split by semicolon to get individual contributors
            return len(contributors_str.split(';'))
        
        # Apply the counting function to each album's contributors
        df['user_count'] = df['contributors'].apply(count_users)
        
        # Filter for albums with multiple users
        consensus_albums = df[df['user_count'] > 1].copy()
        
        if consensus_albums.empty:
            return "<div class='text-center text-light p-5'>No albums selected by multiple users</div>"
        
        # Sort by user count and get top 10
        consensus_albums = consensus_albums.sort_values(by=['user_count'], ascending=[False]).head(10)
        
        # Create display name
        consensus_albums['album_artist'] = consensus_albums['artist'] + ' - ' + consensus_albums['album']
        
        # For longer names, truncate with ellipsis
        max_length = 40
        consensus_albums['display_name'] = consensus_albums['album_artist'].apply(
            lambda x: x if len(x) <= max_length else x[:max_length-3] + '...'
        )
        
        fig = px.bar(
            consensus_albums,
            y='display_name', 
            x='user_count',
            labels={'display_name': 'Album', 'user_count': 'Number of Users'},
            color='user_count',
            color_continuous_scale='Viridis',
            orientation='h',
            text='user_count'
        )
        
        fig.update_traces(
            textposition='outside',
            textfont=dict(color="#b3b3b3")
        )
        
        fig.update_layout(
            title={
                'text': 'Most Agreed Upon Albums',
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'color': '#1DB954', 'size': 18}
            },
            margin=dict(t=50, l=200, r=50, b=50),
            paper_bgcolor='rgba(30, 30, 30, 0)',
            plot_bgcolor='rgba(30, 30, 30, 0)',
            font=dict(color="#b3b3b3"),
            xaxis=dict(
                title_font=dict(color="#b3b3b3"), 
                tickfont=dict(color="#b3b3b3"),
                range=[0, max(consensus_albums['user_count']) + 0.5]  # Add some padding
            ),
            yaxis=dict(
                title_font=dict(color="#b3b3b3"), 
                tickfont=dict(color="#b3b3b3"),
                autorange="reversed"  # Top albums at the top
            ),
            coloraxis_showscale=False
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_user_compatibility_table(self, df: pd.DataFrame) -> str:
        """
        Create a more sophisticated compatibility table showing musical taste compatibility between users.
        Analyzes genre preferences, genre avoidances, ranking-weighted genres, and artist overlap.
        
        Args:
            df (DataFrame): Processed data
                
        Returns:
            str: HTML representation of the compatibility table
        """
        import math
        
        # Define placeholder genres to be excluded from all calculations
        PLACEHOLDER_GENRES = {"Genre 1", "Genre 2"}
        
        # Extract user information and genres from the contributors field
        def extract_users_and_genres(row):
            if not isinstance(row['contributors'], str):
                return [], []
            
            genres = []
            # Only add valid, non-placeholder genres
            if pd.notna(row['genre_1']) and row['genre_1'] not in PLACEHOLDER_GENRES:
                genres.append(row['genre_1'])
            if pd.notna(row['genre_2']) and row['genre_2'] not in PLACEHOLDER_GENRES:
                genres.append(row['genre_2'])
            
            # Extract user names and ranks from contributor string (format: "User1 (rank); User2 (rank)")
            user_ranks = []
            for part in row['contributors'].split(';'):
                parts = part.split(' (')
                if len(parts) == 2:
                    user = parts[0].strip()
                    rank_str = parts[1].replace(')', '').strip()
                    try:
                        rank = int(rank_str)
                        user_ranks.append((user, rank))
                    except ValueError:
                        # Skip if rank cannot be parsed as integer
                        continue
            
            # Create user-genre-rank pairs and user-artist pairs
            genre_tuples = []
            artist_tuples = []
            for user, rank in user_ranks:
                for genre in genres:
                    # Include rank information for weighting
                    genre_tuples.append((user, genre, rank))
                # Add user-artist association
                artist_tuples.append((user, row['artist']))
                
            return genre_tuples, artist_tuples
        
        # Collect all user-genre-rank pairs and user-artist pairs
        user_genre_pairs = []
        user_artist_pairs = []
        for _, row in df.iterrows():
            genres, artists = extract_users_and_genres(row)
            user_genre_pairs.extend(genres)
            user_artist_pairs.extend(artists)
        
        # Convert to DataFrame and handle empty data case
        if not user_genre_pairs:
            return "<div class='text-center text-light p-5'>Not enough genre data available to analyze user compatibility</div>"
        
        # Create DataFrame from collected pairs
        genre_df = pd.DataFrame(user_genre_pairs, columns=['user', 'genre', 'rank'])
        artist_df = pd.DataFrame(user_artist_pairs, columns=['user', 'artist'])
        
        # 1. RANKING-WEIGHTED GENRES
        # Convert rank to weight (lower rank = higher weight)
        max_rank = genre_df['rank'].max()
        genre_df['weight'] = (max_rank - genre_df['rank'] + 1) / max_rank
        
        # Aggregate weighted genre counts
        genre_pivot = genre_df.groupby(['user', 'genre']).agg(
            count=('genre', 'size'),
            weighted_count=('weight', 'sum')
        ).reset_index()
        
        # Calculate user totals for weighted and unweighted counts
        user_totals = genre_pivot.groupby('user').agg(
            total=('count', 'sum'),
            weighted_total=('weighted_count', 'sum')
        ).reset_index()
        
        # Merge totals with pivot data
        genre_pivot = genre_pivot.merge(user_totals, on='user')
        
        # Calculate weighted and unweighted percentages
        genre_pivot['percentage'] = (genre_pivot['count'] / genre_pivot['total'] * 100).round(1)
        genre_pivot['weighted_percentage'] = (genre_pivot['weighted_count'] / genre_pivot['weighted_total'] * 100).round(1)
        
        # 2. GENRE ABSENCE ANALYSIS
        # Get the complete set of all valid genres used by at least one user
        all_genres = pd.concat([df['genre_1'].dropna(), df['genre_2'].dropna()])
        # Filter out placeholder genres
        all_genres = all_genres[~all_genres.isin(PLACEHOLDER_GENRES)]
        all_available_genres = set(all_genres.unique())
        print(f"Total available genres: {len(all_available_genres)}")
        
        # Exclude extremely rare genres (optional) - those appearing in only 1 album
        genre_counts = all_genres.value_counts()
        valid_genres = set(genre_counts[genre_counts > 1].index)  # Must appear in at least 2 albums
        
        print(f"Filtering out single-occurrence genres. Valid genres: {len(valid_genres)}")
        
        # Get all unique users
        all_users = genre_pivot['user'].unique()
        
        # For each user, collect which genres they use
        user_genres = {}
        for user in all_users:
            # Get all genres this user has selected
            user_genres[user] = set(genre_pivot[genre_pivot['user'] == user]['genre'].unique())
        
        # For each user, determine which genres they avoid from the valid set
        user_avoids = {}
        for user in all_users:
            # A genre is "avoided" if it appears in the valid set but the user doesn't use it
            avoided = valid_genres - user_genres[user]
            user_avoids[user] = avoided
            
        # Debug output to verify
        print(f"Valid genres users could choose: {', '.join(sorted(valid_genres))}")
        for user in all_users:
            avoided_str = ', '.join(sorted(user_avoids[user])) if user_avoids[user] else "none"
            print(f"User {user} avoids {len(user_avoids[user])}/{len(valid_genres)} genres: {avoided_str}")
        
        # 3. ARTIST OVERLAP MEASUREMENT
        # Get unique artists per user
        artist_counts = artist_df.groupby(['user', 'artist']).size().reset_index(name='count')
        
        # Create user-artist mapping for calculating artist overlap
        user_artists = {user: set(artist_counts[artist_counts['user'] == user]['artist']) for user in all_users}
        
        # Create pivot tables for genre preferences (regular and weighted)
        genre_pivot_table = genre_pivot.pivot_table(
            values='percentage', 
            index='user', 
            columns='genre', 
            fill_value=0
        )
        
        weighted_pivot_table = genre_pivot.pivot_table(
            values='weighted_percentage', 
            index='user', 
            columns='genre', 
            fill_value=0
        )
        
        # Calculate user similarity scores with enhanced metrics
        user_pairs = []
        users = sorted(genre_pivot_table.index.tolist())  # Sort users for consistent order
        
        for i, user1 in enumerate(users):
            for j, user2 in enumerate(users):
                if i < j:  # Only count each pair once
                    # 1. Calculate regular genre similarity (cosine similarity)
                    u1_vector = genre_pivot_table.loc[user1].values
                    u2_vector = genre_pivot_table.loc[user2].values
                    
                    dot_product = sum(a * b for a, b in zip(u1_vector, u2_vector))
                    norm_u1 = math.sqrt(sum(a * a for a in u1_vector))
                    norm_u2 = math.sqrt(sum(b * b for b in u2_vector))
                    
                    genre_similarity = 0.0
                    if norm_u1 > 0 and norm_u2 > 0:
                        genre_similarity = dot_product / (norm_u1 * norm_u2)
                    
                    # 2. Calculate ranking-weighted genre similarity
                    u1_weighted = weighted_pivot_table.loc[user1].values
                    u2_weighted = weighted_pivot_table.loc[user2].values
                    
                    weighted_dot = sum(a * b for a, b in zip(u1_weighted, u2_weighted))
                    weighted_norm_u1 = math.sqrt(sum(a * a for a in u1_weighted))
                    weighted_norm_u2 = math.sqrt(sum(b * b for b in u2_weighted))
                    
                    weighted_similarity = 0.0
                    if weighted_norm_u1 > 0 and weighted_norm_u2 > 0:
                        weighted_similarity = weighted_dot / (weighted_norm_u1 * weighted_norm_u2)
                    
                    # 3. Calculate genre absence similarity
                    u1_absences = user_avoids.get(user1, set())
                    u2_absences = user_avoids.get(user2, set())
                    
                    absence_similarity = 0.0
                    if valid_genres:  # If we have valid genres to potentially avoid
                        # Only calculate if both users avoid at least one genre
                        if len(u1_absences) > 0 and len(u2_absences) > 0:
                            # Jaccard similarity of avoided genres
                            absence_similarity = len(u1_absences.intersection(u2_absences)) / max(1, len(u1_absences.union(u2_absences)))
                    
                    # Print debug info for each pair to verify
                    shared = u1_absences.intersection(u2_absences)
                    union = u1_absences.union(u2_absences)
                    print(f"Users {user1} & {user2} avoidance similarity: {absence_similarity:.2f}")
                    print(f"  - User {user1} avoids {len(u1_absences)}/{len(valid_genres)} genres")
                    print(f"  - User {user2} avoids {len(u2_absences)}/{len(valid_genres)} genres")
                    print(f"  - Shared avoidances: {len(shared)}/{len(union)} = {absence_similarity:.2f}")
                    
                    # 4. Calculate artist overlap similarity
                    u1_artists = user_artists.get(user1, set())
                    u2_artists = user_artists.get(user2, set())
                    
                    artist_similarity = 0.0
                    if u1_artists or u2_artists:  # Check if either set is non-empty
                        # Jaccard similarity of artists
                        artist_similarity = len(u1_artists.intersection(u2_artists)) / max(1, len(u1_artists.union(u2_artists)))
                    
                    # Combined similarity score (weighted average)
                    # Adjust weights to reduce influence of absence similarity if it's generally low
                    if absence_similarity < 0.1 and artist_similarity > 0:
                        # If absence similarity is very low but artist similarity exists,
                        # shift more weight to other factors
                        combined_similarity = (
                            0.30 * genre_similarity + 
                            0.40 * weighted_similarity + 
                            0.05 * absence_similarity + 
                            0.25 * artist_similarity
                        )
                    else:
                        combined_similarity = (
                            0.25 * genre_similarity + 
                            0.35 * weighted_similarity + 
                            0.20 * absence_similarity + 
                            0.20 * artist_similarity
                        )
                    
                    # Identify shared avoided genres
                    shared_avoids = sorted(list(u1_absences.intersection(u2_absences)))
                    
                    # Create a unique display for each user pair with more variety
                    if not shared_avoids:
                        avoidance_display = "None"
                    else:
                        # Use the ASCII sum of both usernames as a pseudo-random seed
                        name_hash = sum(ord(c) for c in (user1 + user2))
                        
                        # Select different genres for each pair based on their name hash
                        if len(shared_avoids) > 2:
                            # Rotate the list based on name hash to show different genres for different pairs
                            rotated_index = name_hash % len(shared_avoids)
                            rotated_avoids = shared_avoids[rotated_index:] + shared_avoids[:rotated_index]
                            avoidance_display = f"{rotated_avoids[0]}, {rotated_avoids[1]} (+ {len(shared_avoids)-2} more)"
                        elif len(shared_avoids) == 2:
                            avoidance_display = f"{shared_avoids[0]}, {shared_avoids[1]}"
                        elif len(shared_avoids) == 1:
                            avoidance_display = shared_avoids[0]
                        
                        # Add the total count for more information
                        avoidance_display += f" [Total: {len(shared_avoids)}]"
                    
                    # Print detailed debug information
                    print(f"  - Full list of shared avoidances ({len(shared_avoids)} total): {', '.join(shared_avoids) if shared_avoids else 'None'}")
                    
                    # Count shared artists
                    shared_artists = u1_artists.intersection(u2_artists)
                    shared_artist_count = len(shared_artists)
                    
                    # Store comprehensive similarity data with full avoidance data
                    # This ensures each pair preserves their unique avoidance information
                    user_pairs.append((
                        user1, user2, 
                        combined_similarity, 
                        genre_similarity,
                        weighted_similarity,
                        absence_similarity,
                        artist_similarity,
                        shared_avoids,  # Store the actual list of shared avoided genres
                        shared_artist_count
                    ))
        
        # Sort by combined similarity score (highest first), then alphabetically for consistency
        user_pairs.sort(key=lambda x: (-x[2], x[0], x[1]))
        
        # Create an HTML table with the enhanced compatibility information
        html = """
        <div class="section-frame mt-4 mb-4">
            <div class="table-responsive">
                <table class="table table-dark table-striped table-bordered">
                    <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">User Pair</th>
                            <th scope="col">Compatibility</th>
                            <th scope="col">Similarity Breakdown</th>
                            <th scope="col">Shared Avoidances</th>
                            <th scope="col">Shared Artists</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add rows for each user pair
        for i, pair_data in enumerate(user_pairs):
            user1, user2, combined, genre_sim, weighted_sim, absence_sim, artist_sim, shared_avoids, artist_count = pair_data
            
            # Format the breakdown to show individual components
            breakdown = f"""
                <div><strong>Standard Genre:</strong> {genre_sim:.2f}</div>
                <div><strong>Rank-Weighted:</strong> {weighted_sim:.2f}</div>
                <div><strong>Genre Avoidance:</strong> {absence_sim:.2f}</div>
                <div><strong>Artist Overlap:</strong> {artist_sim:.2f}</div>
            """
            
            # Create the avoidance display string for THIS SPECIFIC pair
            avoidance_list = shared_avoids  # This is the actual list of shared avoided genres
            
            if not avoidance_list:
                avoidance_display = "None"
            elif len(avoidance_list) == 1:
                avoidance_display = avoidance_list[0]
            elif len(avoidance_list) == 2:
                avoidance_display = f"{avoidance_list[0]}, {avoidance_list[1]}"
            else:
                # Generate a unique selection for each pair by using a different starting point
                pos = i % len(avoidance_list)  # Use the pair's position in the result list
                selected = [avoidance_list[pos], avoidance_list[(pos+1) % len(avoidance_list)]]
                avoidance_display = f"{selected[0]}, {selected[1]} (+ {len(avoidance_list)-2} more)"
            
            # Always add the total count
            if avoidance_list:
                avoidance_display += f" [Total: {len(avoidance_list)}]"
                
            html += f"""
            <tr>
                <td>{i+1}</td>
                <td><strong>{user1} & {user2}</strong></td>
                <td><strong>{combined:.2f}</strong></td>
                <td>{breakdown}</td>
                <td>{avoidance_display}</td>
                <td>{artist_count}</td>
            </tr>
            """
        
        # Close the HTML table
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html

    def create_country_genre_chart(self, df: pd.DataFrame) -> str:
        """Create a heatmap showing the relationship between countries and genres."""
        # Configurable limits - easily adjustable
        MAX_COUNTRIES = 10  # Maximum number of countries to display
        MAX_GENRES = 15     # Maximum number of genres to display
        
        # Combine genre columns and expand the dataframe
        g1 = df[['country', 'genre_1']].rename(columns={'genre_1': 'genre'})
        g2 = df[['country', 'genre_2']].rename(columns={'genre_2': 'genre'})
        genre_df = pd.concat([g1, g2])
        genre_df = genre_df.dropna()
        
        # Create a pivot table for the heatmap
        country_genre = genre_df.groupby(['country', 'genre']).size().reset_index(name='count')
        pivot_data = country_genre.pivot_table(
            values='count', 
            index='country', 
            columns='genre', 
            fill_value=0
        )
        
        # Sort countries and genres by total counts (most significant first)
        total_by_country = pivot_data.sum(axis=1).sort_values(ascending=False)
        total_by_genre = pivot_data.sum(axis=0).sort_values(ascending=False)
        
        # Apply limits if needed
        if len(total_by_country) > MAX_COUNTRIES or len(total_by_genre) > MAX_GENRES:
            # Get top countries and genres based on configured limits
            top_countries = total_by_country.head(MAX_COUNTRIES).index
            top_genres = total_by_genre.head(MAX_GENRES).index
            
            # Filter the pivot table to include only top countries and genres
            pivot_data = pivot_data.loc[pivot_data.index.isin(top_countries), pivot_data.columns.isin(top_genres)]
            
            # Re-sort the filtered data
            total_by_country = total_by_country[total_by_country.index.isin(top_countries)]
            total_by_genre = total_by_genre[total_by_genre.index.isin(top_genres)]
        
        # Reindex data for better display (sorts countries and genres by frequency)
        pivot_data = pivot_data.reindex(index=total_by_country.index, columns=total_by_genre.index)
        
        # Calculate dynamic height based on number of countries
        height = max(450, 100 + len(pivot_data) * 40)  # Base height + extra for each country
        
        # Create the heatmap figure with width set to fill container
        fig = px.imshow(
            pivot_data,
            labels=dict(x="Genre", y="Country", color="Album Count"),
            color_continuous_scale="Viridis",
            aspect="auto",
            height=height
        )
        
        # Configure layout for better readability and to fill container
        fig.update_layout(
            title={
                'text': 'Genre Distribution by Country',
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'color': '#1DB954', 'size': 18}
            },
            margin=dict(t=50, l=120, r=50, b=100),
            paper_bgcolor='rgba(30, 30, 30, 0)',
            plot_bgcolor='rgba(30, 30, 30, 0)',
            font=dict(color="#b3b3b3"),
            yaxis=dict(
                side="left",
                automargin=True,
                title=dict(standoff=15),
                fixedrange=True
            ),
            xaxis=dict(
                tickangle=45,
                automargin=True,
                fixedrange=True
            ),
            autosize=False,
            width=None,
        )
        
        # Improve appearance
        fig.update_traces(
            xgap=2,
            ygap=2,
            colorbar=dict(
                thickness=20,
                title=dict(text="Album Count", font=dict(color="#b3b3b3")),
                tickfont=dict(color="#b3b3b3"),
                len=0.8  # Make colorbar slightly shorter
            )
        )
        
        # Generate HTML with specific config to prevent resize issues
        html = fig.to_html(
            full_html=False, 
            include_plotlyjs=False, 
            config={
                "displayModeBar": False,
                "responsive": True,
                "staticPlot": False,   # Disable interactivity to prevent resize issues
                "doubleClick": False,  # Disable double-click actions
            }
        )
        
        # Add custom JavaScript to force proper sizing
        extra_js = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                // Find this specific chart's container
                var containers = document.querySelectorAll('.js-plotly-plot');
                containers.forEach(function(container) {
                    // Force the chart to use full width
                    if (container.style.width) {
                        container.style.width = '100%';
                    }
                    // Force SVG to use full width
                    var svg = container.querySelector('svg');
                    if (svg) {
                        svg.setAttribute('width', '100%');
                        svg.style.width = '100%';
                    }
                });
            }, 100);
        });
        </script>
        """
        
        return html + extra_js

    def create_user_genre_diversity(self, df: pd.DataFrame) -> str:
        """Create a chart showing genre diversity by user."""
        # Count unique genres per user
        g1 = df[['username', 'genre_1']].rename(columns={'genre_1': 'genre'})
        g2 = df[['username', 'genre_2']].rename(columns={'genre_2': 'genre'})
        all_genres = pd.concat([g1, g2])
        all_genres = all_genres.dropna()
        
        # Count unique genres per user
        user_diversity = all_genres.groupby('username')['genre'].nunique().reset_index()
        user_diversity.columns = ['username', 'genre_diversity']
        user_diversity = user_diversity.sort_values('genre_diversity', ascending=False)
        
        fig = px.bar(
            user_diversity,
            x='username',
            y='genre_diversity',
            labels={'username': 'User', 'genre_diversity': 'Number of Unique Genres'},
            color='genre_diversity',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            title={
                'text': 'Genre Diversity by User',
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'color': '#1DB954', 'size': 18}
            },
            margin=dict(t=50, l=50, r=50, b=50),
            paper_bgcolor='rgba(30, 30, 30, 0)',
            plot_bgcolor='rgba(30, 30, 30, 0)',
            font=dict(color="#b3b3b3"),
            xaxis=dict(title_font=dict(color="#b3b3b3"), tickfont=dict(color="#b3b3b3")),
            yaxis=dict(title_font=dict(color="#b3b3b3"), tickfont=dict(color="#b3b3b3"))
        )
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_genre_bar_chart(self, genre_counts: pd.DataFrame) -> str:
        """Create a bar chart of genre counts."""
        fig = px.bar(
            genre_counts,
            x='genre',
            y='count',
            labels={'genre': 'Genre', 'count': 'Count'},
            color='count',
            color_continuous_scale='Sunset'
        )
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, showlegend=False)
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_user_album_counts(self, df: pd.DataFrame) -> str:
        """Create a bar chart of user album counts."""
        user_album_counts = df.groupby('username')['album'].nunique().reset_index(name='album_count')
        fig = px.bar(
            user_album_counts,
            x='username',
            y='album_count',
            labels={'album_count': 'Album Count', 'username': 'User'},
            color='album_count',
            color_continuous_scale='Portland'
        )
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, showlegend=False)
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    def create_charts(self, df: pd.DataFrame, genre_counts: pd.DataFrame) -> Dict[str, str]:
        """
        Create all chart visualizations.
        
        Args:
            df (DataFrame): Processed data
            genre_counts (DataFrame): Genre count data
            
        Returns:
            dict: Dictionary of chart HTML
        """
        self.status_label.setText("Creating visualizations...")
        
        charts = {
            # Keep only charts that are used in the template
            'treemap_graph': self.create_genre_treemap(genre_counts),
            'map_graph': self.create_country_choropleth(df),
            'genre_graph': self.create_genre_bar_chart(genre_counts),
            'user_counts_graph': self.create_user_album_counts(df),
            
            # Remove unused charts
            # 'user_genre_graph': self.create_user_genre_chart(df),
            # 'genre_trend_graph': self.create_genre_trend_chart(df),
            
            # New charts
            'release_timeline_graph': self.create_release_timeline(df),
            'user_agreement_graph': self.create_user_agreement_chart(df),
            'country_genre_graph': self.create_country_genre_chart(df),
            'user_genre_diversity_graph': self.create_user_genre_diversity(df),
            'musical_compatibility_graph': self.create_user_compatibility_table(df)
        }
        return charts

    def generate_and_save_html(self, charts: Dict[str, str], stats: Dict[str, Any], 
                            df: pd.DataFrame, current_year: int) -> bool:
        """
        Generate and save the HTML report.
        
        Args:
            charts (dict): Dictionary of chart HTML
            stats (dict): Dictionary of statistics
            df (DataFrame): Processed data
            current_year (int): The year of the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.status_label.setText("Generating HTML report...")
            
            # Prepare for template
            albums = df.to_dict(orient='records')

            template_path = resource_path('template.html')
            env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
            template = env.get_template(os.path.basename(template_path))

            html_content = template.render(
                **charts,
                albums=albums,
                total_albums=stats['total_albums'],
                unique_artists=stats['unique_artists'],
                unique_genres=stats['unique_genres'],
                countries=stats['countries'],
                unique_users=stats['unique_users'],
                current_year=current_year,
                top_country=stats['top_country'],
                avg_points=stats['avg_points'],
                top_genre=stats['top_genre']
            )

            # Save and open
            desktop_path = Path.home() / "Desktop"
            output_path = desktop_path / "album_report.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            webbrowser.open(f'file://{output_path}')
            self.status_label.setText("Report generated successfully!")
            # REMOVE THIS LINE:
            # self.show_info("Success", "HTML report generated and opened.")
            return True
        except Exception as e:
            self.status_label.setText("Error generating report!")
            self.show_error("HTML Generation Error", f"Failed to generate HTML: {e}")
            return False

    def generate_html(self):
        """
        Generate HTML report with visualizations from the loaded data.
        This is the main workflow method that coordinates the report generation process.
        """
        try:
            self.status_label.setText("Processing data...")
            
            # Step 1: Load and combine data
            df = self.load_and_combine_data()
            if df is None:
                return
                
            # Step 2: Preprocess data
            df_processed = self.preprocess_data(df)
            
            # Step 3: Validate year
            current_year = self.validate_year(df_processed)
            if current_year is None:
                return
            
            # Filter to the current year
            df_processed = df_processed[df_processed['year'] == current_year]
                
            # Step 4: Calculate statistics
            stats, genre_counts = self.calculate_statistics(df_processed)
            
            # Step 5: Create visualizations
            charts = self.create_charts(df_processed, genre_counts)
            
            # Step 6: Generate and save the HTML report
            self.generate_and_save_html(charts, stats, df_processed, current_year)
            
        except Exception as e:
            self.status_label.setText("Error!")
            self.show_error("Error", f"An unexpected error occurred:\n{e}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set app ID for Windows taskbar icon
    if platform.system() == 'Windows':
        try:
            import ctypes
            # Use a consistent unique ID based on your app information
            app_id = f'SuSheProcessor.App.Version.{open(resource_path("version.txt")).read().strip()}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception as e:
            print(f"Warning: Could not set application ID for taskbar icon: {e}")
    
    # Set application icon globally (affects both window and taskbar)
    try:
        icon_path = resource_path("logos/sushe_processor.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            app.setWindowIcon(app_icon)
        else:
            print(f"Warning: Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Warning: Could not set application icon: {e}")
    
    # Try to load Spotify-like fonts if available
    try:
        # Try to load Gotham font if available (.otf version)
        id = QFontDatabase.addApplicationFont(resource_path("fonts/Gotham-Medium.otf"))
        if id < 0:  # Try alternative font files
            font_paths = [
                "fonts/Gotham.otf",
                "fonts/Gotham-Book.otf",
                "fonts/Gotham-Bold.otf"
            ]
            
            for font_path in font_paths:
                id = QFontDatabase.addApplicationFont(resource_path(font_path))
                if id >= 0:
                    print(f"Loaded font from {font_path}")
                    break
            
            if id < 0:
                print("Gotham font not available, using system default")
    except Exception as e:
        print(f"Error loading font: {e}")
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())