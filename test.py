from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('dataset.csv')

@app.route('/')
def home():
    return render_template('newindex.html')

@app.route('/search', methods=['POST'])
def search():
    # Get the keywords entered by the user
    query = request.form.get("keywords")

    # Split the query based on AND/OR and strip spaces
    query = query.upper()  # Standardize to uppercase for easier handling
    and_parts = [part.strip() for part in query.split(" AND ")]
    
    # Initialize the filtered DataFrame to include all rows initially
    filtered_df = df.copy()

    for part in and_parts:
        # Each `part` can have multiple "OR" keywords
        or_keywords = [kw.strip() for kw in part.split(" OR ")]

        # Apply filter where at least one of the OR keywords is present in the row
        filtered_df = filtered_df[
            filtered_df.apply(lambda row: any(row.astype(str).str.contains(kw, case=False, regex=True).any() for kw in or_keywords), axis=1)
        ]

    # Check if any rows are left after filtering
    if filtered_df.empty:
        message = "No results found for the given keywords."
        return render_template('newresults.html', tables=None, message=message, keywords=query)

    return render_template('newresults.html', tables=[filtered_df.to_html()], keywords=query)



if __name__ == '__main__':
    app.run(debug=True)