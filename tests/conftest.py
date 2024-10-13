import sys
import os

 # Add the project root directory to Python's module search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from arxiv_sns_proto import create_app
from arxiv_sns_proto.db import init_db

def get_test_db_url():
    # Get the main database URL from environment variable or use default
    main_db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/postgres')
    
    # Parse the URL to get components
    from urllib.parse import urlparse
    url = urlparse(main_db_url)
    
    # Create a new database name for testing
    db_name = f"test_{url.path.strip('/') or 'arxiv_sns_proto'}"
    
    # Construct the test database URL
    test_db_url = f"{url.scheme}://{url.netloc}/{db_name}"
    return main_db_url, test_db_url, db_name

def create_test_db(main_db_url, test_db_name):
    conn = psycopg2.connect(main_db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {test_db_name}")
    cur.close()
    conn.close()

def drop_test_db(main_db_url, test_db_name):
    conn = psycopg2.connect(main_db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cur.close()
    conn.close()

@pytest.fixture(scope='session')
def app():
    main_db_url, test_db_url, test_db_name = get_test_db_url()
    
    # Drop the test database if it exists (in case of previous test failure)
    drop_test_db(main_db_url, test_db_name)
    
    # Create the test database
    create_test_db(main_db_url, test_db_name)
    
    # Set the DATABASE_URL to the test database
    os.environ['DATABASE_URL'] = test_db_url
    
    app = create_app({'TESTING': True})
    
    with app.app_context():
        init_db()
    
    yield app
    
    # After all tests, drop the test database
    drop_test_db(main_db_url, test_db_name)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
