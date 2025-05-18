# Library Manager
Basic Library Management System 

### Steps
1. Open cmd/terminal and clone the repository (ensure git is installed or use GutHub Desktop)
```bash
git clone https://github.com/clumsyspeedboat/library_management_task.git
```
2. "cd" into the repository
```bash
cd <path_to_your_dir>/library_management_task
```
3. Create virtual environment (ensure python is installed and added to PATH)
```bash
python -m venv env
```
4. Activate virtual environment
```bash
env\Scripts\activate # on Windows
source env/bin/activate # on Linux/Mac
```
5. Install dependencies/packages
```bash
pip install -r requirements.txt
```
5. Run Flask app
```bash
python app.py
```
6. Navigate to localhost (port will be displayed in terminal)
```bash
http://localhost:5000 # Most probably
```
---
### Task 2 till 4 documentation
 - The books can now have multiple genres, authors, and publishers. 2 examples of this already exist in the database.
 - An ENUM is used to define possible states of borrow("Present" and "Borrowed") with a default state of "Present". Because the borrow is not defined at time of adding books to the database, the state is null. This is changed to "Present" in app.py using SQL COALESCE function.
 - Association tables are created to define many-to-many relations between entities
 - The assiciation tables use foreign keys to form composite primary keys
 - The borrow entry id deleted when the book is successfully returned

### Possible imporovements
- Adding a separate state attribute the the book, so that the state of the book and the borrow can be independently used.
- The above change would allow to keep the borrow records even after the book is returned. This way, a history of the borrows can be maintained which can then be used for other purposes.
