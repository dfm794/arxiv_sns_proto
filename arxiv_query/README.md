The arxiv_query module is a Python package that provides an interface to the arxiv API.

The file query_arxiv.py contains the ArxivQueryServer class which is a RabbitMQ server that can be used to query the arXiv API and a function arxiv_query which is a simple wrapper around the arxiv API that makes the actual query.

For the purposes of week3, we do not need to exercise the RabbitMQ server path (athough it is used in the project). Therefore, to accomplish the task for week3, we provide a simpler script direct_to_db.py which simply calls arxiv_query with the same parameters and writes the results to a SQLite database called arxiv_results.db in the same directory as the script is run from.

This exercises the needed functions for week3 do the following:

Assuming you have a recent version (>3.10)of python installed, install the dependencies with pip:
pip install urllib
pip install feedparser
pip install pika
pip install json
pip install sqlite3
pip install os

Then run the test:
python direct_to_db.py

The file direct_to_db.py contains a series of test queries that can be used to test the arxiv_query function.
The results are stored in a SQLite database called arxiv_results.db and maintaned in the same directory as the direct_to_db.py file is run from, as stated above.

Since the arXiv API limits requests to once every 3 seconds, the code in direct_to_db.py pauses for 4 seconds between each request.


The expected output of the test is (however, the exact titles may vary):
Test Query 1:
Query: {'query_string': 'quantum computing', 'max_results': 5}
Number of results: 5
First result title: Pulse controlled noise suppressed quantum computation

Test Query 2:
Query: {'query_string': 'machine learning', 'start': 10, 'max_results': 3}
Number of results: 3
First result title: Proceedings of the 2016 ICML Workshop on #Data4Good: Machine Learning in
  Social Good Applications

Test Query 3:
Query: {'query_string': 'artificial intelligence', 'max_results': 2}
Number of results: 2
First result title: The Governance of Physical Artificial Intelligence

All tests passed successfully!
Results have been stored in the 'arxiv_results.db' SQLite database.

After the test has completed, the server can be closed with CTRL+C.


Note that it can take a while to run the test (up to a few minutes), so be patient.


While not needed for week 3, the project accesses Arxiv over RabbitMQ. If you would like to exercise this, you can do so by ensuring a RabbitMQ message broker is running on your localhost (the host the tests are running on) and then running the following commands

To launch the server:
python query_arxiv.py

Then run the test in a separate terminal:

python server_to_db.py

The server will emit
ArxivQueryServer is waiting for requests...

The expected output of the test is the same as the direct_to_db.py test.

