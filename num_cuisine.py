from pymongo import MongoClient
from datetime import datetime


def count_restaurants_per_cuisine():
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Restaurant']
    collection = db['ds4300']

    # Group restaurants by cuisine and count them
    pipeline = [
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$limit": 10} # go back and organize the groupings from least to greatest
    ]
    results = collection.aggregate(pipeline)

    # result dictionary
    restaurant_counts = {}
    for result in results:
        restaurant_counts[result['_id']] = result['count']

    return restaurant_counts


if __name__ == "__main__":
    counts = count_restaurants_per_cuisine()
    for cuisine, count in counts.items():
        print(f"{cuisine}: {count} restaurants")