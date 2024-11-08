import pandas as pd
import spacy
import string
from flask import Flask, request, render_template, jsonify
from transformers import AutoTokenizer, AutoModel
from pymedtermino import icd10  # UMLS or SNOMED can also be used for detailed ontology mapping
from elasticsearch import Elasticsearch

# Load pre-trained medical NLP model (e.g., ClinicalBERT)
tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
model = AutoModel.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")

# Initialize SpaCy for lemmatization and stop word removal
nlp = spacy.load("en_core_web_sm")

# Initialize Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Load dataset (ensure 'dataset.csv' contains relevant data like 'Title', 'Abstract', etc.)
df = pd.read_csv("dataset.csv")
if df.empty:
    raise ValueError("The dataset is empty. Please check the dataset file.")

# Step 1: Preprocess medical text
def preprocess_text(text):
    if pd.isna(text):
        return ""
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc 
        if token.text not in spacy.lang.en.stop_words.STOP_WORDS and token.text not in string.punctuation
    ]
    return " ".join(tokens)

# Step 2: Map terms to medical ontology (ICD-10 example)
def map_to_ontology(term):
    icd_code = icd10.search(term)  # Using ICD-10 for concept mapping
    return icd_code[0].code if icd_code else term  # Map to ICD-10 code if available

# Step 3: Generate Boolean query from user input
def generate_boolean_query(user_input):
    terms = user_input.split(',')
    mapped_terms = [map_to_ontology(term.strip()) for term in terms]
    boolean_query = " AND ".join(mapped_terms)
    return boolean_query

# Step 4: Index data in Elasticsearch
def index_data():
    for idx, row in df.iterrows():
        doc = {
            "title": row.get("Title", ""),
            "abstract": preprocess_text(row.get("Abstract", "")),
            "keywords": preprocess_text(row.get("Keywords", ""))
        }
        es.index(index="healthcare_data", id=idx, body=doc)
    print("Data indexed successfully in Elasticsearch.")

# Step 5: Execute the query in Elasticsearch
def execute_query(query):
    search_query = {
        "query": {
            "query_string": {
                "query": query
            }
        }
    }
    res = es.search(index="healthcare_data", body=search_query)
    results = [
        {
            "title": hit["_source"]["title"],
            "abstract": hit["_source"]["abstract"],
            "keywords": hit["_source"]["keywords"]
        }
        for hit in res["hits"]["hits"]
    ]
    return results

# Step 6: Flask app for web interface
app = Flask(_name_)

@app.route('/')
def home():
    return render_template('newindex.html')

@app.route('/search', methods=['POST'])
def search():
    user_input = request.form['terms']
    boolean_query = generate_boolean_query(user_input)
    results = execute_query(boolean_query)
    if not results:
        return jsonify({"message": "No results found for the given query."}), 404
    return jsonify(results)

if _name_ == "_main_":
    index_data()  # Index data in Elasticsearch before starting the app
    app.run(debug=True)