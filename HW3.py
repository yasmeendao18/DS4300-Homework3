#!/usr/bin/env python
# coding: utf-8

# In[6]:


'''
Restaurant Queries API. Queries that answer questions regarding the restaruant DB. 
'''

import pymongo
import folium

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["restaurant_db"]
collection = db["mongo_data"]



# In[7]:


# How many restaurants are in Manhattan?

# Define the count pipeline
pipeline = { "borough": "Manhattan" }

# Execute the count pipeline
result = collection.count_documents(pipeline)

print(result)


# In[9]:


# What are the restaurants with the best average sanitation score in the Bronx?
# Note: Lower score = Better Sanitation; Restaurants with a score between 0 and 13 points earn an A, those with 14 to 27 points receive a B and those with 28 or more a C.

pipeline = [
    {"$match": {"borough": "Bronx"}},
    {"$addFields": {"avg_score": {"$avg": "$grades.score"}}},
    {"$match": {"avg_score": {"$exists": True, "$ne": None}}},
    {"$sort": {"avg_score": 1}},
    {"$limit": 10},
    {"$project": {"_id": 0, "name": 1, "avg_score": 1, "borough": 1}}
]

# Execute the aggregation pipeline
result = collection.aggregate(pipeline)

print(result)

# Print the results
print("# What are the restaurants with the best average sanitation score in the Bronx?")
for restaurant in result:
    print(restaurant)


# In[12]:


# What restaurants are within 5 miles of the Empire State Building?
pipeline = [
    {"$geoNear": {
        "near": {"type": "Point", "coordinates": [-73.985428, 40.748817]}, # Coordinates of the Empire State Building
        "distanceField": "distance",
        "maxDistance": 8047,
        "spherical": True,
        "key": "address.coord"}},
    {"$project": {"_id": 0,
                  "name": 1,
                  "distance": {"$round": [{"$multiply": ["$distance", 0.000621371]}, 2]} # Convert meters to miles 
                 }}
]

# Execute the aggregation pipeline
result = collection.aggregate(pipeline)


# Print the top 10 results
for i, restaurant in enumerate(result):
    if i >= 10:
        break
    print(restaurant)


# In[15]:


# Visualize the number of restuarants in Mahattan

# Retrieve data with latitude, longitude for restaurants in Manhattan
query = {
    "address.coord": {"$type": 1},  # Filter for fields with BSON type 1 (double)
    "address.coord.0": {"$exists": True},  # Ensure the first coordinate exists
    "address.coord.1": {"$exists": True},  # Ensure the second coordinate exists
    "borough": "Manhattan"  # Filter for borough equal to "Manhattan"
}

# Projection to include necessary fields (name, latitude, longitude, borough)
projection = {"name": 1, "address.coord": 1, "_id": 0}

# Retrieve data
restaurants_manhattan = collection.find(query, projection).limit(5000)  # Limit to the first 5000 resturants due to rendering limitations

# Initialize the map at Central Park
mymap = folium.Map(location=[40.785091, -73.968285], zoom_start=15)

# Iterate through the restaurants and add markers to the map
for restaurant in restaurants_manhattan:
    name = restaurant["name"]
    lon, lat= restaurant["address"]["coord"]
    
    # Create a marker for each restaurant
    marker_icon = folium.Icon(color='red', icon_size=(15, 15), shadow_size=(0,0))
    circle_icon = folium.CircleMarker(location=[lat, lon], 
                                      radius=3, color='red', 
                                      fill=True, fill_color='red', 
                                      fill_opacity=.6, 
                                      tooltip=name).add_to(mymap)


# Display the map
mymap


# In[ ]:




