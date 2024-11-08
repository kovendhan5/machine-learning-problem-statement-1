from flask import Flask, request, render_template
from pymongo import MongoClient
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources manually
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection string
mongo_uri = "mongodb+srv://bejistojoseph801:mongodb2003@cluster0.aq48n.mongodb.net/"
client = MongoClient(mongo_uri)

# Initialize NLTK components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(text):
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.isalnum() and token not in stop_words]
    return " ".join(tokens)

# Function to generate Boolean query
def generate_boolean_query(user_query):
    tokens = nltk.word_tokenize(user_query)
    keywords = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.isalnum() and token not in stop_words]
    return " AND ".join(keywords)

# Function to retrieve research studies
def retrieve_research_studies(db):
    results = db['research_studies'].find()
    return results

# Function to filter medical records by symptoms
def filter_medical_records(db, symptoms):
    query = {"symptoms": {"$in": symptoms}}
    results = db['medical_records'].find(query)
    return results

# Function to identify drug interactions
def identify_drug_interactions(db, drug_name):
    query = {"drug_name": drug_name}
    results = db['drug_interactions'].find(query)
    return results

# Function to access diagnostic data
def access_diagnostic_data(db, symptoms, lab_results):
    query = {
        "symptoms": {"$in": symptoms},
        "lab_results": {"$in": lab_results}
    }
    results = db['diagnostic_data'].find(query)
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    databases = ["Student_Profile", "medical", "sample_mflix", "admin", "local"]
    output = {}
    
    if request.method == 'POST':
        user_query = request.form.get('query', '').strip()
        boolean_query = generate_boolean_query(user_query)
        
        for db_name in databases:
            db = client[db_name]
            output[db_name] = {}
            
            if db_name == "medical":
                output[db_name]['research_studies'] = list(retrieve_research_studies(db))
                output[db_name]['medical_records'] = list(filter_medical_records(db, ["fever", "cough"]))
                output[db_name]['drug_interactions'] = list(identify_drug_interactions(db, "aspirin"))
                output[db_name]['diagnostic_data'] = list(access_diagnostic_data(db, ["fever"], ["positive"]))
    
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
