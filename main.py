import numpy as np
from matplotlib import pyplot as plt
from pymongo import MongoClient

import queries

def main():
    # create client
    client = MongoClient("mongodb://localhost:27017")
    db = client['Restaurant']

    # define collection
    collection = db['restaurants']

    # example usage
    # get restaurant by zipcode
    zipcode = input("Enter zip code: ")
    restaurants = queries.get_restaurants_in_zipcode(zipcode)
    if restaurants:
        print("Restaurants in zipcode", zipcode, ":")
        for restaurant in restaurants:
            print(restaurant)
    else:
        print("No restaurants found in zipcode", zipcode)

    # print the most recent scores
    print("Most recent scores for each restaurant:")
    recent_scores = queries.most_recent_scores(db, collection)

    for score in recent_scores:
        print(score)

    # print bar chart
    # queries.plot_top_ten_scores_bar()

    # extract the scores and filter out None values
    scores = [score['score'] for score in recent_scores if score['score'] is not None]
    # print histogram
    queries.recent_scores_hist(scores)


    # Heatmap option
    bins = np.arange(0, max(scores) + 1, 1)
    # fig, ax = plt.subplots()
    # ax.set_facecolor('lightgray')
    # # Create heatmap
    # plt.hist2d(scores, scores, bins=bins, cmap='YlOrRd')
    # plt.colorbar(label='Frequency')
    # plt.xlabel('Scores')
    # plt.ylabel('Scores')
    # plt.title('Heatmap of Most Recent Scores')
    # plt.show()

    # Box plot option
    # recent_scores = queries.most_recent_scores(db, collection)
    #
    # # extract the scores and filter out None values
    # scores = [score['score'] for score in recent_scores if score['score'] is not None]
    #
    # # create a box plot
    # plt.boxplot(scores)
    # plt.xlabel('Scores')
    # plt.ylabel('Score Distribution')
    # plt.title('Box Plot of Most Recent Scores')
    # plt.show()


if __name__ == "__main__":
    main()
