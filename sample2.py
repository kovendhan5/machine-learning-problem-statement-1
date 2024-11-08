import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, render_template
import os
import requests
from functools import lru_cache
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# --- Configuration ---
DATA_DIR = r"K:\hackathon\New folder"  # Use a raw string (r"...") for Windows paths
COVID_DATA_FILE = "dataset.csv" # Replace with your actual data file
ICD_API_URL = "https://icd.who.int/icdapi"
DEFAULT_SEARCH_TYPE = "research"

# ICD API credentials (environment variables - KEEP THESE SECURE!)
CLIENT_ID = os.environ.get("YOUR_CLIENT_ID")  # Do NOT put credentials directly in the code
CLIENT_SECRET = os.environ.get("YOUR_CLIENT_SECRET")

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

# --- NLTK Initialization ---
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.isalnum() and token not in stop_words]
    return " ".join(tokens)

if covid_df is not None:
    text_col = next((col for col in covid_df.columns if col in ('text', 'abstract')), None)
    if text_col:
        covid_df['processed_text'] = covid_df[text_col].apply(preprocess_text)
    else:
        print("No suitable text column ('text' or 'abstract') found in dataset.")
        exit()

# --- 2. Query Processing and Boolean Generation ---
@lru_cache(maxsize=1)  # Cache the access token
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
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
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
    tokens = nltk.word_tokenize(user_query)
    keywords = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.isalnum() and token not in stop_words]
    icd_codes = get_icd_codes(user_query)
    keywords.extend(icd_codes)
    return " AND ".join(keywords)

# --- 3. Search and Retrieval ---
def search_data(query_string, data_source):
    if data_source == "research" and covid_df is not None and 'processed_text' in covid_df.columns:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(covid_df['processed_text'])
        query_vec = vectorizer.transform([query_string])
        similarity_scores = cosine_similarity(query_vec, tfidf_matrix)

        top_indices = similarity_scores[0].argsort()[::-1]
        results = covid_df.iloc[top_indices].head(50)  # Get top 50 results
    else:
        results = pd.DataFrame()  # Return empty dataframe if dataset is not loaded.

    return results

# --- 4. Flask App ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            error_message = "Please enter a search query"
            return render_template('index.html', error_message=error_message) # Added error handling for index.html too.

        search_type = request.form.get('search_type', DEFAULT_SEARCH_TYPE)
        boolean_query = generate_boolean_query(query, search_type)
        results = search_data(boolean_query, search_type)

        if results.empty:
            no_results_message = "No results found for your query."
            return render_template('results.html', message=no_results_message, query=query, num_results=0)

        return render_template('results.html', tables=[results.to_html(classes='data')], query=query, num_results=len(results))

    return render_template('index.html') #  Corrected template name

if __name__ == '__main__':
    app.run(debug=True)
