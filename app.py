from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load your dataset
df = pd.read_csv('dataset.csv')  # Replace with your dataset file path

def generate_boolean_query(terms):
    return " AND ".join([f"{term.strip()}" for term in terms])

def search_articles(query):
    return df[df['abstract'].str.contains(query, case=False, na=False)]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    terms = request.form['terms'].split(',')
    boolean_query = generate_boolean_query(terms)
    results = search_articles(boolean_query)
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)