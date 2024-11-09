import streamlit as st
from pymongo import MongoClient
import spacy
import pandas as pd

# Load spacy model
nlp = spacy.load("en_core_web_sm")

# MongoDB connection string
mongo_uri = "mongodb+srv://bejistojoseph801:mongodb2003@cluster0.aq48n.mongodb.net/"
client = MongoClient(mongo_uri)

# Function to preprocess text
def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return " ".join(tokens)

# Function to generate Boolean query
def generate_boolean_query(user_query):
    doc = nlp(user_query)
    keywords = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return " AND ".join(keywords)

# Function to retrieve research studies
def retrieve_research_studies(db):
    return list(db['research_studies'].find())

# Function to filter medical records by symptoms
def filter_medical_records(db, symptoms):
    query = {"symptoms": {"$in": symptoms}}
    return list(db['medical_records'].find(query))

# Function to identify drug interactions
def identify_drug_interactions(db, drug_name):
    query = {"drug_name": drug_name}
    return list(db['drug_interactions'].find(query))

# Function to access diagnostic data
def access_diagnostic_data(db, symptoms, lab_results):
    query = {
        "symptoms": {"$in": symptoms},
        "lab_results": {"$in": lab_results}
    }
    return list(db['diagnostic_data'].find(query))

# Streamlit UI
st.title("AI-Driven Boolean Query Generator for Healthcare")

user_query = st.text_input("Enter your query:")
if st.button("Search"):
    if user_query:
        boolean_query = generate_boolean_query(user_query)
        st.write(f"Generated Boolean Query: {boolean_query}")
        
        # Connect to databases and display data in table format
        db = client["medical"]
        
        # Display Research Studies
        st.write("### Research Studies")
        research_studies = retrieve_research_studies(db)
        if research_studies:
            df_research_studies = pd.DataFrame(research_studies)
            st.dataframe(df_research_studies)
        else:
            st.write("No research studies found.")
        
        # Display Medical Records by Symptoms
        st.write("### Medical Records by Symptoms")
        medical_records = filter_medical_records(db, ["fever", "cough"])
        if medical_records:
            df_medical_records = pd.DataFrame(medical_records)
            st.dataframe(df_medical_records)
        else:
            st.write("No medical records found.")
        
        # Display Drug Interactions
        st.write("### Drug Interactions")
        drug_interactions = identify_drug_interactions(db, "aspirin")
        if drug_interactions:
            df_drug_interactions = pd.DataFrame(drug_interactions)
            st.dataframe(df_drug_interactions)
        else:
            st.write("No drug interactions found.")
        
        # Display Diagnostic Data
        st.write("### Diagnostic Data")
        diagnostic_data = access_diagnostic_data(db, ["fever"], ["positive"])
        if diagnostic_data:
            df_diagnostic_data = pd.DataFrame(diagnostic_data)
            st.dataframe(df_diagnostic_data)
        else:
            st.write("No diagnostic data found.")
