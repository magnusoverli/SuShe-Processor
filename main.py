import sys
import os
import json
import sys
import pandas as pd
import plotly.express as px
import plotly.colors as pc
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QFileDialog, QMessageBox, QLineEdit, QLabel, QScrollArea, QFrame, QStyle, QSizePolicy
)
from PyQt6.QtCore import Qt
from jinja2 import Environment, FileSystemLoader
import webbrowser
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores its path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Album Presentation App")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize data structures
        self.loaded_files = []  # List to store tuples of (file_path, username_widget)
        self.username_map = {}  # Dictionary to map variations to standard usernames
        
        # Load username mappings
        self.load_username_mappings()
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Load JSON Button
        self.load_button = QPushButton("Load JSON Data")
        self.load_button.clicked.connect(self.load_json)
        main_layout.addWidget(self.load_button)
        
        # Scroll Area for loaded files
        self.files_scroll_area = QScrollArea()
        self.files_scroll_area.setWidgetResizable(True)
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout()
        self.files_container.setLayout(self.files_layout)
        self.files_scroll_area.setWidget(self.files_container)
        main_layout.addWidget(self.files_scroll_area)
        
        # Generate HTML Button
        self.generate_button = QPushButton("Generate HTML Report")
        self.generate_button.clicked.connect(self.generate_html)
        self.generate_button.setEnabled(False)
        main_layout.addWidget(self.generate_button)
        
        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        main_layout.addWidget(self.exit_button)
        
        # Set main layout to central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_username_mappings(self, mapping_file='username_mappings.json'):
        """
        Load username mappings from a JSON file.
        Each mapping contains a standardized username and its possible variations.
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
            QMessageBox.critical(self, "Mapping File Not Found",
                                f"The mapping file '{mapping_file}' was not found.")
            self.username_map = {}
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid Mapping File",
                                f"Failed to parse '{mapping_file}':\n{e}")
            self.username_map = {}

    def load_json(self):
        """Load multiple JSON files and display them with username input fields."""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Open JSON Files", "", "JSON Files (*.json)"
        )
        if file_paths:
            for path in file_paths:
                if any(f[0] == path for f in self.loaded_files):
                    QMessageBox.warning(self, "Duplicate File", f"'{os.path.basename(path)}' is already loaded.")
                    continue
                try:
                    # Attempt to load JSON to validate
                    with open(path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except Exception as e:
                    QMessageBox.critical(self, "Invalid JSON", f"Failed to load '{os.path.basename(path)}':\n{e}")
                    continue
                
                # Extract username from file name based on the mapping
                username = self.extract_username_from_filename(os.path.basename(path))
                
                # Create file entry widget with the extracted username
                file_widget = self.create_file_entry_widget(path, default_username=username)
                self.files_layout.addWidget(file_widget)
                
                # If username was not extracted, inform the user
                if not username:
                    QMessageBox.information(
                        self, 
                        "Username Not Found", 
                        f"No matching username found in the file name '{os.path.basename(path)}'. Please enter it manually."
                    )
                
                # Store the file path and username widget
                username_input = file_widget.findChild(QLineEdit)
                username_input.textChanged.connect(self.update_generate_button_state)
                self.loaded_files.append((path, username_input))
            
            self.update_generate_button_state()

    def create_file_entry_widget(self, file_path, default_username=""):
        """Create a widget representing a loaded JSON file with an icon and username input."""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # File icon
        icon_label = QLabel()
        pixmap = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon).pixmap(24, 24)
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)
        
        # File name
        file_name = os.path.basename(file_path)
        name_label = QLabel(file_name)
        name_label.setFixedWidth(200)
        layout.addWidget(name_label)
        
        # Username input
        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter username")
        username_input.setText(default_username)  # Set the default username
        if default_username:
            username_input.setToolTip("Username auto-filled from file name.")
            username_input.setStyleSheet("background-color: #e6ffe6;")  # Light green background
        else:
            username_input.setToolTip("Please enter a username.")
            username_input.setStyleSheet("background-color: #ffe6e6;")  # Light red background
        layout.addWidget(username_input)
        
        # Spacer to push the separator to the end
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(spacer)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)
        
        return widget

    def extract_username_from_filename(self, filename):
        """
        Extract the username from the filename based on known variations.
        Returns the standardized username or an empty string if no match is found.
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
                return
        self.generate_button.setEnabled(True)

    def resize_image(self, img_str, max_size=(100, 100)):
        """Resize base64-encoded images to optimize performance."""
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

    def generate_html(self):
        """Generate HTML without rating-based stats, using album counts on the map, plus row numbers."""
        if not self.loaded_files:
            QMessageBox.warning(self, "No Data", "Please load JSON data first.")
            return

        try:
            combined_data = []
            for file_path, username_widget in self.loaded_files:
                username = username_widget.text().strip()
                if not username:
                    QMessageBox.warning(self, "Input Required", f"Username required for '{os.path.basename(file_path)}'.")
                    return
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for album in data:
                            album['username'] = username
                        combined_data.extend(data)
                    else:
                        raise ValueError(f"Invalid JSON format in {file_path}. Expected a list.")

            if not combined_data:
                QMessageBox.warning(self, "No Data Loaded", "No valid data was loaded from the JSON files.")
                return

            df = pd.DataFrame(combined_data)

            # Remove 'rating' and 'comments' if present
            if 'rating' in df.columns:
                df.drop(columns=['rating'], inplace=True)
            if 'comments' in df.columns:
                df.drop(columns=['comments'], inplace=True)

            # Convert columns
            df['release_date'] = pd.to_datetime(df['release_date'], format='%d-%m-%Y', errors='coerce')
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce').astype(pd.Int64Dtype())
            df['points'] = pd.to_numeric(df['points'], errors='coerce').astype(pd.Int64Dtype())

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

            # Basic stats
            total_albums = len(df_unique)
            unique_artists = df_unique['artist'].nunique()
            countries = df_unique['country'].nunique()
            unique_users = df_unique['username'].nunique()

            # Genre counts
            genre_counts = pd.concat([df['genre_1'], df['genre_2']]).value_counts().reset_index()
            genre_counts.columns = ['genre', 'count']
            unique_genres = genre_counts['genre'].nunique()

            # Ensure single year
            unique_years = df_unique['year'].dropna().unique()
            if len(unique_years) > 1:
                QMessageBox.warning(self, "Year Mismatch", f"Multiple years: {unique_years}.")
                return
            elif len(unique_years) == 1:
                current_year = unique_years[0]
                df_unique = df_unique[df_unique['year'] == current_year]
            else:
                QMessageBox.warning(self, "No Valid Year", "No valid release dates found.")
                return

            # Add row numbers
            df_unique.reset_index(drop=True, inplace=True)
            df_unique["row_number"] = df_unique.index + 1

            # =========== GRAPHS (Non-Rating) ===========

            # 2. Genre Distribution Treemap
            fig_treemap = px.treemap(
                genre_counts,
                path=['genre'],
                values='count',
                labels={'genre': 'Genre', 'count': 'Count'}
            )
            fig_treemap.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, title=None)
            treemap_graph = fig_treemap.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 3. Albums by Country Choropleth Map (uses album counts)
            country_agg = df_unique.groupby('country').agg(
                num_albums=('album', 'count'),
                total_points=('total_points', 'sum')
            ).reset_index()
            fig_map = px.choropleth(
                country_agg,
                locations="country",
                locationmode='country names',
                color="num_albums",
                hover_name="country",
                projection="natural earth",
                labels={'num_albums': 'Albums'}
            )
            fig_map.update_traces(
                customdata=country_agg[['total_points']],
                hovertemplate="<b>%{location}</b><br>Albums: %{z}<br>Points: %{customdata[0]}<extra></extra>",
                marker_line_width=0.8,
                marker_line_color="white"
            )
            fig_map.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),
                height=500,
                coloraxis_showscale=False,
                geo=dict(showframe=False, showcoastlines=True, coastlinecolor="LightGrey", projection_scale=0.95)
            )
            map_graph = fig_map.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 5. Genre Counts Bar Chart
            fig_genre = px.bar(
                genre_counts,
                x='genre',
                y='count',
                labels={'genre': 'Genre', 'count': 'Count'},
                color='count',
                color_continuous_scale='Sunset'
            )
            fig_genre.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, showlegend=False)
            genre_graph = fig_genre.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 8. User Album Counts
            user_album_counts = df.groupby('username')['album'].nunique().reset_index(name='album_count')
            fig_user_counts = px.bar(
                user_album_counts,
                x='username',
                y='album_count',
                labels={'album_count': 'Album Count', 'username': 'User'},
                color='album_count',
                color_continuous_scale='Portland'
            )
            fig_user_counts.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, showlegend=False)
            user_counts_graph = fig_user_counts.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 9. User Genre Distribution
            user_g1 = df[['username', 'genre_1']].rename(columns={'genre_1': 'genre'}).dropna()
            user_g2 = df[['username', 'genre_2']].rename(columns={'genre_2': 'genre'}).dropna()
            user_genre_counts = pd.concat([user_g1, user_g2], ignore_index=True)
            user_genre_counts = user_genre_counts.groupby(['username', 'genre']).size().reset_index(name='count')
            fig_user_genre = px.scatter(
                user_genre_counts,
                x='username',
                y='genre',
                size='count',
                color='genre',
                labels={'username': 'User', 'genre': 'Genre', 'count': 'Albums'},
                height=500
            )
            fig_user_genre.update_layout(margin=dict(t=0, l=0, r=0, b=0), showlegend=False)
            user_genre_graph = fig_user_genre.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 11. Genre Popularity Over Time
            genre_trend = df_unique.explode(['genre_1', 'genre_2'])
            genre_trend = genre_trend.melt(
                id_vars=['month'],
                value_vars=['genre_1', 'genre_2'],
                var_name='genre_type',
                value_name='genre'
            ).dropna(subset=['genre'])
            genre_trend_count = genre_trend.groupby(['month', 'genre']).size().reset_index(name='count')
            genre_trend_count['month_name'] = pd.to_datetime(genre_trend_count['month'], format='%m').dt.strftime('%B')
            genre_trend_count.sort_values('month', inplace=True)
            fig_genre_trend = px.scatter(
                genre_trend_count,
                x='month_name',
                y='count',
                color='genre',
                labels={'month_name': 'Month', 'count': 'Albums'},
                height=500
            )
            fig_genre_trend.update_layout(margin=dict(t=0, l=0, r=0, b=0), showlegend=False)
            genre_trend_graph = fig_genre_trend.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # 12. Top Artists by total_points
            top_artists = df_unique.groupby('artist')['total_points'].sum().reset_index().sort_values(
                by='total_points', ascending=False
            ).head(10)
            fig_top_artists = px.bar(
                top_artists,
                x='artist',
                y='total_points',
                labels={'artist': 'Artist', 'total_points': 'Total Points'},
                color='total_points',
                color_continuous_scale='YlGnBu'
            )
            fig_top_artists.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, showlegend=False)
            top_artists_graph = fig_top_artists.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

            # Prepare for template
            albums = df_unique.to_dict(orient='records')

            template_path = resource_path('template.html')
            env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
            template = env.get_template(os.path.basename(template_path))

            html_content = template.render(
                treemap_graph=treemap_graph,
                map_graph=map_graph,
                genre_graph=genre_graph,
                user_counts_graph=user_counts_graph,
                user_genre_graph=user_genre_graph,
                genre_trend_graph=genre_trend_graph,
                top_artists_graph=top_artists_graph,
                albums=albums,
                total_albums=total_albums,
                unique_artists=unique_artists,
                unique_genres=unique_genres,
                countries=countries,
                unique_users=unique_users,
                current_year=current_year
            )

            # Save and open
            desktop_path = Path.home() / "Desktop"
            output_path = desktop_path / "album_report.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            webbrowser.open(f'file://{output_path}')
            QMessageBox.information(self, "Success", "HTML report generated and opened.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")
            import traceback
            traceback.print_exc()



def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
