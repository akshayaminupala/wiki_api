import unittest
from flask import json
from assignment import app, db, SearchHistory, analyze_word_frequency, fetch_wikipedia_data

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_search_history.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()
    def test_word_frequency_endpoint_large_n(self):
        # Test the /word_frequency endpoint with a large value for n
        response = self.app.get('/word_frequency?topic=Pride&n=1000')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('word_frequency', data)
        self.assertLessEqual(len(data['word_frequency']), 1000)

    def test_word_frequency_endpoint_nonexistent_topic(self):
        # Test the /word_frequency endpoint with a nonexistent topic
        response = self.app.get('/word_frequency?topic=NonExistentTopic&n=5')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)

    def test_word_frequency_endpoint_long_topic(self):
        # Test the /word_frequency endpoint with a long topic
        long_topic = 'A' * 256  # Exceeding the allowed length
        response = self.app.get(f'/word_frequency?topic={long_topic}&n=5')
        data = json.loads(response.data.decode('utf-8'))
       

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)


    def test_analyze_word_frequency_empty_text(self):
        # Test the analyze_word_frequency function with an empty article text
        article_text = ""
        result = analyze_word_frequency(article_text, 2)

        self.assertEqual(result, [])

    def test_analyze_word_frequency_non_alphabetic_text(self):
    # Test the analyze_word_frequency function with non-alphabetic article text
        article_text = "12345 67890 !@#$%^&*"
        result = analyze_word_frequency(article_text, 3)

        # Filter out non-alphabetic words from the result
        result_alpha = [(word, count) for word, count in result if word.isalpha()]

        self.assertEqual(result_alpha, [])

    def test_word_frequency_endpoint_empty_topic(self):
        # Test the /word_frequency endpoint with an empty topic
        response = self.app.get('/word_frequency?topic=&n=5')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_word_frequency_endpoint_negative_n(self):
        # Test the /word_frequency endpoint with a negative value for n
        response = self.app.get('/word_frequency?topic=Python&n=-1')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_word_frequency_endpoint_non_integer_n(self):
        # Test the /word_frequency endpoint with a non-integer value for n
        response = self.app.get('/word_frequency?topic=Python&n=invalid')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_search_history_endpoint_no_entries(self):
        # Test the /search_history endpoint when there are no entries in the database
        response = self.app.get('/search_history')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('search_history', data)
        self.assertEqual(len(data['search_history']), 0)

    def test_search_history_endpoint_with_entries(self):
        # Test the /search_history endpoint when there are entries in the database
        # Add a search history entry for testing
        with app.app_context():
            entry = SearchHistory(topic='TestTopic', top_words='TestWords')
            db.session.add(entry)
            db.session.commit()

        response = self.app.get('/search_history')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('search_history', data)
        self.assertEqual(len(data['search_history']), 1)
        self.assertEqual(data['search_history'][0]['topic'], 'TestTopic')
        self.assertEqual(data['search_history'][0]['top_words'], 'TestWords')

    def test_fetch_wikipedia_data_missing_page(self):
        # Test the fetch_wikipedia_data function with a topic that has a missing page
        result = fetch_wikipedia_data('NonExistentTopic')

        self.assertIsNotNone(result)
        self.assertIn('query', result)
        self.assertIn('pages', result['query'])
        self.assertIn('-1', result['query']['pages'])
        self.assertIn('missing', result['query']['pages']['-1'])
        self.assertEqual(result['query']['pages']['-1']['missing'], '')

if __name__ == '__main__':
    unittest.main()
