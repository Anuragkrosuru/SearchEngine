"""
Configuration for the Search server.
"""

# List of Index‐segment API URLs that the Search server will query.
# Tests may override this variable to point at different ports.
SEARCH_INDEX_SEGMENT_API_URLS = [
    "http://localhost:9000/api/v1/hits/",
    "http://localhost:9001/api/v1/hits/",
    "http://localhost:9002/api/v1/hits/",
]
