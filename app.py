from flask import Flask, jsonify, request, abort, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
import psycopg2
from pymongo.errors import ConnectionFailure
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Determine which database to use
DB_TYPE = os.getenv("DB_TYPE", "mongodb").lower()

conn = None

if DB_TYPE == 'mongodb':
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("Error: MONGODB_URI not set.")
        exit(1)

    app.config["MONGO_URI"] = mongo_uri
    # mongo.init_app(app)
    mongo = PyMongo(app)

    with app.app_context():
        try:
            mongo.cx.admin.command('ping')
            print("MongoDB connection successful.")
            print(f"Connected to MongoDB database: {mongo.cx.name}")
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            exit(1)
        except Exception as e:
            print(f"Unexpected error during MongoDB connection: {e}")
            exit(1)

elif DB_TYPE == 'postgres':
    def connect_to_postgres_db(retries=10, delay=3):
        for i in range(retries):
            try:
                return psycopg2.connect(
                    dbname=os.getenv("PG_DBNAME", "library_db"),
                    user=os.getenv("PG_USER", "library_user"),
                    password=os.getenv("PG_PASSWORD", "library_pass"),
                    host=os.getenv("PG_HOST", "localhost"),
                    port=os.getenv("PG_PORT", 5432),
                )
            except psycopg2.OperationalError as e:
                print(f"PostgreSQL not ready (attempt {i+1}): {e}")
                time.sleep(delay)
        raise Exception("Failed to connect to PostgreSQL after multiple attempts")

    try:
        conn = connect_to_postgres_db()
        print("PostgreSQL connection successful.")
    except Exception as e:
        print(e)
        exit(1)
else:
    print(f"Invalid DB_TYPE: {DB_TYPE}")
    exit(1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    if DB_TYPE == 'postgres':
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    Book.id,
                    Book.title,
                    array_agg(DISTINCT Author.name) AS authors,
                    array_agg(DISTINCT Publisher.name) AS publishers,
                    array_agg(DISTINCT Genre.name) AS genres,
                    Customer.name AS borrower,
                    Borrow.borrowed_on,
                    Borrow.return_date,
                    COALESCE(Borrow.borrow_state, 'Present') AS borrow_state
                FROM Book
                LEFT JOIN BookAuthor ON BookAuthor.book_id = Book.id
                LEFT JOIN Author ON Author.id = BookAuthor.author_id
                LEFT JOIN BookPublisher ON BookPublisher.book_id = Book.id
                LEFT JOIN Publisher ON Publisher.id = BookPublisher.publisher_id
                LEFT JOIN BookGenre ON BookGenre.book_id = Book.id
                LEFT JOIN Genre ON Genre.id = BookGenre.genre_id
                LEFT JOIN Borrow ON Borrow.book_id = Book.id
                LEFT JOIN Customer ON Customer.id = Borrow.customer_id
                GROUP BY Book.id, Book.title, Customer.name,
                         Borrow.borrowed_on, Borrow.return_date, Borrow.borrow_state
                ORDER BY Book.id;
            """)
            books = [{
                'id': r[0],
                'title': r[1],
                'authors': r[2] or [],
                'publishers': r[3] or [],
                'genres': r[4] or [],
                'borrower': r[5],
                'borrowed_on': r[6].isoformat() if r[6] else None,
                'return_date': r[7].isoformat() if r[7] else None,
                'state': r[8]
            } for r in cur.fetchall()]
            return jsonify(books)

    elif DB_TYPE == 'mongodb':
        books_data = list(mongo.db.books.aggregate([
            {'$lookup': {
                'from': 'authors', 'localField': 'author_ids',
                'foreignField': '_id', 'as': 'authors_info'}},
            {'$lookup': {
                'from': 'publishers', 'localField': 'publisher_id',
                'foreignField': '_id', 'as': 'publisher_info'}},
            {'$lookup': {
                'from': 'genres', 'localField': 'genre_ids',
                'foreignField': '_id', 'as': 'genres_info'}},
            {'$lookup': {
                'from': 'borrows', 'localField': '_id',
                'foreignField': 'book_id', 'as': 'borrow_records'}},
            {'$addFields': {
                'current_borrow': {'$arrayElemAt': [
                    {'$filter': {
                        'input': '$borrow_records',
                        'as': 'br',
                        'cond': {'$eq': ['$$br.borrow_state', 'Borrowed']}
                    }}, 0]}},
            },
            {'$lookup': {
                'from': 'customers',
                'localField': 'current_borrow.customer_id',
                'foreignField': '_id',
                'as': 'borrower_info'}},
            {'$project': {
                '_id': 0,
                'id': '$_id',
                'title': 1,
                'authors': '$authors_info.name',
                'publishers': {'$arrayElemAt': ['$publisher_info.name', 0]},
                'genres': '$genres_info.name',
                'borrower': {'$arrayElemAt': ['$borrower_info.name', 0]},
                'borrowed_on': '$current_borrow.borrowed_on',
                'return_date': '$current_borrow.return_date',
                'state': {
                    '$cond': {
                        'if': {'$eq': ['$current_borrow.borrow_state', 'Borrowed']},
                        'then': 'Borrowed',
                        'else': 'Present'
                    }
                }
            }},
            {'$sort': {'id': 1}}
        ]))

        for book in books_data:
            if isinstance(book.get('borrowed_on'), datetime):
                book['borrowed_on'] = book['borrowed_on'].isoformat()
            if isinstance(book.get('return_date'), datetime):
                book['return_date'] = book['return_date'].isoformat()
        return jsonify(books_data)

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json() or {}
    book_id = data.get('book_id')
    customer_name = data.get('customer')
    borrowed_on = data.get('borrowed_on')
    return_date = data.get('return_date')

    if not all([book_id, customer_name, borrowed_on, return_date]):
        abort(400, 'Missing required fields.')

    if DB_TYPE == 'postgres':
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM Customer WHERE name = %s", (customer_name,))
            row = cur.fetchone()
            if row:
                cust_id = row[0]
            else:
                cur.execute("INSERT INTO Customer (name) VALUES (%s) RETURNING id", (customer_name,))
                cust_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO Borrow (book_id, customer_id, borrowed_on, return_date, borrow_state)
                VALUES (%s, %s, %s, %s, 'Borrowed')
            """, (book_id, cust_id, borrowed_on, return_date))
            conn.commit()
        return jsonify({'message': 'Book borrowed successfully (PostgreSQL)'}), 201

    elif DB_TYPE == 'mongodb':
        books = mongo.db.books
        customers = mongo.db.customers
        borrows = mongo.db.borrows

        if not books.find_one({"_id": book_id}):
            abort(404, 'Book not found.')

        customer = customers.find_one({"name": customer_name})
        if not customer:
            latest = customers.find_one(sort=[("_id", -1)])
            new_id = (latest["_id"] + 1) if latest else 1
            customers.insert_one({"_id": new_id, "name": customer_name})
            cust_id = new_id
        else:
            cust_id = customer["_id"]

        latest_borrow = borrows.find_one(sort=[("_id", -1)])
        new_borrow_id = (latest_borrow["_id"] + 1) if latest_borrow else 1

        borrows.insert_one({
            "_id": new_borrow_id,
            "book_id": book_id,
            "customer_id": cust_id,
            "borrowed_on": borrowed_on,
            "return_date": return_date,
            "borrow_state": "Borrowed"
        })
        return jsonify({'message': 'Book borrowed successfully (MongoDB)'}), 201

@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json() or {}
    book_id = data.get('book_id')

    if not book_id:
        abort(400, 'Missing required field: book_id')

    if DB_TYPE == 'postgres':
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Borrow WHERE book_id = %s AND borrow_state = 'Borrowed'", (book_id,))
            if cur.rowcount == 0:
                abort(404, 'No active borrow record found.')
            conn.commit()
        return jsonify({'message': 'Book returned successfully (PostgreSQL)'})

    elif DB_TYPE == 'mongodb':
        result = mongo.db.borrows.delete_one({"book_id": book_id, "borrow_state": "Borrowed"})
        if result.deleted_count == 0:
            abort(404, 'No active borrow record found.')
        return jsonify({'message': 'Book returned successfully (MongoDB)'})

@app.route('/api/clear', methods=['POST'])
def clear_borrows():
    if DB_TYPE == 'postgres':
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Borrow;")
            conn.commit()
        return jsonify({'message': 'All borrow records cleared (PostgreSQL)'})

    elif DB_TYPE == 'mongodb':
        result = mongo.db.borrows.delete_many({})
        return jsonify({'message': f'Cleared {result.deleted_count} borrow records (MongoDB)'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
