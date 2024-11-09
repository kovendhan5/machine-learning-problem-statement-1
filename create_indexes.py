from pymongo import MongoClient

# Connect to MongoDB
mongo_uri = "mongodb+srv://bejistojoseph801:mongodb2003@cluster0.aq48n.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["medical1"]

# Define collections and fields for text indexing
collections_to_index = {
    "research_studies": ["title", "abstract"],
    "medical_records": ["notes", "description"],
    "drug_interactions": ["drug_name", "interaction_description"],
    "diagnostic_data": ["test_name", "result_description"]
}

# Create text indexes
for collection_name, fields in collections_to_index.items():
    collection = db[collection_name]
    index_spec = [(field, "text") for field in fields]
    try:
        collection.create_index(index_spec, name=f"{collection_name}_text_index")
        print(f"Text index created on fields {fields} in collection {collection_name}.")
    except Exception as e:
        print(f"Error creating index for {collection_name}: {e}")
