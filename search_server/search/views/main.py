"""Concurrent search across index segments."""
from concurrent.futures import ThreadPoolExecutor
import math
import sqlite3
import requests
from flask import render_template, request
from search import app, model


def fetch_segment(url, query, weight):
    response = requests.get(url, params={"q": query, "w": weight, "explain": "1"}, timeout=5)
    response.raise_for_status()
    return response.json()["hits"]


@app.route("/")
def main():
    query = request.args.get("q", "").strip()
    try:
        weight = float(request.args.get("w", "0.5"))
    except ValueError:
        weight = 0.5
    if not math.isfinite(weight):
        weight = 0.5
    weight = max(0.0, min(1.0, weight))
    hits, results, warnings = [], [], []
    if query:
        urls = app.config["SEARCH_INDEX_SEGMENT_API_URLS"]
        with ThreadPoolExecutor(max_workers=max(1, len(urls))) as executor:
            futures = [executor.submit(fetch_segment, url, query, weight) for url in urls]
            for future in futures:
                try:
                    hits.extend(future.result())
                except (requests.RequestException, ValueError, KeyError):
                    warnings.append("An index segment is unavailable. Results may be incomplete.")
        hits.sort(key=lambda hit: (-hit["score"], hit["docid"]))
        unique_hits = {}
        for hit in hits:
            unique_hits.setdefault(hit["docid"], hit)
        hits = list(unique_hits.values())
        try:
            documents = {doc["docid"]: doc for doc in model.get_documents([h["docid"] for h in hits[:10]])}
            for hit in hits[:10]:
                if hit["docid"] in documents:
                    document = documents[hit["docid"]]
                    if not document["url"].startswith(("https://", "http://")):
                        document["url"] = "#"
                    results.append({**document, **hit})
        except sqlite3.Error:
            warnings.append("Document metadata is unavailable. Run python bin/searchdb first.")
    return render_template("main.html", query=query, weight=weight, results=results,
                           total=len(hits), warnings=sorted(set(warnings)))
