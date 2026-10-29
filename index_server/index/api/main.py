from flask import Blueprint, jsonify, request
import math
import os
import re

# Global containers for loaded data
index_data = {}
stopwords = set()
pagerank = {}
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/', methods=['GET'])
def get_services():
    """
    GET /api/v1/
    Returns a JSON object listing available services.
    Example:
    {
        "hits": "/api/v1/hits/",
        "url": "/api/v1/"
    }
    """
    return jsonify({
        "hits": "/api/v1/hits/",
        "url": "/api/v1/"
    })

@api_blueprint.route('/hits/', methods=['GET'])
def get_hits():
    """
    GET /api/v1/hits/?q=<query>
    
    Extracts the search query and optional weight parameter (defaulting to 0.5).
    Returns a JSON object with a "hits" field.
    
    Add explain=1 to include the ranking components for each hit.
    """
    query = request.args.get("q", "")
    # If no query is provided, we can either return an error or an empty result.
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    try:
        weight = float(request.args.get("w", 0.5))
    except ValueError:
        weight = 0.5

    # Explanations are opt-in to preserve the existing API response.
    search_results = perform_search(query, weight, request.args.get("explain") == "1")
    
    return jsonify({"hits": search_results})

def perform_search(query, weight, explain=False):
    """Performs a search for the given query and PageRank weight `weight`."""

    weight = weight if math.isfinite(weight) else 0.5
    weight = max(0.0, min(1.0, weight))

    # 1) Clean the query just like you do for documents:
    # Remove non-alphanumeric chars, casefold, split on whitespace, remove stopwords
    query_terms = process_query(query)
    if not query_terms:
        return []

    # 2) Build a dictionary of query term frequencies
    q_tf = {}
    for term in query_terms:
        q_tf[term] = q_tf.get(term, 0) + 1

    # Convert each query term frequency to tf-idf by multiplying by the term's IDF
    # Recall: if index_data[term] is in the format:
    #   term idf doc1 tf1 norm1 doc2 tf2 norm2 ...
    # then tokens[1] is the IDF.
    q_tfidf = {}
    for term, freq in q_tf.items():
        if term not in index_data:
            # Term not found in your index_data, skip it or treat IDF as 0
            continue
        tokens = index_data[term].split()
        try:
            idf = float(tokens[1])  # The second token is IDF
        except ValueError:
            idf = 0.0
        # Simple tf * idf for the query
        q_tfidf[term] = freq * idf

    # Query normalization factor = sqrt( sum of (tf-idf)^2 ) for all query terms
    q_norm = math.sqrt(sum(value * value for value in q_tfidf.values()))

    # If the query ends up with zero length, return empty
    if q_norm == 0:
        return []

    # 3) Retrieve the set of docs that contain *all* the query terms (AND semantics).
    # We'll collect doc sets for each term, then do an intersection.
    doc_sets = []
    for term in query_terms:
        docs_for_term = get_docs_for_term(term)
        if not docs_for_term:
            return []  # If one term has no docs, the intersection is empty
        doc_sets.append(docs_for_term)
    # Intersection of all doc sets
    common_docs = set.intersection(*doc_sets)

    results = []
    for docid in common_docs:
        # 4) Construct the doc’s tf-idf vector for just the query terms
        doc_tfidf_vector = {}
        doc_norm_squared = 0.0
        # We'll parse each relevant term's line in index_data to find doc tf + doc norm
        for term in q_tfidf:
            if term not in index_data:
                continue  # skip missing terms
            tokens = index_data[term].split()
            # tokens format: [term, idf, doc1, tf1, norm1, doc2, tf2, norm2, ...]
            idf_str = tokens[1]  # The second token is the IDF
            term_idf = float(idf_str) if idf_str else 0.0

            # Next tokens come in groups of three: (doc, tf, doc_norm)
            # so parse them in a loop
            for i in range(2, len(tokens), 3):
                doc_in_line = tokens[i]
                tf_in_line = tokens[i+1]
                # norm_in_line = tokens[i+2] 

                if doc_in_line == docid:
                    # Found the matching doc
                    try:
                        doc_tf_val = float(tf_in_line)
                    except ValueError:
                        doc_tf_val = 0.0
                    # doc_tfidf = tf * idf
                    doc_tfidf_vector[term] = doc_tf_val * term_idf
                    doc_norm_squared = float(tokens[i+2])
                    break

        # Use the full document vector norm stored in each posting.
        doc_vec_norm = math.sqrt(doc_norm_squared)

        if doc_vec_norm == 0:
            # If doc's vector is empty or 0, skip
            continue

        # Dot product between the doc vector and query vector = sum(doc_tf-idf * query_tf-idf) over all terms
        dot_product = 0.0
        for term, q_weight in q_tfidf.items():
            doc_weight = doc_tfidf_vector.get(term, 0.0)
            dot_product += (q_weight * doc_weight)

        # Cosine similarity: dot_product / (norm_q * norm_doc)
        cos_sim = dot_product / (q_norm * doc_vec_norm)

        # 6) Combine with PageRank: 
        # PageRank(d) is from the global dictionary 'pagerank'.
        doc_pr = pagerank.get(docid, 0.0)  # default 0 if not found
        score = weight * doc_pr + (1 - weight) * cos_sim

        hit = {"docid": int(docid), "score": score}
        if explain:
            hit["explanation"] = {
                "text_relevance": cos_sim,
                "pagerank": doc_pr,
                "pagerank_weight": weight,
                "text_contribution": (1 - weight) * cos_sim,
                "pagerank_contribution": weight * doc_pr,
                "matched_terms": [
                    {"term": term,
                     "cosine_contribution": q_tfidf[term] * doc_tfidf_vector[term]
                     / (q_norm * doc_vec_norm)}
                    for term in q_tfidf
                ],
            }
        results.append(hit)

    # 7) Sort the results in descending order by score
    results.sort(key=lambda x: (-x["score"], x["docid"]))
    return results

def process_query(query):
    """
    Cleans the input query string.
    Returns:
      A list of cleaned query terms.
    """
    # Remove non-alphanumeric characters (except spaces)
    cleaned = re.sub(r"[^a-zA-Z0-9 ]+", "", query)
    # Convert to lowercase
    cleaned = cleaned.casefold()
    # Split into individual terms by whitespace
    terms = cleaned.split()
    # Remove any stopwords from the query terms.
    terms = [term for term in terms if term not in stopwords]
    return terms

def get_docs_for_term(term):
    """
    Retrieves the set of document IDs that contain the specified term from the inverted index.
    Returns:
      A set of document IDs (as strings) for the term.
    """
    # If the term is not in the index, return an empty set.
    if term not in index_data:
        return set()
    
    # Retrieve the corresponding inverted index line.
    line = index_data[term]
    tokens = line.split()
    docs = set()
    # Tokens format: tokens[0] is the term, tokens[1] is the idf.
    # From tokens[2] onward, the tokens appear in groups of three: docid, tf, norm factor.
    for i in range(2, len(tokens), 3):
        docs.add(tokens[i])
    return docs




def load_index():
    """
    Loads the inverted index, stopwords, and pagerank into memory.
    Files are read from the index_server/index/ directory.
    
    This function is intended to be called once during app initialization.
    """

    # Determine the base directory 
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the default file path for the inverted index
    default_index_path = os.path.join(base_dir, "..", "inverted_index", "inverted_index_1.txt")
    
    # Check if the INDEX_PATH environment variable is set; otherwise, use the default index path.
    index_path = os.getenv("INDEX_PATH", default_index_path)

    # Load the inverted index into the global dictionary 'index_data'
    global index_data 
    try:
        # Open the inverted index file 
        with open(index_path, "r") as f:
            # Initialize the dictionary 
            index_data = {}
            # Process each line in the file
            for line in f:
                # Skip any lines that are empty after stripping whitespace
                if not line.strip():
                    continue
                # Split the line on whitespace to create tokens
                tokens = line.split()
                # Use the first token as the key 
                key = tokens[0]
                # Store the stripped version of the line in the dictionary under the key
                index_data[key] = line.strip()
        # Print a message indicating the inverted index was successfully loaded
        print(f"Inverted index loaded from {index_path} (entries: {len(index_data)})")
    except Exception as e:
        # If an error occurs, print the error message
        print(f"Error loading inverted index from {index_path}: {e}")


    # Load the stopwords file into the global set 'stopwords'
    global stopwords
    # Construct the path for the stopwords file
    stopwords_path = os.path.join(base_dir, "..", "stopwords.txt")
    try:
        # Open the stopwords file for reading
        with open(stopwords_path, "r") as f:

            # Create a set of stopwords by stripping each line and ignoring empty lines
            stopwords = {line.strip() for line in f if line.strip()}

        # Print a message indicating the number of stopwords loaded.
        print(f"Stopwords loaded from {stopwords_path} (count: {len(stopwords)})")
    except Exception as e:
        # Print an error message if reading the stopwords file fails.
        print(f"Error loading stopwords from {stopwords_path}: {e}")
    
    
    # Load the pagerank file into the global dictionary 'pagerank'.
    global pagerank
    # Construct the path for pagerank.out, assumed to be one directory up.
    pagerank_path = os.path.join(base_dir, "..", "pagerank.out")
    try:
        # Open the pagerank file for reading.
        with open(pagerank_path, "r") as f:
            # Initialize the pagerank dictionary.
            pagerank = {}
            # Process each line in the pagerank file.
            for line in f:
                # Split the line into parts (expecting at least a docid and a score).
                parts = line.replace(",", " ").split()
                if len(parts) >= 2:
                    # The first part is the document ID.
                    docid = parts[0]
                    try:
                        # Convert the second part into a float representing the PageRank score.
                        score = float(parts[1])
                        # Save the score in the pagerank dictionary under the document ID.
                        pagerank[docid] = score
                    except ValueError:
                        # If conversion fails, continue to the next line.
                        continue
        # Print a message indicating how many pagerank entries were loaded.
        print(f"PageRank loaded from {pagerank_path} (entries: {len(pagerank)})")
    except Exception as e:
        # If an error occurs while loading pagerank, print the error message.
        print(f"Error loading pagerank from {pagerank_path}: {e}")
    
    # Print a final message indicating that all data has been successfully loaded into memory.
    print("Index, stopwords, and PageRank have been loaded into memory.")
