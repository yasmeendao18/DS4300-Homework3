'''
Matt's Restaurant Queries API. Queries that answer questions. Made some functions that can be used for a user to easily get a certain question
answered. The functions were made to be customizable.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# connecting to the Mongo
client = MongoClient("mongodb://localhost:27017")
db = client['Restaurant']
collection = db['restaurants']


def restaurant_in_borough(db):
    """
        Retrieves the count of restaurants in each borough.

        Args:
            db: MongoDB database object.

        Returns:
            List of dictionaries containing the count of restaurants in each borough.
        """
    pipeline = [
        {"$group": {"_id": "$borough", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = collection.aggregate(pipeline)
    return list(result)


def get_grade(grade, borough):
    """
        Retrieves restaurants with a specific grade in a given borough.

        Args:
            grade: The grade to filter by.
            borough: The borough to filter by.

        Returns:
            List of documents containing the restaurant name, cuisine, and matching grade.
        """
    query = {"grades.grade": grade, "borough": borough}
    result = collection.find(query, {"name": 1, "grades":
        {"$elemMatch": {"grade": grade}}, "cuisine": 1, "_id": 0}).sort("name", 1)

    matched_documents = []
    for doc in result:
        # Filter out grades other than 'C' if present
        doc_grades = [g for g in doc['grades'] if g['grade'] == grade]
        # Replace 'grades' field with filtered grades
        doc['grades'] = doc_grades
        matched_documents.append(doc)

    return matched_documents


def restaurant_stats(borough_name):
    """
        Retrieves statistics about restaurant grades and zip codes in a specific borough.

        Args:
            borough_name: The name of the borough.

        Returns:
            Dictionary containing grade counts and zip codes in the specified borough.
    """
    pipeline = [
        {"$match": {"borough": borough_name}},
        {"$unwind": "$grades"},
        {"$group": {
            "_id": {"restaurant_id": "$restaurant_id", "grade": "$grades.grade"},
            "zip_codes": {"$addToSet": "$address.zipcode"}
        }},
        {"$group": {
            "_id": "$_id.grade", 
            "grade_count": {"$sum": 1}, 
            "zip_codes": {"$addToSet": "$zip_codes"} 
        }},
        {"$sort": {"_id": 1}}
    ]

    result = list(collection.aggregate(pipeline))
    if result:
        # Convert the result to a dictionary for easier access
        grade_counts = {item["_id"]: item["grade_count"] for item in result}
        return {
            "grade_counts": grade_counts,
            "zip_codes": result[0]["zip_codes"]  
        }
    else:
        return {
            "grade_counts": {},
            "zip_codes": []
        }


def filter_cuisines(min_count_threshold=100):
    """
        Filters cuisines based on a minimum count threshold.

        Args:
            min_count_threshold: The minimum count threshold for filtering cuisines.

        Returns:
            Dictionary containing filtered cuisines and their respective counts.
    """
    pipeline = [
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": min_count_threshold}}},
        {"$sort": {"count": -1}}
    ]
    result = collection.aggregate(pipeline)

    cuisine_mapping = {
        "Italian": ["Pizza", "Pizza/Italian", "Ice Cream, Gelato, Yogurt, Ices"],
        "American": ["American", "Burgers", "Hotdogs", "Hamburgers", "Chicken", "Steak", "Barbecue", "Donuts",
                     "Bagels/Pretzels", "Sandwiches/Salads/Mixed Buffet", "Delicatessen"],
        "Chinese": ["Chinese", "Chinese/Japanese"],
        "Other": ["Juice, Smoothies, Fruit Salads", "Sandwiches"]
    }

    filtered_cuisines = {}
    for doc in result:
        cuisine = doc["_id"]
        count = doc["count"]
        # Check if cuisine is mapped to a broader category
        for main_cuisine, sub_cuisines in cuisine_mapping.items():
            if cuisine in sub_cuisines:
                cuisine = main_cuisine
                break
        # Update count for the cuisine
        if cuisine in filtered_cuisines:
            filtered_cuisines[cuisine] += count
        else:
            filtered_cuisines[cuisine] = count

    return filtered_cuisines


def plot_cuisine_pie_chart(filtered_cuisines):
    """
        Plots a pie chart showing the distribution of cuisines.

        Args:
            filtered_cuisines: Dictionary containing filtered cuisines and their respective counts.

        Returns:
            None
    """
    labels = filtered_cuisines.keys()
    sizes = filtered_cuisines.values()
    # Explode all slices for better visibility
    explode = [0.1] * len(labels)

    plt.figure(figsize=(10, 10))
    patches, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=140,textprops=dict(color="black",fontsize=10))
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    plt.title('Distribution of Cuisines')

    # Adjust legend font size
    plt.setp(autotexts, size="x-small")

    plt.show()
