from pymongo import MongoClient

import queries


def main():
    # create client
    client = MongoClient("mongodb://localhost:27017")
    db = client['Restaurant']

    # define collection
    restaurants = db.restaurants

    # example usage
    # get restaurant by zipcode
    zipcode = input("Enter zip code: ")
    result = queries.get_restaurants_in_zipcode(zipcode)
    print("Restaurants in" + zipcode + "are" + result)

    # get most recent scores for each restaurant
    recent_scores = queries.most_recent_scores(db, restaurants)
    print("Most recent scores for each restaurant:" + recent_scores)

    # plots
    queries.recent_scores_hist(recent_scores)
    # queries.plot_top_ten_scores_bar()


if __name__ == "__main__":
    main()
