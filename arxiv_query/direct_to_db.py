import time
import sqlite3
from query_arxiv import arxiv_query
def test_arxiv_query_server():


    # Create SQLite connection and cursor
    db_conn = sqlite3.connect('arxiv_results.db')
    db_cursor = db_conn.cursor()

    # Create table if it doesn't exist
    db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS arxiv_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_string TEXT,
        max_results INTEGER,
        start INTEGER,
        title TEXT,
        authors TEXT,
        arxiv_url TEXT,
        pdf_url TEXT
    )
    ''')

    # Test queries
    test_queries = [
        {"query_string": "quantum computing", "max_results": 5},
        {"query_string": "machine learning", "start": 10, "max_results": 3},
        {"query_string": "artificial intelligence", "max_results": 2}
    ]

    responses = []

    for query in test_queries:
        response = arxiv_query(query['query_string'], query.get('start', 0), query['max_results'])
        responses.append(response)
        time.sleep(4)
      # Pause for 4 seconds between iterations

            
            # Store the response in the database
    for result in response:
        # Check if the title already exists
        db_cursor.execute('SELECT id FROM arxiv_results WHERE title = ?', (result['title'],))
        existing_entry = db_cursor.fetchone()
        if existing_entry:
            # Update the existing entry
            db_cursor.execute('''
            UPDATE arxiv_results SET
                query_string = ?, max_results = ?, start = ?, 
                authors = ?, arxiv_url = ?, pdf_url = ?
            WHERE title = ?
            ''', (
                query['query_string'],
                query.get('max_results', 10),
                query.get('start', 0),
                ', '.join(result['authors']),
                result['arxiv_url'],
                result['pdf_url'],
                result['title']
            ))
        else:
            # Insert a new entry
            db_cursor.execute('''
            INSERT INTO arxiv_results (
                query_string, max_results, start, title, authors, arxiv_url, pdf_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                query['query_string'],
                query.get('max_results', 10),
                query.get('start', 0),
                result['title'],
                ', '.join(result['authors']),
                result['arxiv_url'],
                result['pdf_url']
            ))
    db_conn.commit()


    db_conn.close()

    # Print and verify results
    for i, (query, response) in enumerate(zip(test_queries, responses)):
        print(f"\nTest Query {i + 1}:")
        print(f"Query: {query}")
        print(f"Number of results: {len(response)}")
        print(f"First result title: {response[0]['title']}")
        assert len(response) == query['max_results'], f"Expected {query['max_results']} results, got {len(response)}"

    print("\nAll tests passed successfully!")
    print("Results have been stored in the 'arxiv_results.db' SQLite database.")

if __name__ == "__main__":

    test_arxiv_query_server()
