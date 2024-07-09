import psycopg2

db_params = {
    'database': 'lesson6',
    'user': 'postgres',
    'password': 'smth',
    'host': 'localhost',
    'port': 5432
}


class DBConnect:
    def __init__(self, db_params):
        self.db_params = db_params

    def __enter__(self):
        self.conn = psycopg2.connect(**self.db_params)
        self.cur = self.conn.cursor()
        return self.conn, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


class Book:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def create(self, title, author, description):
        create_query = '''
        INSERT INTO book (title, author, description) VALUES (%s, %s, %s)
        RETURNING id;
        '''
        self.cur.execute(create_query, (title, author, description))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def read(self, book_id):
        read_query = '''SELECT * FROM book WHERE id = %s;'''
        self.cur.execute(read_query, (book_id,))
        return self.cur.fetchone()

    def update(self, book_id, title=None, author=None, description=None):
        update_query = '''UPDATE book SET '''
        fields = []
        values = []

        if title:
            fields.append('title = %s')
            values.append(title)
        if author:
            fields.append('author = %s')
            values.append(author)
        if description:
            fields.append('description = %s')
            values.append(description)

        update_query += ', '.join(fields) + ' WHERE id = %s;'
        values.append(book_id)

        self.cur.execute(update_query, tuple(values))
        self.conn.commit()

    def delete(self, book_id):
        delete_query = '''DELETE FROM book WHERE id = %s;'''
        self.cur.execute(delete_query, (book_id,))
        self.conn.commit()


# Context manager yordamida CRUD operatsiyalarini bajarish
with DBConnect(db_params) as (conn, cur):
    book_manager = Book(conn, cur)

    # Create
    new_book_id = book_manager.create("New Book", "John Doe", "A description of the new book")
    print(f"New book created with ID: {new_book_id}")

    # Read
    book = book_manager.read(new_book_id)
    print(f"Book read from database: {book}")

    # Update
    book_manager.update(new_book_id, description="An updated description")
    updated_book = book_manager.read(new_book_id)
    print(f"Book after update: {updated_book}")

    # Delete
    book_manager.delete(new_book_id)
    deleted_book = book_manager.read(new_book_id)
    print(f"Book after deletion (should be None): {deleted_book}")
