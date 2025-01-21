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
        """Process data and generate the interactive HTML report."""
        if not self.loaded_files:
            QMessageBox.warning(self, "No Data", "Please load JSON data first.")
            return

        try:
            combined_data = []
            for file_path, username_widget in self.loaded_files:
                username = username_widget.text().strip()
                if not username:
                    QMessageBox.warning(self, "Input Required", f"Username is required for '{os.path.basename(file_path)}'.")
                    return
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for album in data:
                            album['username'] = username
                        combined_data.extend(data)
                    else:
                        raise ValueError(f"Invalid JSON format in {file_path}. Expected a list of albums.")

            if not combined_data:
                QMessageBox.warning(self, "No Data Loaded", "No valid data was loaded from the JSON files.")
                return

            df = pd.DataFrame(combined_data)
            
            # Remove 'comments' column if present
            if 'comments' in df.columns:
                df.drop(columns=['comments'], inplace=True)

            # Convert types
            df['release_date'] = pd.to_datetime(df['release_date'], format='%d-%m-%Y', errors='coerce')
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce').astype(pd.Int64Dtype())
            df['points'] = pd.to_numeric(df['points'], errors='coerce').astype(pd.Int64Dtype())

            # Warnings if conversions fail
            if df['release_date'].isnull().any():
                QMessageBox.warning(self, "Data Warning", "Some release dates failed to parse and are set as NaT.")
            if df['rating'].isnull().any():
                QMessageBox.warning(self, "Data Warning", "Some ratings could not be converted and are set as NaN.")

            # Resize cover images if available
            if 'cover_image' in df.columns:
                df['cover_image'] = df['cover_image'].apply(self.resize_image)

            # Aggregate points & ratings
            points_agg = df.groupby('album')['points'].sum().reset_index().rename(columns={'points': 'total_points'})
            rating_agg = df.groupby('album')['rating'].mean().reset_index().rename(columns={'rating': 'avg_rating'})

            df_agg = df.merge(points_agg, on='album', how='left').merge(rating_agg, on='album', how='left')
            df_unique = df_agg.drop_duplicates(subset=['album'])

            # Contributors
            contributors = df.groupby('album')[['username', 'rank']].apply(
                lambda x: "; ".join([f"{u} ({r})" for u, r in zip(x['username'], x['rank']) if pd.notnull(r)])
            ).reset_index(name='contributors')
            df_unique = df_unique.merge(contributors, on='album', how='left')
            df_unique.sort_values(by='total_points', ascending=False, inplace=True)

            # Additional metrics
            artist_avg = df.groupby('artist')['rating'].mean().reset_index(name='avg_rating')
            genre_counts = pd.concat([df['genre_1'], df['genre_2']]).value_counts().reset_index()
            genre_counts.columns = ['genre', 'count']
            df_unique['year'] = df_unique['release_date'].dt.year
            df_unique['month'] = df_unique['release_date'].dt.month  # Extract month
            total_albums = len(df_unique)
            unique_artists = df_unique['artist'].nunique()
            unique_genres = genre_counts['genre'].nunique()
            countries = df_unique['country'].nunique()
            unique_users = df_unique['username'].nunique()

            # Ensure all albums belong to the same year
            unique_years = df_unique['year'].dropna().unique()
            if len(unique_years) > 1:
                QMessageBox.warning(
                    self, 
                    "Year Mismatch", 
                    f"Multiple years detected in the data: {unique_years}. Please ensure all albums belong to the same year."
                )
                return
            elif len(unique_years) == 1:
                report_year = unique_years[0]
                df_unique = df_unique[df_unique['year'] == report_year]
                current_year = report_year
            else:
                QMessageBox.warning(
                    self, 
                    "No Valid Year", 
                    "No valid release dates found in the data. Please check your JSON files."
                )
                return

            # 1. Album Ratings Bar Chart
            fig_bar = px.bar(
                df_unique,
                x='album',
                y='avg_rating',
                color='artist',
                labels={'avg_rating': 'Average Rating', 'album': 'Album'},
                hover_data=['artist']
            )
            fig_bar.update_traces(
                marker_line_width=0.5,  # Thinner bar outlines
                marker_line_color="black"  # Outlines for better contrast
            )
            fig_bar.update_layout(
                margin=dict(t=0, l=0, r=0, b=100),  # Removes title padding and trims other margins
                height=500,  # Consistent height
                xaxis=dict(
                    title=None,
                    tickangle=-45,  # Keeps x-axis labels angled
                    tickmode="linear"  # Ensures all labels are shown
                ),
                yaxis=dict(
                    title="Average Rating",
                    title_standoff=10  # Add some spacing between y-axis title and ticks
                ),
                showlegend=False,  # Removes the legend
                title=None  # Removes the title inside the container
            )
            bar_graph = fig_bar.to_html(full_html=False, include_plotlyjs=False, default_height="500px", config={
                "displayModeBar": False  # Disables the toolbar
            })

            # 2. Genre Distribution Treemap
            fig_treemap = px.treemap(
                genre_counts,
                path=['genre'],
                values='count',
                labels={'genre': 'Genre', 'count': 'Count'}
            )
            fig_treemap.update_traces(
                textinfo="label+value+percent entry",
                hovertemplate="<b>Genre:</b> %{label}<br><b>Count:</b> %{value}<br><b>Percentage:</b> %{percentEntry:.2%}<extra></extra>",
                tiling=dict(pad=0, squarifyratio=1)  # Optimizes spacing and squarification
            )
            fig_treemap.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Removes outer margins
                height=500,  # Consistent height with other graphs
                title=None  # Removes the title inside the graph container
            )
            treemap_graph = fig_treemap.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disables the toolbar
            })

            # 3. Albums by Country Choropleth Map
            country_agg = df_unique.groupby('country').agg(
                num_albums=('album', 'count'),
                avg_rating=('avg_rating', 'mean')
            ).reset_index()
            fig_map = px.choropleth(
                country_agg,
                locations="country",
                locationmode='country names',
                color="avg_rating",
                hover_name="country",
                projection="natural earth",
                labels={'avg_rating': 'Average Rating'}
            )
            fig_map.update_traces(
                customdata=country_agg[['num_albums']],  # Assign num_albums as customdata
                hovertemplate="<b>%{location}</b><br>Avg Rating: %{z:.2f}<br>Albums: %{customdata[0]}<extra></extra>",
                marker_line_width=0.8,
                marker_line_color="white"
            )
            fig_map.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Eliminates outer margins
                height=500,  # Consistent height with other graphs
                coloraxis_showscale=False,  # Hides the color bar
                geo=dict(
                    showframe=False,  # Removes map frame
                    showcoastlines=True,  # Adds coastlines for better context
                    coastlinecolor="LightGrey",  # Light grey coastlines
                    projection_scale=0.95,  # Adjust zoom (lower value zooms out)
                )
            )
            map_graph = fig_map.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disables the toolbar
            })

            # 4. Average Rating per Artist Bar Chart
            fig_avg = px.bar(
                artist_avg,
                x='artist',
                y='avg_rating',
                labels={'avg_rating': 'Average Rating', 'artist': 'Artist'},
                color='avg_rating',
                color_continuous_scale='Viridis'
            )
            fig_avg.update_traces(
                marker_line_width=0.5,  # Add thin bar outlines for clarity
                marker_line_color="black"  # Define outline color
            )
            fig_avg.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with the world map graph
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels for readability
                    tickmode="linear",  # Ensure all artist names are displayed
                    title=None  # Remove the x-axis title ("Artist")
                ),
                yaxis=dict(
                    title="Average Rating",
                    title_standoff=10  # Space between y-axis title and ticks
                ),
                showlegend=False,  # Remove the legend
                coloraxis_showscale=False  # Remove the color scale
            )
            avg_graph = fig_avg.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 5. Genre Counts Bar Chart
            fig_genre = px.bar(
                genre_counts,
                x='genre',
                y='count',
                labels={'count': 'Count', 'genre': 'Genre'},
                color='count',
                color_continuous_scale='Sunset'
            )
            fig_genre.update_traces(
                marker_line_width=0.5,  # Add thin bar outlines for clarity
                marker_line_color="black"  # Define outline color
            )
            fig_genre.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with other graphs
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels for readability
                    tickmode="linear",  # Ensure all labels are displayed
                    title=None  # Remove the x-axis title ("Genre")
                ),
                yaxis=dict(
                    title="Count",
                    title_standoff=10  # Add some spacing between y-axis title and ticks
                ),
                showlegend=False,  # Remove the legend
                coloraxis_showscale=False  # Remove the color scale
            )
            genre_graph = fig_genre.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 6. Ratings Over Time Line Chart
            fig_time = px.scatter(
                df_unique,
                x='release_date',
                y='avg_rating',
                color='artist',
                labels={'release_date': 'Release Date', 'avg_rating': 'Average Rating'},
                title=None,
                height=500  # Set consistent height with other graphs
            )
            fig_time.update_traces(
                marker=dict(size=8, line=dict(width=0.5, color='black'))  # Improve point visibility
            )
            fig_time.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                xaxis=dict(
                    title=None  # Remove x-axis title ("Release Date")
                ),
                yaxis=dict(
                    title="Average Rating",
                    title_standoff=10  # Add spacing between y-axis title and ticks
                ),
                showlegend=False  # Remove the legend
            )
            time_graph = fig_time.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 7. User Average Ratings Bar Chart
            user_avg = df.groupby('username')['rating'].mean().reset_index(name='user_avg_rating')
            fig_user_avg = px.bar(
                user_avg,
                x='username',
                y='user_avg_rating',
                labels={'user_avg_rating': 'Average Rating', 'username': 'User'},
                color='user_avg_rating',
                color_continuous_scale='Tealgrn'
            )
            fig_user_avg.update_traces(
                marker_line_width=0.5,  # Add thin bar outlines for clarity
                marker_line_color="black"  # Define outline color
            )
            fig_user_avg.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with other graphs
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels for readability
                    tickmode="linear",  # Ensure all labels are displayed
                    title=None  # Remove the x-axis title ("User")
                ),
                yaxis=dict(
                    title="Average Rating",
                    title_standoff=10  # Add some spacing between y-axis title and ticks
                ),
                showlegend=False,  # Remove the legend
                coloraxis_showscale=False  # Remove the color scale
            )
            user_avg_graph = fig_user_avg.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 8. User Album Counts Bar Chart
            user_album_counts = df.groupby('username')['album'].nunique().reset_index(name='album_count')
            fig_user_counts = px.bar(
                user_album_counts,
                x='username',
                y='album_count',
                labels={'album_count': 'Album Count', 'username': 'User'},
                color='album_count',
                color_continuous_scale='Portland'
            )
            fig_user_counts.update_traces(
                marker_line_width=0.5,  # Add thin bar outlines for clarity
                marker_line_color="black"  # Define outline color
            )
            fig_user_counts.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with other graphs
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels for readability
                    tickmode="linear",  # Ensure all labels are displayed
                    title=None  # Remove the x-axis title ("User")
                ),
                yaxis=dict(
                    title="Album Count",
                    title_standoff=10  # Add some spacing between y-axis title and ticks
                ),
                showlegend=False,  # Remove the legend
                coloraxis_showscale=False  # Remove the color scale
            )
            user_counts_graph = fig_user_counts.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 9. User Genre Distribution Interactive Dot Plot
            # [Updated Code Below]

            # Extract genres from genre_1 and genre_2 columns
            user_g1 = df[['username', 'genre_1']].rename(columns={'genre_1': 'genre'}).dropna()
            user_g2 = df[['username', 'genre_2']].rename(columns={'genre_2': 'genre'}).dropna()
            user_genre_counts = pd.concat([user_g1, user_g2], ignore_index=True)

            if not user_genre_counts.empty:
                # Aggregate counts per user and genre
                user_genre_counts = user_genre_counts.groupby(['username', 'genre']).size().reset_index(name='count')
                
                # Calculate total albums per user for percentage calculations
                total_albums_per_user = user_genre_counts.groupby('username')['count'].sum().reset_index(name='total_albums')
                
                # Merge total albums back to genre counts
                user_genre_counts = user_genre_counts.merge(total_albums_per_user, on='username')
                
                # Calculate percentage contribution of each genre per user
                user_genre_counts['percentage'] = (user_genre_counts['count'] / user_genre_counts['total_albums']) * 100
                
                # Determine a consistent genre order (alphabetical for dynamic handling)
                genre_order = sorted(user_genre_counts['genre'].unique())
                
                # Sort users by total albums descending
                user_genre_counts['username'] = pd.Categorical(
                    user_genre_counts['username'],
                    categories=total_albums_per_user.sort_values('total_albums', ascending=False)['username'],
                    ordered=True
                )
                
                # Sort genres based on the determined order
                user_genre_counts['genre'] = pd.Categorical(user_genre_counts['genre'], categories=genre_order, ordered=True)
                user_genre_counts = user_genre_counts.sort_values(['genre', 'username'])
                
                # Generate a color palette with enough distinct colors
                num_genres = len(genre_order)
                # Use Plotly's qualitative color palettes; cycle through if genres exceed palette length
                base_colors = pc.qualitative.Plotly  # You can choose other palettes like 'Pastel', 'Dark24', etc.
                colors = base_colors * (num_genres // len(base_colors) + 1)  # Ensure enough colors
                color_map = {genre: colors[i] for i, genre in enumerate(genre_order)}
                
                # Create Interactive Dot Plot
            fig_user_genre = px.scatter(
                user_genre_counts,
                x='username',
                y='genre',
                size='count',
                color='genre',
                labels={
                    'username': 'User',
                    'genre': 'Genre',
                    'count': 'Number of Albums'
                },
                title=None,
                height=500  # Set consistent height with other graphs
            )
            fig_user_genre.update_traces(
                hovertemplate='<b>User:</b> %{x}<br><b>Genre:</b> %{y}<br><b>Albums:</b> %{marker.size}<extra></extra>',
                marker=dict(opacity=0.7, line=dict(width=0.5, color='black'))  # Slight border for clarity
            )
            fig_user_genre.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels
                    title=None  # Remove x-axis title
                ),
                yaxis=dict(
                    title=None  # Remove y-axis title
                ),
                showlegend=False  # Remove the legend
            )
            user_genre_graph = fig_user_genre.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 10. Ratings Distribution Histogram
            fig_rating_hist = px.histogram(
                df_unique,
                x='avg_rating',
                nbins=20,
                labels={'avg_rating': 'Average Rating'},
                color_discrete_sequence=['#0d6efd']
            )
            fig_rating_hist.update_traces(
                opacity=0.8  # Slight transparency for better visibility
            )
            fig_rating_hist.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with other graphs
                xaxis=dict(
                    title=None  # Remove x-axis title
                ),
                yaxis=dict(
                    title="Count",
                    title_standoff=10  # Add spacing between y-axis title and ticks
                ),
                showlegend=False  # Remove the legend
            )
            rating_histogram = fig_rating_hist.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 11. Genre Popularity Over Time Line Chart (Now by Month)
            genre_trend = df_unique.explode(['genre_1', 'genre_2'])
            genre_trend = genre_trend.melt(
                id_vars=['month'],
                value_vars=['genre_1', 'genre_2'],
                var_name='genre_type',
                value_name='genre'
            ).dropna(subset=['genre'])
            genre_trend_count = genre_trend.groupby(['month', 'genre']).size().reset_index(name='count')
            genre_trend_count['month_name'] = pd.to_datetime(genre_trend_count['month'], format='%m').dt.strftime('%B')
            genre_trend_count = genre_trend_count.sort_values('month')

            fig_genre_trend = px.scatter(
                genre_trend_count,
                x='month_name',
                y='count',
                color='genre',
                labels={'month_name': 'Month', 'count': 'Number of Albums'},
                title=None,
                height=500  # Set consistent height with other graphs
            )
            fig_genre_trend.update_traces(
                marker=dict(size=8, line=dict(width=0.5, color='black')),  # Improve marker visibility
                mode='markers'  # Use markers only, no lines
            )
            fig_genre_trend.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                xaxis=dict(
                    tickangle=-45,  # Rotate x-axis labels
                    title=None  # Remove x-axis title
                ),
                yaxis=dict(
                    title="Number of Albums",
                    title_standoff=10  # Add spacing between y-axis title and ticks
                ),
                showlegend=False  # Remove the legend
            )
            genre_trend_graph = fig_genre_trend.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 12. Top Artists Bar Chart
            top_artists = df_unique.groupby('artist')['total_points'].sum().reset_index().sort_values(
                by='total_points', ascending=False
            ).head(10)

            fig_top_artists = px.bar(
                top_artists,
                x='artist',
                y='total_points',
                labels={'total_points': 'Total Points', 'artist': 'Artist'},
                color='total_points',
                color_continuous_scale='YlGnBu'
            )
            fig_top_artists.update_traces(
                marker_line_width=0.5,  # Add thin bar outlines for clarity
                marker_line_color="black"  # Define outline color
            )
            fig_top_artists.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),  # Remove unnecessary margins
                height=500,  # Set consistent height with other graphs
                xaxis=dict(
                    tickangle=-45,  # Angle x-axis labels for readability
                    title=None  # Remove x-axis title
                ),
                yaxis=dict(
                    title="Total Points",
                    title_standoff=10  # Add spacing between y-axis title and ticks
                ),
                showlegend=False,  # Remove the legend
                coloraxis_showscale=False  # Remove the color scale
            )
            top_artists_graph = fig_top_artists.to_html(full_html=False, include_plotlyjs=False, config={
                "displayModeBar": False  # Disable the toolbar
            })

            # 9. User Genre Distribution Interactive Dot Plot
            # [Already Implemented Above]

            # Prepare final data
            albums = df_unique.to_dict(orient='records')
            # current_year already set to report_year

            env = Environment(loader=FileSystemLoader('.'))
            try:
                template_path = resource_path('template.html')  # Use resource_path
                env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
                template = env.get_template(os.path.basename(template_path))
            except Exception as e:
                QMessageBox.critical(self, "Template Error", f"Failed to load 'template.html':\n{e}")
                return

            html_content = template.render(
                bar_graph=bar_graph,
                treemap_graph=treemap_graph,
                map_graph=map_graph,
                avg_graph=avg_graph,
                genre_graph=genre_graph,
                time_graph=time_graph,
                user_avg_graph=user_avg_graph,
                user_counts_graph=user_counts_graph,
                user_genre_graph=user_genre_graph,
                rating_histogram=rating_histogram,
                genre_trend_graph=genre_trend_graph,  # Updated graph
                top_artists_graph=top_artists_graph,
                albums=albums,
                total_albums=total_albums,
                unique_artists=unique_artists,
                unique_genres=unique_genres,
                countries=countries,
                unique_users=unique_users,
                current_year=current_year  # For dynamic footer year
            )

            # Save HTML Report to Desktop
            desktop_path = Path.home() / "Desktop"
            output_path = desktop_path / "album_report.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Open the Report in Default Browser
            webbrowser.open(f'file://{output_path}')
            QMessageBox.information(self, "Success", "HTML report generated and opened in browser.")

        except Exception as e:
            # Handle unexpected errors gracefully
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")
            # Optionally, log the error details for debugging
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
