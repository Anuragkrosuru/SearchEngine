import os
import sqlite3
import flask
from flask import current_app


def dict_factory(cursor, row):
    """
    Convert a sqlite3 row to a dict keyed by column name.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """
    Open a database connection and store it on flask.g.
    Uses the path from app config 'DATABASE_FILENAME', defaulting to 'var/search.sqlite3'.
    Enables foreign key support and sets row factory to dict_factory.
    """
    if 'sqlite_db' not in flask.g:
        # Determine database filename from config or use default
        db_path = current_app.config.get(
            'DATABASE_FILENAME',
            os.path.join('var', 'search.sqlite3')
        )
        # Connect to the SQLite database file
        flask.g.sqlite_db = sqlite3.connect(str(db_path))
        # Use dict_factory to return rows as dictionaries
        flask.g.sqlite_db.row_factory = dict_factory
        # Enable foreign key support
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


def close_db(error):  # pylint: disable=unused-argument
    """
    Close the SQLite database at the end of the request.
    Commits changes before closing.
    """
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def get_document(docid):
    """
    Retrieve a single document by its docid.
    Returns a dict with keys: docid, title, summary, url, or None if not found.
    """
    db = get_db()
    row = db.execute(
        'SELECT docid, title, summary, url FROM documents WHERE docid = ?',
        (docid,)
    ).fetchone()
    return row


def get_documents(docids):
    """
    Retrieve multiple documents given a list of docids.
    Returns a list of dicts in the same order as the input docids.
    """
    if not docids:
        return []
    # Build placeholders for the SQL IN clause
    placeholders = ','.join('?' for _ in docids)
    query = f'SELECT docid, title, summary, url FROM documents WHERE docid IN ({placeholders})'
    db = get_db()
    rows = db.execute(query, docids).fetchall()
    # Map rows by docid for ordering
    row_map = {row['docid']: row for row in rows}
    # Return rows in the order of docids
    result = [row_map[d] for d in docids if d in row_map]
    return result
