from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
from collections import Counter
from bs4 import BeautifulSoup  # Import BeautifulSoup


# Create a Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) to handle requests from different origins
CORS(app)

# Configure the SQLAlchemy database URI and track modifications
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create an SQLAlchemy instance for database interaction
db = SQLAlchemy(app)

# Define a model for the SearchHistory table in the database
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    top_words = db.Column(db.String(255), nullable=False)

# Helper function to fetch data from the Wikipedia API based on the provided topic
def fetch_wikipedia_data(topic):
    try:
        # Construct the Wikipedia API URL for the specified topic to get the page ID
        page_id_url = f'https://en.wikipedia.org/w/api.php?action=query&format=json&titles={topic}'

        # Make a GET request to get the page ID
        response = requests.get(page_id_url)
        response.raise_for_status()
        data = response.json()

        # Get the page ID from the API response
        page_id = list(data['query']['pages'].keys())[0]

        # Use the obtained page ID to construct the URL for fetching the full content
        full_content_url = f'https://en.wikipedia.org/w/api.php?action=query&format=json&pageids={page_id}&prop=extracts'

        # Make a GET request to fetch the full content
        response = requests.get(full_content_url)
        response.raise_for_status()

        # Parse the JSON response and return the data
        return response.json()

    except requests.exceptions.RequestException as e:
        app.logger.error(f'Error fetching Wikipedia data: {str(e)}')
        return None

# HELPER function to save search history entries to the database
def save_search_history(topic, word_frequency_result):
    # Convert the word frequency result to a string before saving
    top_words_str = ', '.join([f'{word}: {count}' for word, count in word_frequency_result])

    # Create a new SearchHistory entry and add it to the session
    search_entry = SearchHistory(topic=topic, top_words=top_words_str)
    db.session.add(search_entry)
    
    # Commit the changes to the database
    db.session.commit()

# Helper function to perform word frequency analysis
def analyze_word_frequency(article_text, n):
    # Split the article text into words
    words = article_text.split()

    # Use Counter to count the frequency of each word
    word_frequency = Counter(words).most_common(n)

    return word_frequency

# Endpoint for Word Frequency Analysis
@app.route('/word_frequency', methods=['GET'])
def word_frequency():
    # Retrieve the 'topic' and 'n' parameters from the request's query parameters
    topic = request.args.get('topic')
    n = request.args.get('n')

    # Check if both 'topic' and 'n' parameters are provided
    if not topic or not n:
        return jsonify({'error': 'Invalid input. Both topic and n are required.'}), 400

    try:
        # Convert 'n' to an integer and check if it's a positive value
        n = int(n)
        if n <= 0:
            raise ValueError('Invalid value for n. Please provide a positive integer.')
    except ValueError as e:
        # Handle the case where 'n' is not a valid integer
        return jsonify({'error': f'Invalid value for n. {str(e)}'}), 400

    # Fetch data from Wikipedia based on the provided topic
    data = fetch_wikipedia_data(topic)

    # Check if data is retrieved successfully and contains the expected structure
    if not data or 'query' not in data or 'pages' not in data['query']:
        return jsonify({'error': 'Invalid topic. Wikipedia article not found.'}), 404

    # Extract details from the Wikipedia API response
    page_id = list(data['query']['pages'].keys())[0]
    if 'title' not in data['query']['pages'][page_id]:
        return jsonify({'error': 'Failed to retrieve article details from Wikipedia.'}), 500

    # Extract the article text from the API response
    article_text = data['query']['pages'][page_id]['extract']

    # Remove HTML tags from the article text
    clean_text = BeautifulSoup(article_text, 'html.parser').get_text()

    if not clean_text:
        app.logger.error(f'Failed to retrieve clean article text from Wikipedia. API Response: {data}')
        return jsonify({'error': 'Failed to retrieve clean article text from Wikipedia.'}), 500

    # Perform word frequency analysis on the clean text
    word_frequency_result = analyze_word_frequency(clean_text, n)

    # Save the search history entry to the database
    save_search_history(topic, word_frequency_result)

    # Return the word frequency analysis result in the response
    return jsonify({'word_frequency': word_frequency_result})

# Endpoint for retrieving search history entries
@app.route('/search_history', methods=['GET'])
def search_history():
    # Query all search history entries from the database
    searches = SearchHistory.query.all()
    
    # Convert search history entries to a list of dictionaries
    search_history_data = [{'topic': entry.topic, 'top_words': entry.top_words} for entry in searches]

    # Return the search history data in the response
    return jsonify({'search_history': search_history_data})

# Entry point for running the Flask application
if __name__ == '__main__':
    # Create the required tables in the database
    with app.app_context():
        db.create_all()

    # Run the application in debug mode
    app.run(debug=True)
