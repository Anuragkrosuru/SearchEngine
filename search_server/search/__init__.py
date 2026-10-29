"""Search frontend application."""
from pathlib import Path
from flask import Flask

app = Flask(__name__)
app.config.from_object("search.config")
app.config["DATABASE_FILENAME"] = Path(__file__).resolve().parents[2] / "var/search.sqlite3"

from search import model
app.teardown_appcontext(model.close_db)
from search.views import main
