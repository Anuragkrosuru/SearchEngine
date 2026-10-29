# SearchEngine

A small, explainable search engine for a collection of 3,062 Wikipedia articles.
Search with keywords, browse ranked results, and open **Why this result?** to
see how each page earned its score.

Try **web**, **MapReduce**, or **artificial intelligence**. This searches the
bundled collection, so coverage is limited. It does not search the live web.

## Features

- Simple blue and white interface with clickable example searches.
- TF-IDF cosine relevance combined with precomputed PageRank.
- Per-result explanations showing matched terms and scoring contributions.
- Concurrent queries across three index segments.
- SQLite document metadata and clear messages when a service is unavailable.

## Ranking

After removing stopwords, a document must contain every query term to match.
The index API calculates:

```text
score = (1 - w) × text_relevance + w × pagerank
```

Text relevance is cosine similarity using the full document vector. The UI
uses an equal blend by default (`w=0.5`). API clients can change `w` from 0 to 1.
The explanation shows each term's contribution to text relevance and the two
weighted contributions to the final score. Scores are not confidence values.

Example API request, against one index segment:

```text
http://localhost:9000/api/v1/hits/?q=mapreduce&w=0.5&explain=1
```

Omit `explain=1` for the original response containing only `docid` and `score`.
The frontend merges results from all three segments and shows the top ten.

## Run locally

Use Python 3.12 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install Flask requests beautifulsoup4 pytest
python bin/build-index
python bin/searchdb
```

The rebuild command generates local index segments from `inverted_index/crawl`.
Generated segments and runtime data are ignored by Git. The inherited MapReduce
pipeline is incomplete; `bin/build-index` supplies a separate local rebuild path.

In four separate terminals, activate the virtual environment and run one command
per terminal from the repository root:

```sh
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_0.txt flask --app index run --port 9000
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_1.txt flask --app index run --port 9001
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_2.txt flask --app index run --port 9002
PYTHONPATH=search_server flask --app search run --port 8000
```

Open [localhost:8000](http://localhost:8000). All three index services are needed
for complete results. These commands start local development servers.

## Structure

- `bin/build-index`: local index rebuild command.
- `index_server/`: Flask API, index loading, and ranking logic.
- `search_server/`: Flask frontend, templates, styles, and metadata access.
- `inverted_index/`: bundled crawl and inherited MapReduce pipeline files.
- `tests/`: inherited tests and focused explanation tests.

## Validation

```sh
PYTHONPATH=index_server:search_server python -m pytest tests/test_explanations.py -q
```

The five focused tests cover explanation arithmetic, weight endpoints, repeated
terms, API compatibility, HTML escaping, and unavailable services. Real searches
and explanation panels were also checked locally against the rebuilt collection.
The full inherited test suite has not been validated for these changes.

## Origin and contributors

This project extends shared University of Michigan EECS 485 P5 coursework from
[tisyamukherjee/485p5](https://github.com/tisyamukherjee/485p5). Original contributors
listed in the imported README are Anurag Krosuru, @justinsu, and @tisyaM.
See [SOURCE.md](SOURCE.md) for the imported revision and publication restriction.

Subsequent changes add the working frontend, ranking explanations, a local index
rebuild command, and runtime fixes. These additions do not remove the original
code's attribution or publication restrictions.
