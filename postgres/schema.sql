-- 1) ENUM type for borrow state (only two values)
CREATE TYPE b_state AS ENUM ('Present', 'Borrowed');
-- Present is the default state for books.

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

--- Association Tables ---
-- Contain foreign keys(composite primary keys) to establish many-to-many relationships.
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
--- End of Association Tables ---

-- Borrow table
CREATE TABLE Borrow (
    book_id INT REFERENCES Book(id) ON DELETE CASCADE,
    customer_id INT REFERENCES Customer(id) ON DELETE CASCADE,
    borrowed_on DATE NOT NULL,
    return_date DATE,
    borrow_state b_state NOT NULL DEFAULT 'Present',
    -- The state is set to 'Present' by default when a book is added to the library.
    PRIMARY KEY (book_id, customer_id, borrowed_on)
);
