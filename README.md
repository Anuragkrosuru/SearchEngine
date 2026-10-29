# Search Engine
Search Engine project demo

A scalable search engine similar to Google or Bing, built as part of the University of Michigan EECS 485 course. This project implements information retrieval concepts like text analysis (tf-idf) and link analysis (PageRank), along with parallel data processing using MapReduce.
<img width="2458" height="1996" alt="image" src="https://github.com/user-attachments/assets/3fd3fe01-8e40-4710-a38b-b31a9442b350" />

## 🎯 Learning Goals

- **Information Retrieval**: Text analysis (tf-idf) and link analysis (PageRank)
- **Parallel Data Processing**: MapReduce pipeline implementation
- **Service-Oriented Architecture**: Scaling dynamic pages and web search
- **Distributed Systems**: Multiple index servers and search coordination

## 🏗️ Architecture Overview

The project consists of three main components:

1. **Inverted Index Pipeline** - MapReduce programs that build a segmented inverted index
2. **Index Server** - REST API that returns search results in JSON format
3. **Search Server** - User interface that returns search results like Google/Bing

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLite
- **Processing**: Custom MapReduce implementation, BeautifulSoup
- **Networking**: Python sockets, TCP/UDP protocols, REST APIs
- **Performance**: Multithreading, parallel processing
- **Data**: HTML parsing, text extraction, JSON processing

## 📁 Project Structure

```
p5-search-engine/
├── bin/                    # Shell scripts (init, install, search, searchdb)
├── inverted_index/         # MapReduce pipeline for building inverted index
│   ├── map*.py            # Mapper programs
│   ├── reduce*.py         # Reducer programs
│   ├── partition.py       # Custom partitioner
│   ├── pipeline.sh        # Pipeline execution script
│   └── crawl/             # Input HTML documents
├── index_server/          # REST API server for inverted index segments
│   ├── index/
│   │   ├── api/           # REST API endpoints
│   │   ├── inverted_index/ # Inverted index segment files
│   │   └── pagerank.out   # PageRank scores
├── search_server/         # User interface server
│   ├── search/
│   │   ├── templates/     # HTML templates
│   │   ├── static/        # CSS and static files
│   │   └── views/         # Flask view functions
├── tests/                 # Test cases
└── var/                   # Database and log files
```

## 🔍 Core Features

### Inverted Index Pipeline
- **Document Processing**: Parse 20,000+ HTML documents from Wikipedia
- **Text Analysis**: TF-IDF scoring with custom MapReduce implementation
- **Segmentation**: Partition inverted index into 3 segments by document ID
- **PageRank Integration**: Link analysis for document importance scoring

### Index Server
- **REST API**: `/api/v1/hits/` endpoint for search queries
- **Segment Management**: Each server handles one inverted index segment
- **Query Processing**: AND queries with tf-idf and PageRank scoring
- **Concurrent Processing**: Multiple index servers for scalability

### Search Server
- **User Interface**: Google-like search interface with PageRank weight slider
- **Result Aggregation**: Combines results from multiple index servers
- **Database Integration**: SQLite database for document metadata
- **Concurrent API Calls**: Parallel requests to index servers

## 🚀 Getting Started

### Prerequisites
```bash
python 3.8+
flask
beautifulsoup4
sqlite3
```

### Installation
```bash
# Clone the repository
git clone [your-repo-url]
cd p5-search-engine

# Run install script
./bin/install

# Generate search database
./bin/searchdb
```

### Running the System
```bash
# Start index servers (3 segments)
./bin/index start

# Start search server
./bin/search start

# Access search interface
# http://localhost:8000
```

## 📊 Key Algorithms

### TF-IDF Scoring
- **Term Frequency**: Count of terms in documents
- **Inverse Document Frequency**: Log-based scoring for term importance
- **Normalization**: Document length normalization for cosine similarity

### PageRank Integration
- **Weighted Scoring**: Linear combination of tf-idf and PageRank
- **Configurable Weight**: User-adjustable PageRank influence (0.0 to 1.0)
- **Document Importance**: Link-based ranking independent of query

### MapReduce Pipeline
- **Job 0**: Document counting
- **Job 1**: HTML parsing and content extraction
- **Jobs 2-N**: Text processing, indexing, and scoring
- **Final Job**: Segmentation and output formatting

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Test specific components
pytest -v tests/test_pipeline_public.py
pytest -v tests/test_index_server_public.py
pytest -v tests/test_search_server_public.py

# Style checks
pylint *.py
pycodestyle *.py
pydocstyle *.py
```

## 📈 Performance Features

- **60% Performance Boost**: Through multithreading and parallel processing
- **Distributed Architecture**: Multiple index servers for scalability
- **Efficient Indexing**: Segmented inverted index for fast lookups
- **Concurrent Processing**: Parallel API calls to index servers

## 🔧 Development Features

- **Hot Reloading**: Flask debug mode for development
- **Logging**: Comprehensive logging for debugging
- **Process Management**: Init scripts for starting/stopping services
- **Configuration**: Environment-based configuration for different deployments

## 📝 Project Requirements

- **Group Project**: Teams of 2-3 students
- **Due Date**: 11:59pm ET April 20, 2025
- **Submission**: Tarball with source code and documentation
- **Testing**: Must pass all public and hidden unit tests

## 👨‍💻 Authors

**Anurag Krosuru**
- GitHub: [@Anuragkrosuru](https://github.com/Anuragkrosuru)
- LinkedIn: [anuragkro](https://www.linkedin.com/in/anuragkro)
@justinsu, @tisyaM

## 🙏 Acknowledgments

- **Course Staff**: Andrew DeOrio, Melina O'Dell, Maya Baveja
- **University of Michigan**: EECS 485 Course Materials
- **Project Framework**: Based on Hadoop Streaming and MapReduce concepts

---

⭐ **This project demonstrates advanced web systems concepts including distributed computing, information retrieval, and scalable architecture design.**

## Explainable search interface

The frontend preserves the original pink and white theme with a simpler search form,
and expandable **Why this result?** panels. Explanations show normalized matched
query terms, each term's cosine contribution, TF-IDF cosine relevance, raw
PageRank, and the two weighted contributions to the final score:

`score = (1 - w) * text_relevance + w * pagerank`

These are scoring components, not confidence percentages. Cosine relevance uses
the full document norm from the inverted index. The default ranking blends both components equally. API clients may set `w`
to change the PageRank weight. Query matching uses AND semantics
with stopwords removed. API clients can opt in with `explain=1`; the default
response retains the original `docid` and `score` fields.

### Run locally

From the repository root (Python 3.12 or newer):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install Flask requests beautifulsoup4 pytest
python bin/build-index
python bin/searchdb
```

The rebuild command creates the three local index segments from the bundled
crawl. It provides a local rebuild path because the inherited MapReduce
pipeline is incomplete. In separate terminals, with the virtual environment
activated, start each service:

```sh
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_0.txt flask --app index run --port 9000
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_1.txt flask --app index run --port 9001
PYTHONPATH=index_server INDEX_PATH=index_server/index/inverted_index/inverted_index_2.txt flask --app index run --port 9002
PYTHONPATH=search_server flask --app search run --port 8000
```

Open http://localhost:8000. All three index services are needed for complete
results. Service failures appear in the UI rather than silently implying no
matches. Source provenance remains documented in `SOURCE.md`.
