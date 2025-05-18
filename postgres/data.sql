-- AUTHORS
INSERT INTO Author (name) VALUES 
    ('George Orwell'),             -- a1
    ('Harper Lee'),                -- a2
    ('Jane Austen'),               -- a3
    ('Francesc Miralles'),         -- a4
    ('Hector Garcia'),             -- a5
    ('Faizan Shaikh'),             -- a6
    ('Zain Anwar');                -- a7

-- PUBLISHERS
INSERT INTO Publisher (name) VALUES 
    ('Penguin Books'),             -- p1
    ('J.B. Lippincott & Co.'),     -- p2
    ('T. Egerton'),                -- p3
    ('Secker and Warburg'),        -- p4
    ('Penguin Life');              -- p5


-- GENRES
INSERT INTO Genre (name) VALUES 
    ('Fiction'),                   -- g1
    ('Non-Fiction'),              -- g2
    ('Romance'),                   -- g3
    ('Satire'),                    -- g4
    ('Self Help');                 -- g5

-- BOOKS
INSERT INTO Book (isbn, title) VALUES 
    ('1234567890', '1984'),                            -- b1
    ('1234567891', 'To Kill a Mockingbird'),           -- b2
    ('1234567892', 'Pride and Prejudice'),             -- b3
    ('1234567893', 'Animal Farm'),                     -- b4
    ('1234567894', 'Ikigai'),                          -- b5
    -- In this book, we cook with databases
    ('9999999999', 'Cooking DataBases');               -- b6

-- BOOKAUTHOR (book_id, author_id)
INSERT INTO BookAuthor VALUES 
    (1, 1),  -- 1984 - George Orwell
    (2, 2),  -- To Kill a Mockingbird - Harper Lee
    (3, 3),  -- Pride and Prejudice - Jane Austen
    (4, 1),  -- Animal Farm - George Orwell
    -- multple authors examples
    (5, 4),  -- Ikigai - Francesc Miralles
    (5, 5),  -- Ikigai - Hector Garcia
    -- Our cook book
    (6, 6),  -- Cooking DataBases - Faizan Shaikh
    (6, 7);  -- Cooking DataBases - Zain Anwar

-- BOOKPUBLISHER (book_id, publisher_id)
INSERT INTO BookPublisher VALUES 
    (1, 1),  -- 1984 - Penguin Books
    (2, 2),  -- To Kill a Mockingbird - J.B. Lippincott & Co.
    (3, 3),  -- Pride and Prejudice - T. Egerton
    (4, 4),  -- Animal Farm - Secker and Warburg
    (5, 5),  -- Ikigai - Penguin Life
    (6, 1);  -- Cooking DataBases - Penguin Books

-- BOOKGENRE (book_id, genre_id)
INSERT INTO BookGenre VALUES 
    (1, 1),  -- 1984 - Fiction
    (2, 1),  -- To Kill a Mockingbird - Fiction
    (3, 3),  -- Pride and Prejudice - Romance
    (4, 4),  -- Animal Farm - Satire
    (5, 5),  -- Ikigai - Self Help
    (6, 2);  -- Cooking DataBases - Fiction

-- CUSTOMERS
INSERT INTO Customer (name) VALUES 
    ('Alice'), 
    ('Bob');

-- BORROW (optional initial record)
-- Example: Alice borrowed Animal Farm on 2024-05-01, returned it on 2024-05-10
INSERT INTO Borrow (book_id, customer_id, borrowed_on, return_date, borrow_state)
VALUES
    (4, 1, '2024-02-01', '2024-05-01', 'Borrowed'),
    (2, 2, '2025-05-01', '2024-08-01', 'Borrowed');