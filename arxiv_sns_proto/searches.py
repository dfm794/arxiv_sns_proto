import pika
import json
import uuid
import os
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from arxiv_summary.summarize_pdf import prep_pdf_text_for_summarization, summarize_pdf

bp = Blueprint('searches', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    print(f'g.user: {g.user}')
    db.execute(
        'SELECT s.id, search_query, created, user_id, username'
        ' FROM search s JOIN "user" u ON s.user_id = u.id'
        ' WHERE user_id = %s'
        ' ORDER BY created DESC',
        (g.user[0],)
    )
    searches = db.fetchall()
    
    # Create a new list to hold search data and results
    searches_with_results = []
    
    # Fetch search results for each search
    for search in searches:
        db.execute(
            'SELECT id, title, authors, arxiv_url, pdf_url'
            ' FROM search_result'
            ' WHERE search_id = %s'
            ' ORDER BY title DESC',
            (search['id'],)
        )
        results = db.fetchall()
        
        # Create a new dictionary with all search data and results
        search_data = dict(search)
        search_data['results'] = results
        searches_with_results.append(search_data)
    
    return render_template('searches/index.html', searches=searches_with_results)

def perform_arxiv_search(query_string, max_results=10):
    url = os.getenv('CLOUDAMQP_URL', 'localhost')
    if url != 'localhost':
            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
    else:
        connection = pika.BlockingConnection()
    channel = connection.channel()

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    response = None

    def on_response(ch, method, props, body):
        nonlocal response
        if corr_id == props.correlation_id:
            response = json.loads(body)

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    channel.basic_publish(
        exchange='',
        routing_key='arxiv_query',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
        ),
        body=json.dumps({"query_string": query_string, "max_results": max_results})
    )

    while response is None:
        connection.process_data_events()
    print(f'response: {response}')
    connection.close()
    return response

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        search_query = request.form['search_query']
        error = None

        if not search_query:
            error = 'Search Query is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            #and prepend all: if there are no colons in the search query
            if ':' not in search_query:
                search_query = 'all:' + search_query
            db.execute(
                'INSERT INTO search (search_query, user_id)'
                ' VALUES (%s, %s)',
                (search_query, g.user[0])
            )
            db.connection.commit()
            
            # Get the ID of the newly inserted search
            db.execute('SELECT LASTVAL()')
            search_id = db.fetchone()[0]
            
            # Perform the arXiv search
            search_results = perform_arxiv_search(search_query)
            
            # Insert search results into the database
            for result in search_results:
                db.execute(
                    'INSERT INTO search_result (search_id, title, authors, arxiv_url, pdf_url, pdf_summary)'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    (search_id, result['title'], result['authors'], result['arxiv_url'], result['pdf_url'], "")
                )
            db.connection.commit()
            
            return redirect(url_for('searches.index'))

    return render_template('searches/create.html')

def get_search(id, check_author=True):
    db = get_db()
    db.execute(
        'SELECT s.id, search_query, created, user_id, username'
        ' FROM search s JOIN "user" u ON s.user_id = u.id'
        ' WHERE s.id = %s',
        (id,)
    )
    search = db.fetchone()

    if search is None:
        abort(404, f"Search id {id} doesn't exist.")

    if check_author and search['user_id'] != g.user[0]:
        abort(403)

    return search

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    search = get_search(id)

    if request.method == 'POST':
        search_query = request.form['search_query']
        error = None

        if not search_query:
            error = 'Search Query is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            # Update the search query
            db.execute(
                'UPDATE search SET search_query = %s'
                ' WHERE id = %s',
                (search_query, id)
            )
            
            # Delete old search results
            db.execute('DELETE FROM search_result WHERE search_id = %s', (id,))
            
            # Perform the new arXiv search
            search_results = perform_arxiv_search(search_query)
            
            # Insert new search results into the database
            for result in search_results:
                db.execute(
                    'INSERT INTO search_result (search_id, title, authors, arxiv_url, pdf_url, pdf_summary  )'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    (id, result['title'], result['authors'], result['arxiv_url'], result['pdf_url'], "")
                )
            
            db.connection.commit()
            return redirect(url_for('searches.index'))

    return render_template('searches/update.html', search=search)

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete(id):
    get_search(id)
    db = get_db()
    
    # Delete associated search results first
    db.execute('DELETE FROM search_result WHERE search_id = %s', (id,))
    
    # Then delete the search
    db.execute('DELETE FROM search WHERE id = %s', (id,))
    
    db.connection.commit()
    return redirect(url_for('searches.index'))

@bp.route('/<int:id>/summary', methods=['GET'])
@login_required
def summary(id):
    db = get_db()
    db.execute(
        'SELECT sr.id, sr.title, sr.pdf_url, sr.pdf_summary'
        ' FROM search_result sr JOIN search s ON sr.search_id = s.id'
        ' WHERE sr.id = %s AND s.user_id = %s',
        (id, g.user[0])
    )
    result = db.fetchone()

    if result is None:
        abort(404, f"Search result id {id} doesn't exist or doesn't belong to you.")

    summary = result['pdf_summary']

    if summary == "":
        # Retrieve and summarize the PDF
        pdf_url = result['pdf_url']
        try:
            text = prep_pdf_text_for_summarization(pdf_url)
            summary = summarize_pdf(text)

            # Update the database with the new summary
            db.execute(
                'UPDATE search_result SET pdf_summary = %s WHERE id = %s',
                (summary, id)
            )
            db.connection.commit()
        except Exception as e:
            flash(f"Error processing PDF: {str(e)}")
            summary = "Error occurred while processing the PDF."

    return render_template('searches/summary.html', 
                           id=id, 
                           summary=summary, 
                           title=result['title'])
