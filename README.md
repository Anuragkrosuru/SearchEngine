# SearchEngine
SearchEngine project demo

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
