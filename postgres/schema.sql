-- Authors table
CREATE TABLE Author (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Publishers table
CREATE TABLE Publisher (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Genres table
CREATE TABLE Genre (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Customers table
CREATE TABLE Customer (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Books table
CREATE TABLE Book (
    id SERIAL PRIMARY KEY,
    isbn TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL
);

-- BookAuthor (many-to-many)
CREATE TABLE BookAuthor (
    book_id INT REFERENCES Book(id) ON DELETE CASCADE,
    author_id INT REFERENCES Author(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

-- BookPublisher (many-to-many)
CREATE TABLE BookPublisher (
    book_id INT REFERENCES Book(id) ON DELETE CASCADE,
    publisher_id INT REFERENCES Publisher(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, publisher_id)
);

-- BookGenre (many-to-many)
CREATE TABLE BookGenre (
    book_id INT REFERENCES Book(id) ON DELETE CASCADE,
    genre_id INT REFERENCES Genre(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);

-- Borrow table
CREATE TABLE Borrow (
    book_id INT REFERENCES Book(id) ON DELETE CASCADE,
    customer_id INT REFERENCES Customer(id) ON DELETE CASCADE,
    borrowed_on DATE NOT NULL,
    return_date DATE,
    state TEXT,
    PRIMARY KEY (book_id, customer_id, borrowed_on)
);
