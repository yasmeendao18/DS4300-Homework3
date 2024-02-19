from pymongo import MongoClient

def restaurants_per_cuisine():
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Restaurant']
    collection = db['ds4300']

    # Group restaurants by cuisine and count them
    pipeline = [
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = collection.aggregate(pipeline)

    # result dictionary
    restaurant_counts = {}
    for result in results:
        restaurant_counts[result['_id']] = result['count']

    return restaurant_counts


if __name__ == "__main__":
    counts = restaurants_per_cuisine()
    for cuisine, count in counts.items():
        print(f"{cuisine}: {count} restaurants")


def top_health_inspection_years():
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Restaurant']
    collection = db['ds4300']

    # Unwind the grades array to get all inspection dates
    pipeline = [
        {"$unwind": "$grades"},
        {"$group": {"_id": {"$year": {
            "$dateFromString": {"dateString": {"$dateToString": {"format": "%Y-%m-%d", "date": "$grades.date"}},
                                "format": "%Y-%m-%d"}}}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}  # Limit the results to the top 10 years
    ]
    results = list(collection.aggregate(pipeline))

    # Print the top ten years with the most health inspections
    for idx, result in enumerate(results, start=1):
        print(f"{idx}. Year: {result['_id']}, Health Inspections: {result['count']}")


if __name__ == "__main__":
    top_health_inspection_years()