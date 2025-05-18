# from flask import Flask, render_template, jsonify, request
# import configparser
# import requests
# import logging
# from flask_cors import CORS

# app = Flask(__name__, static_url_path='/static', static_folder='static')
# CORS(app)

# # Configure logging to DEBUG level for detailed logs
# logging.basicConfig(
#     level=logging.DEBUG,  # Changed from INFO to DEBUG
#     format='%(asctime)s %(levelname)s %(message)s',
#     handlers=[
#         logging.StreamHandler()
#     ]
# )

# # Load the configuration from the config.ini file
# config = configparser.ConfigParser()
# config.read('config.ini')

# # Get the API key and URL from the configuration
# try:
#     GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
#     GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
#     logging.info("Gemini API configuration loaded successfully.")
# except Exception as e:
#     logging.error("Error reading config.ini: %s", e)
#     GEMINI_API_KEY = None
#     GEMINI_API_URL = None

# # Route to serve the home page
# @app.route('/')
# def home():
#     return render_template('index.html')

# # Route to serve viewer.html
# @app.route('/viewer.html')
# def viewer():
#     return render_template('viewer.html')

# # API route to fetch description from Gemini API
# @app.route('/api/description', methods=['GET'])
# def get_description():
#     entity_name = request.args.get('name')
#     logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

#     if not entity_name:
#         logging.warning("Missing entity name in request.")
#         return jsonify({'error': 'Missing entity name'}), 400

#     if not GEMINI_API_URL or not GEMINI_API_KEY:
#         logging.error("Gemini API configuration missing.")
#         return jsonify({'error': 'Server configuration error'}), 500

#     # Prepare the JSON payload with explicit instructions
#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": (
#                             f"Provide a detailed description of '{entity_name}'"
#                             "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
#                             "Do not include any concluding remarks or questions."
#                             "Do not mention any Note at the end about not including concluding remarks or questions."
#                         )
#                     }
#                 ]
#             }
#         ]
#     }

#     # Construct the API URL with the API key as a query parameter
#     api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

#     headers = {
#         "Content-Type": "application/json"
#     }

#     # Log the API URL and payload for debugging
#     logging.debug(f"API URL: {api_url_with_key}")
#     logging.debug(f"Payload: {payload}")

#     try:
#         # Make the POST request to the Gemini API
#         response = requests.post(
#             api_url_with_key,  # Include the API key in the URL
#             headers=headers,
#             json=payload,
#             timeout=10  # seconds
#         )
#         logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

#         if response.status_code != 200:
#             logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
#             logging.error(f"Response content: {response.text}")
#             return jsonify({
#                 'error': 'Failed to fetch description from Gemini API',
#                 'status_code': response.status_code,
#                 'response': response.text
#             }), 500

#         response_data = response.json()
#         # Extract the description from the response
#         description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
#         logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

#         return jsonify({'description': description})

#     except requests.exceptions.RequestException as e:
#         logging.error(f"Exception during Gemini API request: {e}")
#         return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
#     except ValueError as e:
#         logging.error(f"JSON decoding failed: {e}")
#         return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
#     except Exception as e:
#         logging.exception(f"Unexpected error: {e}")
#         return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, jsonify, request, abort, render_template
from flask_cors import CORS
import psycopg2
import os
import time

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

def connect_to_db(retries=10, delay=3):
    for i in range(retries):
        try:
            return psycopg2.connect(
                dbname="library_db",
                user="library_user",
                password="library_pass",
                host="localhost",
                port=5432,
            )
        except psycopg2.OperationalError as e:
            print(f"Database not ready (attempt {i+1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to the database after multiple attempts")

conn = connect_to_db()


@app.route('/api/books', methods=['GET'])
def get_books():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                Book.id,
                Book.title,
                    
                -- Aggregate distinct authors for the book into an array
                array_agg(DISTINCT Author.name) AS authors,
                    
                -- Aggregate distinct publishers for the book
                array_agg(DISTINCT Publisher.name) AS publishers,
                    
                -- Aggregate distinct genres for the book
                array_agg(DISTINCT Genre.name) AS genres,
                    
                -- Borrower name (if any)
                Customer.name AS borrower,
                Borrow.borrowed_on,
                Borrow.return_date,
                    
                -- If borrow_state is NULL (never borrowed), treat as 'Present'
                COALESCE(Borrow.borrow_state, 'Present') AS borrow_state
                    
            FROM Book
            -- Join authors via BookAuthor junction table
            LEFT JOIN BookAuthor ON BookAuthor.book_id = Book.id
            LEFT JOIN Author ON Author.id = BookAuthor.author_id

            -- Join publishers via BookPublisher junction table
            LEFT JOIN BookPublisher ON BookPublisher.book_id = Book.id
            LEFT JOIN Publisher ON Publisher.id = BookPublisher.publisher_id

            -- Join genres via BookGenre junction table
            LEFT JOIN BookGenre ON BookGenre.book_id = Book.id
            LEFT JOIN Genre ON Genre.id = BookGenre.genre_id

            -- Join borrow info
            LEFT JOIN Borrow ON Borrow.book_id = Book.id
            LEFT JOIN Customer ON Customer.id = Borrow.customer_id

            GROUP BY
                Book.id,
                Book.title,
                Customer.name,
                Borrow.borrowed_on,
                Borrow.return_date,
                Borrow.borrow_state

            ORDER BY Book.id;
        """)
        books = []
        for r in cur.fetchall():
            books.append({
                'id': r[0],
                'title': r[1],
                'authors': r[2] or [],
                'publishers': r[3] or [],
                'genres': r[4] or [],
                'borrower': r[5],
                'borrowed_on': r[6].isoformat() if r[6] else None,
                'return_date': r[7].isoformat() if r[7] else None,
                'state': r[8]
            })
        return jsonify(books)


@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json() or {}
    book_id = data.get('book_id')
    customer = data.get('customer')
    borrowed_on = data.get('borrowed_on')
    return_date = data.get('return_date')
    if not all([book_id, customer, borrowed_on, return_date]):
        abort(400, 'Missing required fields')
    with conn.cursor() as cur:
        # create or fetch customer
        # we assume customer name is unique
        cur.execute("SELECT id FROM Customer WHERE name = %s", (customer,))
        row = cur.fetchone()
        if row:
            cust_id = row[0]
        else:
            # customer does not exist, create a new one
            cur.execute("INSERT INTO Customer (name) VALUES (%s) RETURNING id", (customer,))
            cust_id = cur.fetchone()[0]
        # Insert new borrow record
        cur.execute(
            """
            INSERT INTO Borrow (book_id, customer_id, borrowed_on, return_date, borrow_state)
            VALUES (%s, %s, %s, %s, 'Borrowed')
            """,
            (book_id, cust_id, borrowed_on, return_date)
        )
        conn.commit()
    return jsonify({'message': 'Book borrowed'}), 201


@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json() or {}
    book_id = data.get('book_id')
    returned_on = data.get('returned_on')
    if not all([book_id, returned_on]):
        abort(400, 'Missing required fields')
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM Borrow
            WHERE book_id = %s AND borrow_state = 'Borrowed'
            """,
            (book_id,)
        )
        if cur.rowcount == 0:
            abort(404, 'No active borrow record found for this book')
        conn.commit()
    return jsonify({'message': 'Book returned'})


@app.route('/api/clear', methods=['POST'])
def clear_borrows():
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Borrow;")
        conn.commit()
    return jsonify({'message': 'All borrow records cleared'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
