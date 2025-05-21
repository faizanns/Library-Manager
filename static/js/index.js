window.onload = function () {
    // Fetch books data from the backend API
    fetch('http://localhost:8000/api/books')
        .then(res => res.json())
        .then(booksData => {
            const bookTable = document.getElementById('book-table');
            const borrowBookSelect = document.getElementById('borrowBookId');
            const returnBookSelect = document.getElementById('returnBookId');

            // Clear existing rows (there's no header row inside tbody)
            bookTable.innerHTML = '';

            console.log(booksData)

            // Reset dropdowns
            borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
            returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

            booksData.forEach(book => {
                const id = book.id;
                const title = book.title || 'Unknown Title';

                // Safely join arrays or show 'Unknown'
                const authors = Array.isArray(book.authors) && book.authors.length > 0 
                    ? book.authors.join(', ') : 'Unknown';

                const publishers = (Array.isArray(book.publishers) && book.publishers.length > 0) 
                ? book.publishers.join(', ') 
                : (typeof book.publishers === 'string' && book.publishers.trim() !== '' ? book.publishers : 'Unknown');


                const genres = Array.isArray(book.genres) && book.genres.length > 0 
                    ? book.genres.join(', ') : 'Unknown';

                const borrower = book.borrower || '';
                const borrowedOn = book.borrowed_on || '';
                const returnDate = book.return_date || '';
                const state = book.state || 'Present';

                // Create a table row for the book
                const row = document.createElement('tr');
                row.setAttribute('data-id', id);

                row.innerHTML = `
                    <td>${id}</td>
                    <td>${title}</td>
                    <td>${authors}</td>
                    <td>${publishers}</td>
                    <td>${genres}</td>
                    <td>${borrower}</td>
                    <td>${borrowedOn ? borrowedOn.split('T')[0] : ''}</td>
                    <td>${returnDate ? returnDate.split('T')[0] : ''}</td>
                    <td>${state}</td>
                `;

                if (state.toLowerCase() === 'borrowed') {
                    row.classList.add('borrowed');
                }

                bookTable.appendChild(row);

                // Add options to dropdowns depending on book state
                const option = document.createElement('option');
                option.value = id;
                option.textContent = `${id} - ${title}`;

                if (state.toLowerCase() === 'present') {
                    borrowBookSelect.appendChild(option);
                } else {
                    returnBookSelect.appendChild(option);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching books data:', error);
            alert('Failed to load books data. Please try again later.');
        });
};

// Borrow Book Form Handler
document.getElementById('borrowForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const bookId = document.getElementById('borrowBookId').value;
    const borrowerName = document.getElementById('borrowerName').value.trim();
    const borrowDate = document.getElementById('borrowDate').value;

    if (!bookId || !borrowerName || !borrowDate) {
        alert('Please fill in all fields.');
        return;
    }

    // Calculate return date +3 months from borrowDate
    const returnDate = new Date(borrowDate);
    returnDate.setMonth(returnDate.getMonth() + 3);

    if (!confirm(`Are you sure you want to borrow Book ID ${bookId}?`)) {
        return;
    }

    const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
    if (!row) {
        alert('No book found with that ID.');
        return;
    }

    if (row.cells[8].textContent.toLowerCase() === 'borrowed') {
        alert('This book is already borrowed.');
        return;
    }

    fetch('http://localhost:8000/api/borrow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: parseInt(bookId),
            customer: borrowerName,
            borrowed_on: borrowDate,
            return_date: returnDate.toISOString().split('T')[0]  // Send ISO date string (YYYY-MM-DD)
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to borrow book');
        return response.json();
    })
    .then(() => {
        alert(`Book ID ${bookId} has been successfully borrowed.`);
        document.getElementById('borrowForm').reset();
        location.reload();
    })
    .catch(error => {
        console.error('Error borrowing book:', error);
        alert('Failed to borrow the book. Please try again.');
    });
});

// Return Book Form Handler
document.getElementById('returnForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const bookId = document.getElementById('returnBookId').value;
    const returnDateInput = document.getElementById('returnDate').value;

    if (!bookId || !returnDateInput) {
        alert('Please fill in all fields.');
        return;
    }

    if (!confirm(`Are you sure you want to return Book ID ${bookId}?`)) {
        return;
    }

    const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
    if (!row) {
        alert('No book found with that ID.');
        return;
    }

    if (row.cells[8].textContent.toLowerCase() !== 'borrowed') {
        alert('This book is not currently borrowed.');
        return;
    }

    fetch('http://localhost:8000/api/return', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: parseInt(bookId),
            returned_on: returnDateInput
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to return book');
        return response.json();
    })
    .then(() => {
        alert(`Book ID ${bookId} has been successfully returned.`);
        document.getElementById('returnForm').reset();
        location.reload();
    })
    .catch(error => {
        console.error('Error returning book:', error);
        alert('Failed to return the book. Please try again.');
    });
});

// Clear borrowing data
document.getElementById('clearDataBtn').addEventListener('click', function () {
    if (confirm('Are you sure you want to clear all borrowing data? This action cannot be undone.')) {
        fetch('http://localhost:8000/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to clear data');
            return response.json();
        })
        .then(() => {
            alert('All borrowing data has been cleared.');
            location.reload();
        })
        .catch(error => {
            console.error('Error clearing data:', error);
            alert('Failed to clear data. Please try again.');
        });
    }
});

