from flask import Flask
from pathlib import Path
import os

def create_app():
    # Define the directory containing the inverted index segments.
    # Here, __file__ refers to index/__init__.py, so we move into the 'inverted_index' folder.
    INDEX_DIR = Path(__file__).parent / "inverted_index"
    
    # Set the configuration for INDEX_PATH.
    # If the environment variable INDEX_PATH is set, use that.
    # Otherwise, default to the path for 'inverted_index_1.txt' within the inverted_index directory.
    app.config["INDEX_PATH"] = os.getenv("INDEX_PATH", str(INDEX_DIR / "inverted_index_1.txt"))
    
    # Register the API blueprint under '/api/v1'
    from .api.main import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    
    return app

app = create_app()

import index.api  # noqa: E402  pylint: disable=wrong-import-position

# Load inverted index, stopwords, and pagerank into memory.
index.api.load_index()

if __name__ == '__main__':
    # Run the app on port 9000; adjust host and port as needed.
    app.run(debug=True, host='0.0.0.0', port=9000)