"Queries that answer the questions"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

# connect to Mongo
client = MongoClient("mongodb://localhost:27017")
db = client['Restaurant']

# define collection
collection = db['restaurants']


# what restaurants are in X zipcode?
def get_restaurants_in_zipcode(zipcode):
    pipeline = [
        {"$match": {"address.zipcode": zipcode}},
        {"$project": {"_id": 0, "name": 1}}
    ]
    result = collection.aggregate(pipeline)
    restaurant_name = [restaurant['name'] for restaurant in result]
    return restaurant_name


#  what are the most recent scores for each restaurant?
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


# bar chart for top ten restaurant scores
def plot_top_ten_scores_bar(top_ten):
    name = [restaurant['name'] for restaurant in top_ten]
    avg_score = [restaurant['average_score'] for restaurant in top_ten]
    plt.barh(name, avg_score, color='blue')
    plt.xlabel('Average Score')
    plt.ylabel('Restaurant Name')
    plt.title('Top Ten Restaurants by Average Score')
    plt.show()


#  histogram of most recent grades
def recent_scores_hist(scores, bins=10, color='blue'):
    plt.hist(scores, bins=bins, color=color, edgecolor='black')
    plt.xlabel('Scores')
    plt.ylabel('Frequency')
    plt.title('Histogram of Most Recent Scores')
    plt.show()
