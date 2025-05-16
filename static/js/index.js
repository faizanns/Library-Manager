window.onload = function () {
    // Fetch all JSON data concurrently
    Promise.all([
        fetch('http://localhost:8000/api/authors').then(res => res.json()),
        fetch('http://localhost:8000/api/publishers').then(res => res.json()),
        fetch('http://localhost:8000/api/books').then(res => res.json()),
        fetch('http://localhost:8000/api/genres').then(res => res.json()),
        fetch('http://localhost:8000/api/borrowings').then(res => res.json())
    ]).then(([authorsData, publishersData, booksData, genresData]) => {
        const authors = {};
        authorsData.forEach(author => {
            authors[author.id] = author.name;
        });

        const publishers = {};
        publishersData.forEach(publisher => {
            publishers[publisher.id] = publisher.name;
        });

        const genres = {};
        genresData.forEach(genre => {
            genres[genre.id] = genre.name;
        });

        const bookTable = document.getElementById('book-table');
        const borrowBookSelect = document.getElementById('borrowBookId');
        const returnBookSelect = document.getElementById('returnBookId');

        // Retrieve borrowing data from LocalStorage
        const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};

        // Clear existing table rows except header
        while (bookTable.rows.length > 1) {
            bookTable.deleteRow(1);
        }

        // Clear dropdown options
        borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
        returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

        booksData.forEach(book => {
            const id = book.id;
            const title = book.title;

            const authorName = authors[book.author_id] || 'Unknown';
            const publisherName = publishers[book.publisher_id] || 'Unknown';
            const genreName = genres[book.genre_id] || 'Unknown';

            const row = document.createElement('tr');
            row.setAttribute('data-id', id);

            const isBorrowed = borrowingData[id] ? true : false;

            row.innerHTML = `<td>${id}</td>
                             <td>${title}</td>
                             <td>${authorName}</td>
                             <td>${publisherName}</td>
                             <td>${genreName}</td>
                             <td>${isBorrowed ? borrowingData[id].borrowerName : ''}</td>
                             <td>${isBorrowed ? borrowingData[id].borrowDate : ''}</td>
                             <td>${isBorrowed ? borrowingData[id].returnDate : ''}</td>
                             <td>${isBorrowed ? 'Borrowed' : 'Present'}</td>`;

            if (isBorrowed) row.classList.add('borrowed');
            bookTable.appendChild(row);

            const option = document.createElement('option');
            option.value = id;
            option.textContent = `${id} - ${title}`;
            if (!isBorrowed) borrowBookSelect.appendChild(option);
            else returnBookSelect.appendChild(option);
        });
    }).catch(error => {
        console.error('Error fetching or processing JSON data:', error);
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

    if (!confirm(`Are you sure you want to borrow Book ID ${bookId}?`)) {
        return;
    }

    const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
    if (!row) {
        alert('No book found with that ID.');
        return;
    }

    if (row.cells[8].textContent === 'Borrowed') {
        alert('This book is already borrowed.');
        return;
    }

    const returnDate = new Date(borrowDate);
    returnDate.setMonth(returnDate.getMonth() + 3);

    // Update row
    row.cells[5].textContent = borrowerName;
    row.cells[6].textContent = borrowDate;
    row.cells[7].textContent = returnDate.toISOString().split('T')[0];
    row.cells[8].textContent = 'Borrowed';
    row.classList.add('borrowed');

    const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
    borrowingData[bookId] = {
        borrowerName: borrowerName,
        borrowDate: borrowDate,
        returnDate: returnDate.toISOString().split('T')[0]
    };
    localStorage.setItem('borrowingData', JSON.stringify(borrowingData));

    // Update dropdowns
    const borrowBookSelect = document.getElementById('borrowBookId');
    const optionToRemove = borrowBookSelect.querySelector(`option[value="${bookId}"]`);
    if (optionToRemove) optionToRemove.remove();

    const returnBookSelect = document.getElementById('returnBookId');
    const newOption = document.createElement('option');
    newOption.value = bookId;
    newOption.textContent = `${bookId} - ${row.cells[1].textContent}`;
    returnBookSelect.appendChild(newOption);

    document.getElementById('borrowForm').reset();
    alert(`Book ID ${bookId} has been successfully borrowed.`);
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

    if (row.cells[8].textContent !== 'Borrowed') {
        alert('This book is not currently borrowed.');
        return;
    }

    row.cells[5].textContent = '';
    row.cells[6].textContent = '';
    row.cells[7].textContent = '';
    row.cells[8].textContent = 'Present';
    row.classList.remove('borrowed');

    const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
    if (borrowingData[bookId]) {
        delete borrowingData[bookId];
        localStorage.setItem('borrowingData', JSON.stringify(borrowingData));
    }

    const returnBookSelect = document.getElementById('returnBookId');
    const optionToRemove = returnBookSelect.querySelector(`option[value="${bookId}"]`);
    if (optionToRemove) optionToRemove.remove();

    const borrowBookSelect = document.getElementById('borrowBookId');
    const newOption = document.createElement('option');
    newOption.value = bookId;
    newOption.textContent = `${bookId} - ${row.cells[1].textContent}`;
    borrowBookSelect.appendChild(newOption);

    document.getElementById('returnForm').reset();
    alert(`Book ID ${bookId} has been successfully returned.`);
});

// Clear borrowing data
document.getElementById('clearDataBtn').addEventListener('click', function () {
    if (confirm('Are you sure you want to clear all borrowing data? This action cannot be undone.')) {
        localStorage.removeItem('borrowingData');
        location.reload();
    }
});
