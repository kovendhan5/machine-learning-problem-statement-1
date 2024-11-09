from flask import Flask, request, render_template
import pandas as pd
import re

app = Flask(__name__)

# Load the dataset (ensure it's not empty and handle potential errors)
try:
    df = pd.read_csv('dataset.csv')
    if df.empty:
        raise ValueError("Dataset is empty. Please check your CSV file.")
except FileNotFoundError:
    print("Error: 'dataset.csv' not found.")
    exit() # or handle the error in a way that makes sense for your app
except pd.errors.ParserError:
    print("Error: Could not parse 'dataset.csv'. Check the file format.")
    exit()
except Exception as e: # Catch general exceptions during file loading
    print(f"An unexpected error occurred while loading the dataset: {e}")
    exit()

# Preprocessing function (moved outside the search function for efficiency)
def preprocess_text(text):
    if pd.isna(text):
        return ""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters and punctuation
    text = text.lower() # Lowercase the text
    return text




# Preprocess relevant columns for searching efficiency.
for col in ['Title', 'Abstract']:  # Preprocess columns applicable for your data
    if col in df.columns:
        df[f'processed_{col}'] = df[col].apply(preprocess_text)



@app.route('/')
def home():
    return render_template('newindex.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get("keywords")
    if not query:  # Handle empty queries
        message = "Please enter search keywords."
        return render_template('newresults.html', tables=None, message=message, keywords=None)


    query = query.upper()
    and_parts = [part.strip() for part in query.split(" AND ")]
    
    filtered_df = df.copy() # Start with the full dataset
    
    for part in and_parts:
        or_keywords = [kw.strip() for kw in part.split(" OR ")]

        # Create a boolean mask for the current AND part
        combined_mask = pd.Series(False, index=filtered_df.index)  # Initialize to all False

        for kw in or_keywords:
             # Use the preprocessed columns for efficiency
            title_mask = filtered_df[f'processed_Title'].str.contains(preprocess_text(kw), case=False, na=False, regex=False) if 'processed_Title' in filtered_df else pd.Series(False, index=filtered_df.index)
            abstract_mask = filtered_df[f'processed_Abstract'].str.contains(preprocess_text(kw), case=False, na=False, regex=False) if 'processed_Abstract' in filtered_df else pd.Series(False, index=filtered_df.index)

            # Combine the title and abstract matches
            combined_mask = combined_mask | title_mask | abstract_mask  # Give higher priority to Title matches


        # Apply the mask to the DataFrame for the current AND part
        filtered_df = filtered_df[combined_mask]

    if filtered_df.empty:
        message = "No results found for the given keywords."
        return render_template('newresults.html', tables=None, message=message, keywords=query)


    return render_template('newresults.html', tables=[filtered_df.to_html(classes='data')], keywords=query, num_results=len(filtered_df)) # Include the number of results



if __name__ == '__main__':
    app.run(debug=True)