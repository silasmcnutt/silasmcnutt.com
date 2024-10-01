import pyperclip
import requests
import sys
import os
from datetime import datetime, timedelta
import pytz

# TMDb API key - replace with your key
API_KEY = '6b8d8648d6eef0d83f9a07c533484262'

def get_movie_poster(movie_name, year):
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}&year={year}'

    response = requests.get(search_url)
    data = response.json()

    if data['results']:
        movie = data['results'][0]
        poster_path = movie['poster_path']
        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
        return poster_url, movie['id']
    else:
        return None, None

def parse_markdown(file_content):
    print("Parsing markdown file...")  # Debugging output
    sections = file_content.split('+++++')
    parsed_data = {}

    for section in sections:
        lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
        if not lines:
            continue

        header = lines[0]
        
        if 'This Month\'s Movies' in header:
            print("Processing 'This Month's Movies' section")  # Debugging output
            movies = []
            i = 1
            while i < len(lines):
                if lines[i] == '-----':  # Start of a new movie entry
                    movie = {
                        'title': lines[i + 1],
                        'year': lines[i + 2],
                        'rating': lines[i + 3],
                        'review': lines[i + 4] if i + 4 < len(lines) else ''
                    }
                    movies.append(movie)
                    i += 5  # Move past this movie entry
                else:
                    i += 1
            parsed_data['movies'] = movies

        elif 'This Month\'s Winner' in header:
            print("Processing 'This Month\'s Winner' section")  # Debugging output
            winner = {}
            i = 1
            while i < len(lines):
                if lines[i] == '-----':  # Start of the winner entry
                    winner = {
                        'title': lines[i + 1],
                        'year': lines[i + 2],
                        'review': lines[i + 3]
                    }
                    i += 4  # Move past the winner entry
                else:
                    i += 1
            parsed_data['winner'] = winner

        elif 'Rating Changes' in header:
            print("Processing 'Rating Changes' section")  # Debugging output
            changes = []
            i = 1
            while i < len(lines):
                if lines[i] == '-----':  # Start of a rating change entry
                    change = {
                        'title': lines[i + 1],
                        'year': lines[i + 2],
                        'old_rating': lines[i + 3],
                        'new_rating': lines[i + 4],
                        'explanation': lines[i + 5] if i + 5 < len(lines) else ''
                    }
                    changes.append(change)
                    i += 6  # Move past this rating change entry
                else:
                    i += 1
            parsed_data['rating_changes'] = changes

        elif 'Watchlist Additions' in header:
            print("Processing 'Watchlist Additions' section")  # Debugging output
            watchlist = []
            i = 1
            while i < len(lines):
                if lines[i] == '-----':  # Start of a watchlist entry
                    watchlist_item = {
                        'title': lines[i + 1],
                        'year': lines[i + 2]
                    }
                    watchlist.append(watchlist_item)
                    i += 3  # Move past this watchlist entry
                else:
                    i += 1
            parsed_data['watchlist'] = watchlist

    return parsed_data

def number_to_word(n):
    """Convert a number to its word representation for class names."""
    num_words = {
        10: 'ten',
        9: 'nine',
        8: 'eight',
        7: 'seven',
        6: 'six',
        5: 'five',
        4: 'four',
        3: 'three',
        2: 'two',
        1: 'one',
        0: 'zero'
    }
    return num_words.get(n, 'unknown')  # Default to 'unknown' if number is not in range

def generate_html(parsed_data):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>This Month's Movies</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <!-- This Month's Movies -->
    <div class="movie-list">
        <h1>This Month's Movies</h1>
"""

    # Movies Section
    for movie in parsed_data.get('movies', []):
        poster_url, _ = get_movie_poster(movie['title'], movie['year'])
        html_content += f"""
        <div class="movie">
            <img src="{poster_url}" alt="{movie['title']} ({movie['year']})">
            <div class="movie-details">
                <h2>{movie['title']} ({movie['year']})</h2>
                <p>{movie['review']}</p>
            </div>
            <div class="movie-rating">
                <span class="number {movie['rating']}">{movie['rating']}</span>
                <span class="separator">/</span>
                <span class="denominator">10</span>
            </div>
        </div>
        """

    html_content += """
    </div>
    <!-- This Month's Winner Section -->
    <div class="winner">
        <h1>This Month's Winner</h1>
        <div class="winner-section">
    """

    # Winner Section
    winner = parsed_data.get('winner', {})
    if winner:
        winner_poster, _ = get_movie_poster(winner['title'], winner['year'])
        html_content += f"""
            <div class="fancy">
                <img src="{winner_poster}" alt="{winner['title']}" class="base-image">
                <img src="{winner_poster}" alt="{winner['title']}" class="top-image">
            </div>
            <div class="winner-text">
                <h2>{winner['title']} ({winner['year']})</h2>
                <p>{winner['review']}</p>
            </div>
        """

    html_content += """
        </div>
    </div>
    <!-- Rating Change Section -->
    <div class="rating-change-list">
        <h1>Rating Changes</h1>
    """

    # Rating Changes Section
    for change in parsed_data.get('rating_changes', []):
        change_poster, _ = get_movie_poster(change['title'], change['year'])
        html_content += f"""
        <div class="rating-change">
            <img src="{change_poster}" alt="{change['title']}">
            <div class="rating-change-details">
                <h2>{change['title']} ({change['year']})</h2>
                <p>{change['explanation']}</p>
            </div>
            <div class="rating-change-rating">
                <span class="old-rating">{change['old_rating']}</span>
                <span class="arrow"><i class="fas fa-arrow-right"></i></span>
                <span class="new-rating">{change['new_rating']}</span>
            </div>
        </div>
        """

    html_content += """
    </div>
    <!-- Watchlist Additions Section -->
    <div class="watchlist">
        <h1>Watchlist Additions</h1>
        <div class="watchlist-grid">
    """

    # Watchlist Section
    for watchlist_item in parsed_data.get('watchlist', []):
        watchlist_poster, movie_id = get_movie_poster(watchlist_item['title'], watchlist_item['year'])
        if watchlist_poster and movie_id:
            letterboxd_url = f'https://letterboxd.com/tmdb/{movie_id}/'
            html_content += f"""
            <div class="watchlist-item">
                <a href="{letterboxd_url}" target="_blank">
                    <img src="{watchlist_poster}" alt="{watchlist_item['title']}">
                </a>
            </div>
            """

    html_content += """
        </div>
    </div>
</body>
</html>
"""

    return html_content



def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py <path_to_markdown_file> [<output_html_file>]")
        sys.exit(1)

    markdown_file = sys.argv[1]
    if not os.path.isfile(markdown_file):
        print(f"Error: The file {markdown_file} does not exist.")
        sys.exit(1)

    with open(markdown_file, 'r', encoding='utf-8') as file:
        file_content = file.read()

    parsed_data = parse_markdown(file_content)
    html_content = generate_html(parsed_data)

    # Copy to clipboard
    pyperclip.copy(html_content)
    print("HTML content copied to clipboard.")

    # Output to file if specified
    if len(sys.argv) == 3:
        output_html_file = sys.argv[2]
        with open(output_html_file, 'w', encoding='utf-8') as output_file:
            output_file.write(html_content)
        print(f"HTML content written to {output_html_file}.")

if __name__ == "__main__":
    main()
