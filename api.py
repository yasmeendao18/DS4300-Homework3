from pymongo import MongoClient
import matplotlib.pyplot as plt

def restaurants_per_cuisine():
    # Connect to the MongoDB database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Restaurant']
    collection = db['ds4300']

    # Group restaurants by cuisine and count
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

    # error handling for plotting
    try:
        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    top_health_inspection_years()

def plot_health_inspections_per_year():
    # Get the top health inspection years
    top_years = top_health_inspection_years()

    # Extract years and counts from the results
    years = [result['_id'] for result in top_years]
    counts = [result['count'] for result in top_years]

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(years, counts, color='skyblue')
    plt.title('Top 10 Years for Health Inspections')
    plt.xlabel('Year')
    plt.ylabel('Number of Inspections')
    plt.xticks(years)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_health_inspections_per_year()

def borough_avg_score(borough_name):
    try:
        # Connect to MongoDB database
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Restaurant']
        collection = db['ds4300']

        pipeline = [
            {"$match": {"borough": borough_name}},  # Match documents for the specified borough
            {"$unwind": "$grades"},  # Deconstruct the grades array
            {"$group": {
                "_id": "$restaurant_id",
                "scores": {"$push": "$grades.score"}
            }}
        ]

        result = list(collection.aggregate(pipeline))
        if result:
            scores_per_borough = [score for restaurant in result for score in restaurant["scores"] if score is not None]
            return scores_per_borough
        else:
            return []
    except Exception as e:
        print("An error occurred:", e)
        return []


def plot_borough_avg_score():
    try:
        borough_names = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
        all_scores = []

        for borough_name in borough_names:
            scores = borough_avg_score(borough_name)
            all_scores.append(scores)

        plt.figure(figsize=(10, 6))
        plt.boxplot(all_scores, labels=borough_names)
        plt.title('Scores Distribution by Borough')
        plt.xlabel('Borough')
        plt.ylabel('Score')
        plt.grid(True)
        plt.show()
    except Exception as e:
        print("An error occurred while plotting:", e)

# call function to plot
if __name__ == "__main__":
    plot_borough_avg_score()

