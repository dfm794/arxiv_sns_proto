import urllib
import feedparser
import pika
import json

import os
import signal
import sys

#A class that will allow us to use the arxiv_query function via rabbitmq
#The class init finction with take a url that defauts to 'localhost', a query queue name
#that defaults to 'arxiv_query', and a result queue name that defaults to 'arxiv_results'
#a query function that will subscribe to the query queue and call the arxiv_query function
#and publish the results to the result queue

class ArxivQueryServer():
    def __init__(self, url='localhost', query_queue='arxiv_query'):
        self.url = url
        self.query_queue = query_queue
        self.params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.query_queue)
        self.channel.basic_consume(queue=self.query_queue, on_message_callback=self.on_request)
        print("ArxivQueryServer is waiting for requests...")
        self.channel.start_consuming()
    
    def on_request(self, ch, method, props, body):
        query_params = json.loads(body)
        result = arxiv_query(query_params['query_string'], query_params.get('start', 0), query_params.get('max_results', 10))
        
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=json.dumps(result))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def close(self):
        self.connection.close()



#accept a query string, optional start index and optional max_results
# return a list of dictionaries of items extracted from the parsed feed
# Each item in the list will contain the following
# 'title' - The title of the entry
# 'authors' - A list of authors
# 'arxiv_url' - URL to the entry on the arXiv
# 'pdf_url' - URL to the PDF of the entry on the arXiv

def arxiv_query(search_query, start=0, max_results=10):
    base_url = 'http://export.arxiv.org/api/query?'
    query = 'search_query="%s"&start=%i&max_results=%i' % (search_query, start, max_results)
    url = base_url + query
    #print(url)
    url = url.replace(' ', '%20')
    response = urllib.request.urlopen(url)
    #print(response)
    feed = feedparser.parse(response)
    #print(feed)
    entries = []
    for entry in feed.entries:
        authors = [author.name for author in entry.authors]
        entry_dict = {
            'title': entry.title,
            'authors': authors,
            'arxiv_url': entry.link,
            'pdf_url': next(link.href for link in entry.links if 'title' in link and link.title == 'pdf')
        }
        #print(entry_dict)
        entries.append(entry_dict)
    return entries


if __name__ == '__main__':
    #check is the RABBITMQ_URL environment variable is set
    #if it is use it as the url for the server, otherwise use 'localhost'
    url = os.getenv('CLOUDAMQP_URL', 'localhost')
    server = ArxivQueryServer(url=url)
    #listen for a hangup signal and close the server
    def signal_handler(sig, frame):
        server.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()

