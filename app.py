from flask import Flask, render_template, request, session, url_for
import pyodbc

app = Flask(__name__)
app.secret_key = 'Lepi'

def connect_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=LEPILAPTOP\\SQLEXPRESS05;'
        'DATABASE=NetflixClone;'
        'Trusted_Connection=yes;'
    )
    return conn

def fetch_movies():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Title, ReleaseYear, Genre, VideoFileName FROM Movies")
    movies = cursor.fetchall()
    conn.close()
    return [{'Title': row[0], 'ReleaseYear': row[1], 'Genre': row[2], 'VideoFileName': row[3]} for row in movies]

def fetch_genres():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Genre FROM Movies")
    genres = [row[0] for row in cursor.fetchall()]
    conn.close()
    return genres

def sort_by_year(movies):
    n = len(movies)
    for i in range(n):
        for j in range(0, n-i-1):
            if movies[j]['ReleaseYear'] > movies[j+1]['ReleaseYear']:
                movies[j], movies[j+1] = movies[j+1], movies[j]
    return movies

def sort_by_title(movies):
    n = len(movies)
    for i in range(n):
        for j in range(0, n-i-1):
            if movies[j]['Title'].lower() > movies[j+1]['Title'].lower():
                movies[j], movies[j+1] = movies[j+1], movies[j]
    return movies

def search_by_title(movies, search_term):
    found_movies = []
    for movie in movies:
        if search_term.lower() in movie['Title'].lower():
            found_movies.append(movie)
    return found_movies

def filter_by_genre(movies, genre):
    genre_movies = []
    for movie in movies:
        if movie['Genre'].lower() == genre.lower():
            genre_movies.append(movie)
    return genre_movies

def unfilter_movies():
    return fetch_movies()

@app.route('/', methods=['GET', 'POST'])
def index():
    genres = fetch_genres()
    
    movies = session.get('filtered_movies', fetch_movies())

    if request.method == 'POST':
        action = request.form['action']
        
        if action == 'Sort by Year':
            movies = sort_by_year(movies)
        elif action == 'Sort by Title':
            movies = sort_by_title(movies)
        elif action == 'Search':
            search_term = request.form['search_term']
            movies = search_by_title(fetch_movies(), search_term)
        elif action == 'Filter':
            genre = request.form['genre']
            movies = filter_by_genre(fetch_movies(), genre)
        elif action == 'Unfilter':
            movies = unfilter_movies()
        
        session['filtered_movies'] = movies
    
    return render_template('index.html', movies=movies, genres=genres)

@app.route('/video/<video_file>')
def video(video_file):
    return render_template('video.html', video_file=video_file)

if __name__ == '__main__':
    app.run(debug=True)