import pandas as pd
import spacy
import scispacy
from scispacy.abbreviation import AbbreviationDetector
from scispacy.linking import EntityLinker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, render_template
import os
import requests
from functools import lru_cache

# --- Configuration ---
DATA_DIR = "data"
COVID_DATA_FILE = "dataset.csv"  # Replace with your actual data file
ICD_API_URL = "https://icd.who.int/icdapi"
DEFAULT_SEARCH_TYPE = "research"

# ICD API credentials (environment variables)
CLIENT_ID = os.environ.get("ICD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ICD_CLIENT_SECRET")

# --- Data Loading and Preprocessing ---
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise ValueError(f"Data file '{filepath}' is empty.")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(f"Error loading '{filepath}': {e}")
        return None

covid_df = load_data(os.path.join(DATA_DIR, COVID_DATA_FILE))


# --- SpaCy Initialization ---
try:
    nlp = spacy.load("en_core_sci_sm") # Make absolutely sure this is the correct model name

    nlp.add_pipe("abbreviation_detector")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
except OSError as e:
    print(f"Error loading SpaCy/SciSpacy: {e}")
    exit()

def preprocess_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = str(text)
    doc = nlp(text)
    abbreviations = {abrv.text: abrv._.long_form for abrv in doc._.abbreviations} # Create dict for replacements
    for short_form, long_form in abbreviations.items(): # perform all replacements
        text = text.replace(short_form, long_form)

    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return " ".join(tokens)

if covid_df is not None:
    text_col =  'text' if 'text' in covid_df.columns else ('abstract' if 'abstract' in covid_df.columns else None) # Select appropriate text column name

    if text_col:
        covid_df['processed_text'] = covid_df[text_col].apply(preprocess_text) # Use variable to select correct column
    else:
        print("No suitable text column ('text' or 'abstract') found in dataset.")
        exit()
# ... (Rest of the code - ICD functions, search, Flask app - should work as provided before)
# --- 2. Query Processing and Boolean Generation ---

@lru_cache(maxsize=1)
def get_icd_access_token():
    url = f"{ICD_API_URL}/Token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error during access token retrieval: {e}")
        return None


def get_icd_codes(query):
    token = get_icd_access_token()
    if token is None:
        print("Error: Could not obtain ICD access token.")
        return []

    url = f"{ICD_API_URL}/GetICD11CodeInfo"
    headers = {
        "Accept": "application/json",
        "API-Version": "v2",
        "Authorization": f"Bearer {token}"
    }
    params = {"q": query, "useFlexisearch": "true"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        icd_codes = [item["code"] for item in data.get("linearizations", []) if "code" in item]
        return icd_codes
    except requests.exceptions.RequestException as e:
        print(f"Error in ICD API request: {e}")
        return []

def generate_boolean_query(user_query, search_type=DEFAULT_SEARCH_TYPE):
    doc = nlp(user_query)
    keywords = []
    for token in doc:
        if not (token.is_stop or token.is_punct or token.is_space):
            if token.ent_type_ in ("DISEASE", "CHEMICAL", "DRUG"):
                umls_entities = [entity.kb_id_ for entity in token._.kb_ents if entity.kb_id_]
                keywords.extend(umls_entities)
            keywords.append(token.lemma_.lower())

    icd_codes = get_icd_codes(user_query)
    if icd_codes:
        keywords.extend(icd_codes)

    query_string = " AND ".join(keywords)
    return query_string

# --- 3. Search and Retrieval ---
def search_data(query_string, data_source):
    if data_source == "research" and covid_df is not None and 'processed_text' in covid_df.columns:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(covid_df['processed_text'])
        query_vec = vectorizer.transform([query_string])
        similarity_scores = cosine_similarity(query_vec, tfidf_matrix)

        top_indices = similarity_scores[0].argsort()[::-1]
        results = covid_df.iloc[top_indices].head(50)
    else:
        results = pd.DataFrame()

    return results

# --- 4. Flask App ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()

        if not query:
            error_message = "Please enter a search query"
            return render_template('newindex.html', error_message=error_message)

        search_type = request.form.get('search_type', DEFAULT_SEARCH_TYPE)
        boolean_query = generate_boolean_query(query, search_type)
        results = search_data(boolean_query, search_type)

        if results.empty:
            no_results_message = "No results found for your query."
            return render_template('newresults.html', message=no_results_message, query=query, num_results=0)

        return render_template('newresults.html', tables=[results.to_html(classes='data')], query=query, num_results=len(results))

    return render_template('newindex.html')

if __name__ == '__main__':
    app.run(debug=True)