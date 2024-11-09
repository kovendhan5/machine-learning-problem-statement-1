# AI-Driven Boolean Query Generator for Healthcare
This repository contains a solution for building an AI-Driven Boolean Query Generator for Healthcare, implemented in three approaches to streamline search queries for healthcare data. Each method was used to access, process, and filter large datasets effectively, providing search results tailored to healthcare data queries. The system uses APIs, databases, and NLP libraries to generate accurate Boolean queries.

# Overview
The objective of this project is to build a Boolean Query Generator for Healthcare that utilizes various techniques to process and filter data for healthcare applications. This README outlines three approaches implemented to achieve the desired functionality and performance, along with the specific technologies and limitations encountered with each approach.

# Solution Approaches
# 1. ICD API Approach
This approach leverages the ICD API for accessing a vast healthcare dataset. API credentials (Client ID and Client Secret) are required to authenticate and retrieve data. For security, these credentials are stored as environment variables:

```python
CLIENT_ID = os.environ.get("YOUR_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUR_CLIENT_SECRET")
```
Steps:
Set up environment variables to keep API credentials secure.
Use the API to pull data based on healthcare queries.
Generate Boolean queries by processing the retrieved dataset.
Note:
The ICD API key has expired, which limits this method from further use without renewed credentials.

# 2. MongoDB Database with Flask Integration
In this method, the dataset is stored in a MongoDB database and connected to a Flask application. The AI model trained for the Boolean Query Generator retrieves data from the MongoDB database, enabling faster data access and processing within the application.

Steps:
Integrate MongoDB with Flask for data retrieval.
Use AI models to generate Boolean queries on the data stored in MongoDB.
Process and return relevant results based on user inputs.
Note:
The MongoDB time limit has also expired, and a new configuration may be needed for further use.

# 3. Streamlit Application with NLP and Scapy
The final approach utilizes Streamlit for a user-friendly interface, combined with Scapy and other NLP libraries for generating Boolean queries. This setup enables users to input healthcare-related search terms and receive filtered results based on the query.

Steps:
Develop the Streamlit interface for ease of use.
Integrate Scapy and NLP libraries to filter and process search terms.
Return accurate Boolean query results based on the input, tailored for healthcare data.
This Streamlit approach remains functional and continues to generate healthcare-focused Boolean queries accurately based on user inputs.

Getting Started
*Prerequisites*
```
Python 3.8+
Streamlit
Flask
MongoDB
ICD API (if reactivating the first approach)
Scapy and NLP libraries (e.g., SpaCy, NLTK)
```
Installation
Clone this repository:

```bash
git clone https://github.com/kovendhan5/machine-learning-problem-statement-1
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Running the Application
To run the Streamlit app (Approach 3):

```bash
streamlit run app.py
```
To run the Flask app with MongoDB (Approach 2):

```bash
python flaskapp_database.py
```
Usage
Choose one of the three approaches based on available credentials and requirements.
For the Streamlit interface, navigate to the provided URL after starting the app and input healthcare-related terms to generate Boolean queries.
For the Flask and MongoDB setup, use the Flask routes to interact with the AI model.
