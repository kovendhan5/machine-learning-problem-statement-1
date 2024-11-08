import pandas as pd
import spacy
import string  # Importing string module for punctuation handling
from flask import Flask, request, render_template

# Load spaCy's English NLP model
nlp = spacy.load("en_core_web_sm")

# Load your dataset
df = pd.read_csv('dataset.csv')  # Replace with your dataset file path

# Check if DataFrame is empty
if df.empty:
    print("The DataFrame is empty. Please check your CSV file.")
else:
    # Display the first few rows of the dataset and its columns
    print(df.head())
    print("Columns in DataFrame:", df.columns)

    # Preprocessing function
    def preprocess_text(text):
        if pd.isna(text):  # Check for NaN values
            return ""
        doc = nlp(text)
        tokens = [
            token.lemma_ for token in doc 
            if token.text not in spacy.lang.en.stop_words.STOP_WORDS and token.text not in string.punctuation
        ]
        return " ".join(tokens)

    # Apply preprocessing to the dataset
    if 'Title' in df.columns:  # Adjust according to actual column name
        df['processed_text'] = df['Title'].apply(preprocess_text)
    else:
        print("No suitable column found for text processing.")

# Function to generate Boolean query
def generate_boolean_query(user_input):
    terms = user_input.split(',')
    boolean_query = " AND ".join([term.strip() for term in terms])
    return boolean_query

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    user_input = request.form['terms']
    boolean_query = generate_boolean_query(user_input)
    
    # Debugging output
    print("Generated Boolean Query:", boolean_query)  # Print the generated query
    
    # Search logic
    # Use regex to match terms; replace ' AND ' with '|'
    results = df[df['processed_text'].str.contains(boolean_query.replace(' AND ', '|'), case=False)]
    
    print(f"Number of results found: {len(results)}")  # Print number of results found
    
    if len(results) == 0:
        print("No results found for the given query.")  # Inform if no results are found
    else:
        print("Results found:", results[['Title', 'processed_text']].head())  # Print a sample of found results
    
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)