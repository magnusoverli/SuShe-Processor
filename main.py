import sys
import os
import json
import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from jinja2 import Environment, FileSystemLoader
import webbrowser
import base64
from io import BytesIO
from PIL import Image
import datetime  # For dynamic footer year


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Album Presentation App")
        self.setGeometry(100, 100, 400, 300)
        
        self.data = None
        
        # Layout setup
        layout = QVBoxLayout()
        
        # Load JSON Button
        self.load_button = QPushButton("Load JSON Data")
        self.load_button.clicked.connect(self.load_json)
        layout.addWidget(self.load_button)
        
        # Generate HTML Button
        self.generate_button = QPushButton("Generate HTML Report")
        self.generate_button.clicked.connect(self.generate_html)
        self.generate_button.setEnabled(False)
        layout.addWidget(self.generate_button)
        
        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
        
        # Set layout to central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def load_json(self):
        """Allow users to select and load multiple JSON files, assigning a username to each."""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Open JSON Files", "", "JSON Files (*.json)"
        )
        if file_paths:
            try:
                data_list = []
                for path in file_paths:
                    # Prompt for username
                    username, ok = QInputDialog.getText(self, "Username Input", f"Enter username for '{os.path.basename(path)}':")
                    if not ok or not username.strip():
                        QMessageBox.warning(self, "Input Required", f"Username is required for '{os.path.basename(path)}'. Skipping this file.")
                        continue
                    username = username.strip()
                    
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            # Add username to each album
                            for album in data:
                                album['username'] = username
                            data_list.extend(data)
                        else:
                            raise ValueError(f"Invalid JSON format in {path}. Expected a list of albums.")
                if not data_list:
                    QMessageBox.warning(self, "No Data Loaded", "No valid data was loaded.")
                    return
                self.data = data_list
                QMessageBox.information(
                    self, "Success", f"Loaded {len(file_paths)} JSON file(s) successfully.\nTotal Albums: {len(self.data)}"
                )
                self.generate_button.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON files:\n{e}")
    
    def resize_image(self, img_str, max_size=(100, 100)):
        """Resize base64-encoded images to optimize performance."""
        try:
            img_data = base64.b64decode(img_str)
            image = Image.open(BytesIO(img_data))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)  # PIL>=9.1 uses Resampling
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Image processing error: {e}")
            return img_str  # Return original if there's an error
    
    def generate_html(self):
        """Process data and generate the interactive HTML report."""
        if not self.data:
            QMessageBox.warning(self, "No Data", "Please load JSON data first.")
            return

        try:
            df = pd.DataFrame(self.data)
            
            # Remove 'comments' column if it exists
            if 'comments' in df.columns:
                df.drop(columns=['comments'], inplace=True)
            
            # Data Cleaning and Type Conversion
            df['release_date'] = pd.to_datetime(df['release_date'], format='%d-%m-%Y', errors='coerce')
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce').astype(pd.Int64Dtype())
            df['points'] = pd.to_numeric(df['points'], errors='coerce').astype(pd.Int64Dtype())
            
            # Check for any conversion issues
            if df['release_date'].isnull().any():
                QMessageBox.warning(self, "Data Warning", "Some release dates could not be parsed and are set as NaT.")
            if df['rating'].isnull().any():
                QMessageBox.warning(self, "Data Warning", "Some ratings could not be converted to numbers and are set as NaN.")
            
            # Resize Images
            if 'cover_image' in df.columns:
                df['cover_image'] = df['cover_image'].apply(lambda x: self.resize_image(x))
            
            # Aggregate Points Per Album
            points_aggregated = df.groupby('album')['points'].sum().reset_index().rename(columns={'points': 'total_points'})
            
            # Calculate Average Rating Per Album
            rating_aggregated = df.groupby('album')['rating'].mean().reset_index().rename(columns={'rating': 'avg_rating'})
            
            # Merge aggregated points and ratings back to the main dataframe
            df_agg = df.merge(points_aggregated, on='album', how='left').merge(rating_aggregated, on='album', how='left')
            
            # Remove duplicate rows after aggregation
            df_unique = df_agg.drop_duplicates(subset=['album'])
            
            # Create a Contributors column that lists all users and their ranks for each album
            contributors = df.groupby('album').apply(
                lambda x: "; ".join([f"{user} ({rank})" for user, rank in zip(x['username'], x['rank']) if pd.notnull(rank)])
            ).reset_index(name='contributors')
            
            # Merge contributors back to the unique dataframe
            df_unique = df_unique.merge(contributors, on='album', how='left')
            
            # Sort the unique dataframe by total_points in descending order
            df_unique.sort_values(by='total_points', ascending=False, inplace=True)
            
            # Data Aggregations for Visualizations
            artist_avg = df.groupby('artist')['rating'].mean().reset_index().rename(columns={'rating': 'avg_rating'})
            genre_counts = pd.concat([df['genre_1'], df['genre_2']]).value_counts().reset_index()
            genre_counts.columns = ['genre', 'count']
            df_unique['year'] = df_unique['release_date'].dt.year  # Extract year for time-based analysis
            
            # User-Based Aggregations
            user_avg = df.groupby('username')['rating'].mean().reset_index().rename(columns={'rating': 'user_avg_rating'})
            user_album_counts = df['username'].value_counts().reset_index()
            user_album_counts.columns = ['username', 'album_count']
            user_genre_counts = df.groupby('username')[['genre_1', 'genre_2']].agg(lambda x: x.value_counts().to_dict()).reset_index()
            
            # Summary Statistics
            total_albums = len(df_unique)
            unique_artists = df_unique['artist'].nunique()
            unique_genres = genre_counts['genre'].nunique()
            countries = df_unique['country'].nunique()
            unique_users = df_unique['username'].nunique()
            
            # Visualizations
            # 1. Album Ratings Bar Chart
            fig_bar = px.bar(
                df_unique, 
                x='album', 
                y='avg_rating', 
                color='artist', 
                title='Album Ratings (Average)',
                labels={'avg_rating': 'Average Rating', 'album': 'Album'}, 
                hover_data=['artist']
            )
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            bar_graph = fig_bar.to_html(full_html=False, include_plotlyjs='cdn')
            
            # 2. Genre Distribution Pie Chart
            fig_pie = px.pie(
                genre_counts, 
                names='genre', 
                values='count', 
                title='Genre Distribution',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_pie.update_traces(textinfo='percent+label')
            pie_graph = fig_pie.to_html(full_html=False, include_plotlyjs=False)
            
            # 3. Albums by Country Map (Choropleth)
            country_agg = df_unique.groupby('country').agg(
                num_albums=pd.NamedAgg(column='album', aggfunc='count'),
                avg_rating=pd.NamedAgg(column='avg_rating', aggfunc='mean')
            ).reset_index()
            
            fig_map = px.choropleth(
                country_agg,
                locations="country",
                locationmode='country names',
                color="avg_rating",
                hover_name="country",
                color_continuous_scale='Viridis',
                title="Average Album Ratings by Country",
                labels={'avg_rating': 'Average Rating'},
                projection="natural earth"
            )
            fig_map.update_traces(
                hovertemplate="<b>%{location}</b><br>Average Rating: %{z:.2f}<br>Number of Albums: %{customdata[0]}"
            )
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title="Average Rating",
                    tickvals=[country_agg['avg_rating'].min(), country_agg['avg_rating'].max()],
                    ticktext=[f"{country_agg['avg_rating'].min():.2f}", f"{country_agg['avg_rating'].max():.2f}"]
                )
            )
            fig_map.update_traces(customdata=country_agg[['num_albums']])
            map_graph = fig_map.to_html(full_html=False, include_plotlyjs=False)
            
            # 4. Average Rating per Artist Bar Chart
            fig_avg = px.bar(
                artist_avg, 
                x='artist', 
                y='avg_rating', 
                title='Average Rating per Artist',
                labels={'avg_rating': 'Average Rating', 'artist': 'Artist'},
                color='avg_rating', 
                color_continuous_scale='Viridis'
            )
            fig_avg.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            avg_graph = fig_avg.to_html(full_html=False, include_plotlyjs=False)
            
            # 5. Genre Counts Bar Chart
            fig_genre = px.bar(
                genre_counts, 
                x='genre', 
                y='count', 
                title='Genre Counts',
                labels={'count': 'Count', 'genre': 'Genre'},
                color='count', 
                color_continuous_scale='Sunset'
            )
            fig_genre.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            genre_graph = fig_genre.to_html(full_html=False, include_plotlyjs=False)
            
            # 6. Ratings Over Time Line Chart
            fig_time = px.line(
                df_unique, 
                x='release_date', 
                y='avg_rating', 
                color='artist', 
                title='Average Ratings Over Time',
                labels={'release_date': 'Release Date', 'avg_rating': 'Average Rating'},
                markers=True
            )
            fig_time.update_layout(
                hovermode="x unified",
                margin=dict(b=150)
            )
            time_graph = fig_time.to_html(full_html=False, include_plotlyjs=False)
            
            # 7. User Average Ratings Bar Chart
            fig_user_avg = px.bar(
                user_avg, 
                x='username', 
                y='user_avg_rating', 
                title='Average Rating per User',
                labels={'user_avg_rating': 'Average Rating', 'username': 'User'},
                color='user_avg_rating', 
                color_continuous_scale='Tealgrn'
            )
            fig_user_avg.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            user_avg_graph = fig_user_avg.to_html(full_html=False, include_plotlyjs=False)
            
            # 8. User Album Counts Bar Chart
            fig_user_counts = px.bar(
                user_album_counts, 
                x='username', 
                y='album_count', 
                title='Number of Albums per User',
                labels={'album_count': 'Album Count', 'username': 'User'},
                color='album_count', 
                color_continuous_scale='Portland'
            )
            fig_user_counts.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            user_counts_graph = fig_user_counts.to_html(full_html=False, include_plotlyjs=False)
            
            # 9. User Genre Distribution Heatmap
            user_genre_flat = []
            for index, row in user_genre_counts.iterrows():
                user = row['username']
                genres = row[['genre_1', 'genre_2']].to_dict()
                for genre, count in genres.items():
                    if isinstance(count, dict):
                        for g, c in count.items():
                            user_genre_flat.append({'username': user, 'genre': g, 'count': c})
            
            user_genre_df = pd.DataFrame(user_genre_flat)
            if not user_genre_df.empty:
                fig_user_genre = px.density_heatmap(
                    user_genre_df, 
                    x='username', 
                    y='genre', 
                    z='count',
                    title='Genre Distribution per User',
                    labels={'count': 'Count', 'username': 'User', 'genre': 'Genre'},
                    color_continuous_scale='Blues'
                )
                fig_user_genre.update_layout(
                    margin=dict(b=150)
                )
                user_genre_graph = fig_user_genre.to_html(full_html=False, include_plotlyjs=False)
            else:
                user_genre_graph = "<p>No genre data available for users.</p>"
            
            # 10. Ratings Distribution Histogram
            fig_rating_hist = px.histogram(
                df_unique, 
                x='avg_rating', 
                nbins=20, 
                title='Ratings Distribution',
                labels={'avg_rating': 'Average Rating'},
                color_discrete_sequence=['#0d6efd']
            )
            fig_rating_hist.update_layout(
                hovermode="x",
                margin=dict(b=100)
            )
            rating_histogram = fig_rating_hist.to_html(full_html=False, include_plotlyjs=False)
            
            # 11. Correlation Matrix Heatmap
            corr = df_unique[['avg_rating', 'total_points']].corr()
            fig_corr = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale='RdBu',
                title='Correlation Matrix'
            )
            fig_corr.update_layout(
                margin=dict(t=100, l=100, r=100, b=100)
            )
            correlation_heatmap = fig_corr.to_html(full_html=False, include_plotlyjs=False)
            
            # 12. Genre Popularity Over Time Line Chart
            genre_trend = df_unique.explode(['genre_1', 'genre_2'])
            genre_trend = genre_trend.melt(id_vars=['year'], value_vars=['genre_1', 'genre_2'], var_name='Genre Type', value_name='Genre')
            genre_trend = genre_trend.dropna(subset=['Genre'])
            genre_trend_count = genre_trend.groupby(['year', 'Genre']).size().reset_index(name='count')
            
            fig_genre_trend = px.line(
                genre_trend_count, 
                x='year', 
                y='count', 
                color='Genre',
                title='Genre Popularity Over Time',
                labels={'year': 'Year', 'count': 'Number of Albums'},
                markers=True
            )
            fig_genre_trend.update_layout(
                hovermode="x unified",
                margin=dict(b=150)
            )
            genre_trend_graph = fig_genre_trend.to_html(full_html=False, include_plotlyjs=False)
            
            # 13. Top Artists by Total Points Bar Chart
            top_artists = df_unique.groupby('artist')['total_points'].sum().reset_index().sort_values(by='total_points', ascending=False).head(10)
            fig_top_artists = px.bar(
                top_artists, 
                x='artist', 
                y='total_points', 
                title='🏆 Top Artists by Total Points',
                labels={'total_points': 'Total Points', 'artist': 'Artist'},
                color='total_points',
                color_continuous_scale='YlGnBu'
            )
            fig_top_artists.update_layout(
                xaxis_tickangle=-45,
                hovermode="closest",
                margin=dict(b=150)
            )
            top_artists_graph = fig_top_artists.to_html(full_html=False, include_plotlyjs=False)
            
            # Prepare Data for HTML (Albums Table)
            albums = df_unique.to_dict(orient='records')
            
            # Current Year for Footer
            current_year = datetime.datetime.now().year
            
            # Setup Jinja2 Environment
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('template.html')
            
            # Render HTML with all components
            html_content = template.render(
                bar_graph=bar_graph,
                pie_graph=pie_graph,
                map_graph=map_graph,
                avg_graph=avg_graph,
                genre_graph=genre_graph,
                time_graph=time_graph,
                user_avg_graph=user_avg_graph,
                user_counts_graph=user_counts_graph,
                user_genre_graph=user_genre_graph,
                rating_histogram=rating_histogram,
                correlation_heatmap=correlation_heatmap,
                genre_trend_graph=genre_trend_graph,
                top_artists_graph=top_artists_graph,
                albums=albums,
                total_albums=total_albums,
                unique_artists=unique_artists,
                unique_genres=unique_genres,
                countries=countries,
                unique_users=unique_users,
                current_year=current_year  # For dynamic footer year
            )
            
            # Save HTML Report
            output_path = os.path.join(os.getcwd(), "album_report.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open the Report in Default Browser
            webbrowser.open(f'file://{output_path}')
            QMessageBox.information(self, "Success", "HTML report generated and opened in browser.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate HTML report:\n{e}")

def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
