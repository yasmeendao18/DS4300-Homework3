"""
Restaurant Queries API. Queries that answer questions regarding the restaruant DB.
"""

import pymongo
import folium

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["restaurant_db"]
collection = db["mongo_data"]


def aggregate_test(collection, pipeline):
    """
    Executes the aggregation in MongoDB

    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection to execute the aggregation pipeline on.
    - pipeline (list): A list of aggregation stages to be executed in sequence.

    Returns:
    - pymongo.command_cursor.CommandCursor: Cursor yielding the result of the aggregation.

    """
    return collection.aggregate(pipeline)


def count_test(collection, pipeline):
    """
    Executes the countDocuments in MongoDB

    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection to execute the countDocuments pipeline on.
    - pipeline (list): A list of stages to be executed in sequence.

    Returns:
    - pymongo.command_cursor.CommandCursor: Cursor yielding the result of the count.
    """
    return collection.count_documents(pipeline)


def num_restaurants(collection, borough):
    """
    Count the number of restaurants in a specified borough.

    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection containing restaurant data.
    - borough (str): The NYC borough for which to count the restaurants.

    Returns:
    - int: The number of restaurants in the specified borough.
    """

    # Define the count pipeline
    pipeline = {"borough": borough}

    # Execute the count pipeline
    result = count_test(collection, pipeline)
    return result


def lowest_avg_score(collection, borough):
    """
    Find the restaurants with the lowest average sanitation score in a specified borough.
        Note: Lower score = Better Sanitation; Restaurants with a score between 0 and 13 points earn an A, those with 14 to 27 points receive a B and those with 28 or more a C.


    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection containing restaurant data.
    - borough (str): The NYC borough for which to find the restaurants.

    Returns:
    - list of dict: A list of dictionaries containing information about the restaurants with the lowest average sanitation score.
      Each dictionary includes 'name', 'avg_score', and 'borough'.

    """

    pipeline = [
        {"$match": {"borough": borough}},
        {"$addFields": {"avg_score": {"$avg": "$grades.score"}}},
        {"$match": {"avg_score": {"$exists": True, "$ne": None}}},
        {"$sort": {"avg_score": 1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "name": 1, "avg_score": 1, "borough": 1}}
    ]

    # Execute the aggregation pipeline
    result = aggregate_test(collection, pipeline)
    return result


def distance_restaurants(collection, lon, lat):
    """
    Find restaurants within 5 miles of a specified location.

    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection containing restaurant data.
    - lon (float): The longitude of the specified location.
    - lat (float): The latitude of the specified location.

    Returns:
    - list of dict: A list of dictionaries containing information about restaurants near the specified location.
      Each dictionary includes 'name' and 'distance'(miles).
    """

    pipeline = [
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": [lon, lat]},  # Central coordinates
            "distanceField": "distance",
            "maxDistance": 8047,  # 5 miles in meters
            "spherical": True,
            "key": "address.coord"}},
        {"$project": {"_id": 0,
                      "name": 1,
                      "distance": {"$round": [{"$multiply": ["$distance", 0.000621371]}, 2]}  # Convert meters to miles
                      }}
    ]

    # Execute the aggregation pipeline
    result = aggregate_test(collection, pipeline)
    return result


def map_restaurants(collection, borough):
    """
    Maps the restaurants in specified NYC boroughs.

    Parameters:
    - collection (pymongo.collection.Collection): The MongoDB collection containing restaurant data.
    - borough (str): The NYC borough for which to graph the restaurants.

    Returns:
    - folium.Map: A Folium map object displaying the restaurants in the specified borough.

   """

    # Retrieve data with latitude, longitude for restaurants in Manhattan
    query = {
        "address.coord": {"$type": 1},
        "address.coord.0": {"$exists": True},  # Ensure the first coordinate exists
        "address.coord.1": {"$exists": True},  # Ensure the second coordinate exists
        "borough": borough  # Filter for borough
    }

    # Projection to include necessary fields (name, latitude, longitude)
    projection = {"name": 1, "address.coord": 1, "_id": 0}

    # Retrieve data
    restaurants_manhattan = collection.find(query, projection).limit(5000)  # Limit to the first 5000 restaurants due to rendering limitations

    # Initialize the map at Central Park
    mymap = folium.Map(location=[40.785091, -73.968285], zoom_start=15)

    # Iterate through the restaurants and add markers to the map
    for restaurant in restaurants_manhattan:
        name = restaurant["name"]
        lon, lat= restaurant["address"]["coord"]

        # Create a marker for each restaurant
        marker_icon = folium.Icon(color='red', icon_size=(15, 15), shadow_size=(0, 0))
        circle_icon = folium.CircleMarker(location=[lat, lon],
                                          radius=3, color='red',
                                          fill=True, fill_color='red',
                                          fill_opacity=.6,
                                          tooltip=name).add_to(mymap)

    # Display the map
    return mymap


if __name__ == "__main__":
    print('\nQ1, \nHow many restaurants are in Manhattan?')

    output1 = num_restaurants(collection, "Manhattan")
    print(output1)

    print('\nQ2')
    output2 = lowest_avg_score(collection, "Bronx")
    # Print the results
    print("What are the restaurants with the best average sanitation score in the Bronx?")
    for restaurant in output2:
        print(restaurant)

    print('\nQ3, \nWhat restaurants are within 5 miles of the Empire State Building?')
    output3 = distance_restaurants(collection, -73.985428, 40.748817)
    # Print the top 10 results
    for i, restaurant in enumerate(output3):
        if i >= 10:
            break
        print(restaurant)

    # How many restaurants are there in Manhattan
    map_object = map_restaurants(collection, "Manhattan")
    map_object


