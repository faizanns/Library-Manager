-- Authors
INSERT INTO Author (name) VALUES ('J.K. Rowling'), ('George Orwell');

-- Publishers
INSERT INTO Publisher (name) VALUES ('Bloomsbury'), ('Penguin');

-- Genres
INSERT INTO Genre (name) VALUES ('Fantasy'), ('Dystopian');

-- Customers
INSERT INTO Customer (name) VALUES ('Alice'), ('Bob');

-- Books
INSERT INTO Book (isbn, title) VALUES ('1234567890', 'Harry Potter'), ('9876543210', '1984');

-- BookAuthor
INSERT INTO BookAuthor VALUES (1, 1), (2, 2);

-- BookPublisher
INSERT INTO BookPublisher VALUES (1, 1), (2, 2);

-- BookGenre
INSERT INTO BookGenre VALUES (1, 1), (2, 2);

-- Borrow
INSERT INTO Borrow VALUES (1, 1, '2024-05-01', '2024-05-10', 'Returned');
