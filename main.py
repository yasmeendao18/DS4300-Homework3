from pymongo import MongoClient
from mongodb_restaurant import RestaurantQueries
import matt_restaurant_queries
import yandL_queries


def main():
    client, db = connect_mongoDB()
    # define collection
    collection = db['restaurants']
    y_query_test(db)
    l_query_test()
    m_query_test(db)
    e_query_test(collection)
    plot_other_charts(db, collection)


def connect_mongoDB():
    # create client
    client = MongoClient("mongodb://localhost:27017")
    db = client['Restaurant']
    return client, db


def y_query_test(db):
    # get restaurant by zipcode to test
    zipcode = input("Enter zip code: ")
    restaurants = yandL_queries.get_restaurants_in_zipcode(zipcode)
    if restaurants:
        print("Restaurants in zipcode", zipcode, ":")
        for restaurant in restaurants:
            print(restaurant)
    else:
        print("No restaurants found in zipcode", zipcode)

    # print the most recent scores
    print("Most recent scores for each restaurant:")
    recent_scores = yandL_queries.most_recent_scores(db, db['restaurants'])
    for score in recent_scores:
        print(score)


def l_query_test():
    # print restaurants per cuisine
    counts = yandL_queries.restaurants_per_cuisine()
    for cuisine, count in counts.items():
        print(f"{cuisine}: {count} restaurants")


def m_query_test(db):
    # Example usage:
    restaurant_counts = matt_restaurant_queries.restaurant_in_borough(db)
    print(restaurant_counts)

    result = matt_restaurant_queries.get_grade("C", "Manhattan")
    print(result)

    borough_name = "Manhattan"
    stats = matt_restaurant_queries.restaurant_stats(borough_name)
    print("Grade counts for each grade:", stats["grade_counts"])
    print("List of zip codes in", borough_name + ":", stats["zip_codes"])

    # Example usage:
    filtered_cuisines = matt_restaurant_queries.filter_cuisines(min_count_threshold=200)

    # pie chart
    matt_restaurant_queries.plot_cuisine_pie_chart(filtered_cuisines)


def e_query_test(collection):
    """
    Queries 1,2,10
    Map of restaurants in each borough.
    """
    
    restaurant_queries = RestaurantQueries(collection)
    borough_1 = "Manhattan"
    borough_2 = "Bronx"
    
    # Number of restaurants in Manhattan
    print("Number of restaurants in", borough_1, ":", restaurant_queries.num_restaurants(borough_1))
    
    # Restaurant with lowest average score in the Bronx
    print("Restaurants with lowest average score in", borough_2, ":",
          list(restaurant_queries.lowest_avg_score(borough_2)))

    # Restaurants within 5 miles of a the Empire State Building location
    lon, lat = -73.985428, 40.748817 # Coordinates of the Empire State Building
    nearby_restaurants = restaurant_queries.distance_restaurants(lon, lat)
    print("Restaurants within 5 miles of the specified location:")
    for i, restaurant in enumerate(nearby_restaurants):
        if i >= 10:
            break
        print(restaurant)
    # Map the restaurants for each selected borough
    restaurant_queries.map_restaurants(borough_1).save("map_restaurants.html")
    restaurant_queries.map_restaurants(borough_2).save("map_restaurants2.html")


def plot_other_charts(db, collection):
    yandL_queries.top_health_inspection_years()
    # bar chart
    yandL_queries.plot_health_inspections_per_year()
    # box plot
    yandL_queries.plot_borough_avg_score()

    # print bar chart
    top_ten_scores = yandL_queries.get_top_ten_scores(collection)
    for rest in top_ten_scores:
        print(rest)
    yandL_queries.plot_top_ten_scores_bar(top_ten_scores)

    # print histogram
    recent_scores = yandL_queries.most_recent_scores(db, db['restaurants'])
    # extract the scores and filter out None values
    scores = [score['score'] for score in recent_scores if score['score'] is not None]
    yandL_queries.recent_scores_hist(scores)


if __name__ == "__main__":
    main()
