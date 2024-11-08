from pymongo import MongoClient

# MongoDB connection string
mongo_uri = "mongodb+srv://bejistojoseph801:mongodb2003@cluster0.aq48n.mongodb.net/"

# Create a MongoClient
client = MongoClient(mongo_uri)

# List of databases
databases = ["Student_Profile", "medical", "sample_mflix", "admin", "local"]

# Function to retrieve research studies or clinical trial data
def retrieve_research_studies(db):
    results = db['research_studies'].find()
    for result in results:
        print(result)

# Function to filter medical records by patient symptoms or conditions
def filter_medical_records(db, symptoms):
    query = {"symptoms": {"$in": symptoms}}
    results = db['medical_records'].find(query)
    for result in results:
        print(result)

# Function to identify drug interactions or adverse events
def identify_drug_interactions(db, drug_name):
    query = {"drug_name": drug_name}
    results = db['drug_interactions'].find(query)
    for result in results:
        print(result)

# Function to access diagnostic data based on symptoms and lab results
def access_diagnostic_data(db, symptoms, lab_results):
    query = {
        "symptoms": {"$in": symptoms},
        "lab_results": {"$in": lab_results}
    }
    results = db['diagnostic_data'].find(query)
    for result in results:
        print(result)

# Example usage
for db_name in databases:
    db = client[db_name]
    print(f"\nDatabase: {db_name}")

    if db_name == "medical":
        print("Retrieving research studies:")
        retrieve_research_studies(db)

        print("\nFiltering medical records by symptoms ['fever', 'cough']:")
        filter_medical_records(db, ["fever", "cough"])

        print("\nIdentifying drug interactions for 'aspirin':")
        identify_drug_interactions(db, "aspirin")

        print("\nAccessing diagnostic data for symptoms ['fever'] and lab results ['positive']: ")
        access_diagnostic_data(db, ["fever"], ["positive"])

    # Add similar blocks for other databases if needed
