"Lilian and Yasmeen's restaurant queries API that answer the questions"

import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

# connect to Mongo
client = MongoClient("mongodb://localhost:27017")
db = client['Restaurant']

# define collection
collection = db['restaurants']


def restaurants_per_cuisine():
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


def top_health_inspection_years():
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


def plot_health_inspections_per_year():
    # Get the top health inspection years
    top_years = top_health_inspection_years()

    # Extract years and counts from the results
    years = [result['_id'] for result in top_years]
    counts = [result['count'] for result in top_years]

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(years, counts, color='skyblue')
    plt.title('Number of Health Inspections per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Inspections')
    plt.xticks(years)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()


def borough_avg_score(borough_name):
    try:
        # Connect to MongoDB database
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Restaurant']
        collection = db['restaurants']

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


def get_restaurants_in_zipcode(zipcode):
    """
     restaurants in X zipcode
     """
    pipeline = [
        {"$match": {"address.zipcode": zipcode}},
        {"$project": {"_id": 0, "name": 1}}
    ]
    result = collection.aggregate(pipeline)
    restaurant_name = [restaurant['name'] for restaurant in result]
    return restaurant_name


#  question 9 what are the most recent scores for each restaurant?
def most_recent_scores(db, collection):
    pipeline = [
        {"$unwind": "$grades"},
        {"$sort": {"grades.date": -1}},
        {"$group": {"_id": "$restaurant_id", "name": {"$first": "$name"},
                    "most_recent_grade": {"$first": "$grades"}}},
        {"$project": {"_id": 0, "restaurant_id": "$_id", "name": 1,
                      "grade": "$most_recent_grade.grade",
                      "score": "$most_recent_grade.score"}}
    ]
    result = list(collection.aggregate(pipeline))
    return result


def get_top_ten_scores(collection):
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
    top_restaurants = list(collection.aggregate(pipeline))
    return top_restaurants


# bar chart for top ten restaurant scores
def plot_top_ten_scores_bar(top_ten):
    """
         bar chart for scores
    """
    name = [restaurant['name'] for restaurant in top_ten]
    avg_score = [restaurant['average_score'] for restaurant in top_ten]

    num_bars = len(name)

    # Generate a gradient of green colors
    colors = plt.cm.get_cmap('Oranges')(np.linspace(1, 0, num_bars))

    plt.figure(figsize=(20, 10))
    bars = plt.barh(name, avg_score, color=colors)
    plt.xlabel('Average Score')
    plt.ylabel('Restaurant Name')
    plt.title('Top Ten Restaurants with Highest Average Score')
    plt.grid()
    plt.gca().set_axisbelow(True)
    # Add values inside the bars
    for bar, value in zip(bars, avg_score):
        plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, '{:.2f}'.format(value),
                 va='center', ha='left', fontsize=10, color='black')
    plt.show()


def recent_scores_hist(scores, bins=18, color='slateblue', alpha=1):
    """
        histogram of most recent grades
    """
    plt.hist(scores, bins=bins, color=color, edgecolor='black', alpha=alpha)
    plt.xlabel('Scores')
    plt.ylabel('Frequency')
    plt.title('Histogram of Most Recent Scores')
    plt.gca().set_axisbelow(True)
    plt.xticks(range(0, max(scores) + 1, 10))
    plt.grid()
    plt.show()
