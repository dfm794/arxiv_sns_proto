The arxiv_query module is a Python package that provides an interface to the arxiv API.

The file query_arxiv.py contains the ArxivQueryServer class, which is a RabbitMQ server that can be used to query the arXiv API.

The file test.py contains a series of test queries that can be used to test the ArxivQueryServer class.
The results are stored in a SQLite database called arxiv_results.db and maintaned in the same directory as the test.py file is run from.

Since the arXiv API limits requests to once every 3 seconds, the code in test.py pauses for 4 seconds between each request.

As the test and the server communicate using RabbitMQ, RabbitMQ must be installed and running the machine where this code is executed. (the code can be altered to run accross machines, but by default runs on the localhost)

To demonstrate the use of the ArxivQueryServer class, first run the server:

python query_arxiv.py

Then run the test in a separate terminal:

python test.py

The server will emit
ArxivQueryServer is waiting for requests...

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