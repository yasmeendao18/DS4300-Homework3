"Queries that answer the questions"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

# connect to Mongo
client = MongoClient("mongodb://localhost:27017")
db = client['Restaurant']

# define collection
restaurants = db['Restaurants']


# what restaurants are in X zipcode?
def get_restaurants_in_zipcode(zipcode):
    zipcode_query = {"address.zipcode": zipcode}

    result = restaurants.find(zipcode_query)

    return result


#  what are the most recent scores for each restaurant?
def most_recent_scores(db, collection):
    pipeline = [
        {"$unwind": "$grades"},
        {"$sort": {"grades.date": -1}},
        {"$group": {"_id": "$restaurant_id", "name": {"$first": "$name"},
                    "most_recent_grade.grade": {"$first": "$grades"}}},
        {"$project": {"_id": 0, "restaurant_id": "$_id", "name": 1, "grade": "$most_recent_grade.grade",
                      "score": "$most_recent_grade.score"}}
    ]

    result = restaurants.aggregate(pipeline)

    return result


# Bar chart for top ten restaurant scores
# def plot_top_ten_scores_bar(top_ten):
#     name = [restaurant['name'] for restaurant in top_ten]
#     avg_score = [restaurant['average_score']for restaurant in top_ten]
#     plt.barh(name, avg_score, color='blue')
#     plt.xlabel('Average Score')
#     plt.ylabel('Restaurant Name')
#     plt.title('Top Ten Restaurants by Average Score')
#     plt.show()


#  histogram of most recent grades
def recent_scores_hist(scores):
    plt.hist(scores, bins=range(0, max(scores) + 1), edgecolor='black', alpha=0.6)
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.title('Histogram of Most Recent Scores')
    plt.grid(True)
    plt.show()


# def recent_scores_heatmap(scores):
#     max_score = max(scores)
#     score_counts = np.zeros((max_score + 1,))
#
#     for score in scores:
#         score_counts[score] += 1
#
#     plt.imshow(score_counts.reshape(1, -1), cmap='hot', aspect='auto', extent=[0, max_score, 0, 1])
#     plt.colorbar(label='Frequency')
#     plt.xlabel('Score')
#     plt.ylabel('Frequency')
#     plt.title('Heatmap of Most Recent Scores')
#     plt.show()
