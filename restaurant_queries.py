'''
Restaurant Queries API. Queries that answer questions. Made some functions that can be used for a user to easily get a certain question
answered. The functions were made to be customizable.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# connecting to the Mongo
client = MongoClient("mongodb://localhost:27017")
db = client.Restaurant


# Which borough has the most restaurants?
# Define the aggregation pipeline
pipeline = [
    { "$group": { "_id": "$borough", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
]

# Execute the aggregation pipeline
result = db.food.aggregate(pipeline)

# Print the result
#for doc in result:
#    print(doc)


#  What are the top 10 restaurants with the highest average score
pipeline = [
    {"$unwind": "$grades"},
    {"$group": {
        "_id": "$_id",
        "name": {"$first": "$name"},
        "average_score": {"$avg": "$grades.score"},
        "cuisine": {"$first": "$cuisine"}
    }},
    {"$sort": {"average_score": -1}},
    {"$limit": 10}
]
top_restaurants = db.food.aggregate(pipeline)

# for doc in top_restaurants:
#    print(doc)


def restaurant_in_borough(db):
    pipeline = [
        {"$group": {"_id": "$borough", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = db.food.aggregate(pipeline)
    return list(result)

def get_grade(grade, borough):
    query = {"grades.grade": grade, "borough": borough}
    result = db.food.find(query, {"name": 1, "grades":
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
    pipeline = [
        {"$match": {"borough": borough_name}},  # Match documents for the specified borough
        {"$unwind": "$grades"},  # Deconstruct the grades array
        {"$group": {
            "_id": {"restaurant_id": "$restaurant_id", "grade": "$grades.grade"},  # Group by restaurant_id and grade
            "zip_codes": {"$addToSet": "$address.zipcode"}  # Collect unique zip codes for the borough
        }},
        {"$group": {
            "_id": "$_id.grade",  # Group by grade to count occurrences of each grade
            "grade_count": {"$sum": 1},  # Count occurrences of each grade
            "zip_codes": {"$addToSet": "$zip_codes"}  # Collect all zip codes in the borough
        }},
        {"$sort": {"_id": 1}}  # Sort grades alphabetically
    ]

    result = list(db.food.aggregate(pipeline))
    if result:
        # Convert the result to a dictionary for easier access
        grade_counts = {item["_id"]: item["grade_count"] for item in result}
        return {
            "grade_counts": grade_counts,
            "zip_codes": result[0]["zip_codes"]  # Assuming all zip codes are the same across the borough
        }
    else:
        return {
            "grade_counts": {},
            "zip_codes": []
        }

def filter_cuisines(min_count_threshold=100):
    pipeline = [
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": min_count_threshold}}},
        {"$sort": {"count": -1}}
    ]
    result = db.food.aggregate(pipeline)

    cuisine_mapping = {
        "Italian": ["Pizza", "Pizza/Italian", "Ice Cream, Gelato, Yogurt, Ices"],
        "American": ["American", "Burgers", "Hotdogs", "Hamburgers", "Chicken", "Steak",
                     "Barbecue", "Donuts", "Bagels/Pretzels"],
        "Chinese": ["Chinese", "Chinese/Japanese"],
        # Add more mappings as needed
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
    labels = filtered_cuisines.keys()
    sizes = filtered_cuisines.values()
    explode = [0.1] * len(labels)  # Explode all slices for better visibility

    plt.figure(figsize=(8, 8))
    patches, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=140,
                                        textprops=dict(color="black",
                                                       fontsize=10))  # Set font color and size for percentages

    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Distribution of Cuisines')

    # Adjust legend font size
    plt.setp(autotexts, size="x-small")

    plt.show()


