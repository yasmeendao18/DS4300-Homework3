import pymongo
import folium
from mongodb_restaurant import RestaurantQueries

if __name__ == "__main__":

    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["restaurant_db"]
    collection = db["mongo_data"]
    restaurant_queries = RestaurantQueries(collection)
    borough = "Manhattan"
    print("Number of restaurants in", borough, ":", restaurant_queries.num_restaurants(borough))

    print("Restaurants with lowest average score in", borough, ":", list(restaurant_queries.lowest_avg_score(borough)))

    # Restaurants within 5 miles of a specified location
    lon, lat = -73.985428, 40.748817
    nearby_restaurants = restaurant_queries.distance_restaurants(lon, lat)
    print("Restaurants within 5 miles of the specified location:")
    for i, restaurant in enumerate(nearby_restaurants):
        if i >= 10:
            break
        print(restaurant)


