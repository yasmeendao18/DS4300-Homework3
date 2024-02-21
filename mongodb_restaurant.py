# import pymongo
import folium
import pymongo


class RestaurantQueries:
    def __init__(self, collection):
        self.collection = collection

    @staticmethod
    def aggregate_test(collection, pipeline):
        """
        Executes the aggregation in MongoDB
        """
        return collection.aggregate(pipeline)

    @staticmethod
    def count_test(collection, pipeline):
        """
        Executes the countDocuments in MongoDB
        """
        return collection.count_documents(pipeline)

    def num_restaurants(self, borough):
        """
        Count the number of restaurants in a specified borough.
        """
        pipeline = {"borough": borough}
        result = self.count_test(self.collection, pipeline)
        return result

    def lowest_avg_score(self, borough):
        """
        Find the restaurants with the lowest average sanitation score in a specified borough.
        """
        pipeline = [
            {"$match": {"borough": borough}},
            {"$addFields": {"avg_score": {"$avg": "$grades.score"}}},
            {"$match": {"avg_score": {"$exists": True, "$ne": None}}},
            {"$sort": {"avg_score": 1}},
            {"$limit": 10},
            {"$project": {"_id": 0, "name": 1, "avg_score": 1, "borough": 1}}
        ]
        result = self.aggregate_test(self.collection, pipeline)
        return result

    def distance_restaurants(self, lon, lat):
        """
        Find restaurants within 5 miles of a specified location.
        """
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["Restaurant"]
        collection = db["restaurants"]
        collection.create_index([("address.coord", "2dsphere")])
        pipeline = [
            {"$geoNear": {
                "near": {"type": "Point", "coordinates": [lon, lat]},  # Central coordinates
                "distanceField": "distance",
                "maxDistance": 8047,  # 5 miles in meters
                "spherical": True,
                "key": "address.coord"}},
            {"$project": {"_id": 0,
                          "name": 1,
                          "distance": {"$round": [{"$multiply": ["$distance", 0.000621371]}, 2]}}
             }
        ]
        result = self.aggregate_test(self.collection, pipeline)
        return result

    def map_restaurants(self, borough):
        """
        Maps the restaurants in specified NYC boroughs.
        """
        query = {
            "address.coord": {"$type": 1},
            "address.coord.0": {"$exists": True},  # Ensure the first coordinate exists
            "address.coord.1": {"$exists": True},  # Ensure the second coordinate exists
            "borough": borough  # Filter for borough
        }
        projection = {"name": 1, "address.coord": 1, "_id": 0}
        restaurants_borough = self.collection.find(query, projection).limit(5000)

        mymap = folium.Map(location=[40.785091, -73.968285], zoom_start=15)
        for restaurant in restaurants_borough:
            name = restaurant["name"]
            lon, lat = restaurant["address"]["coord"]
            marker_icon = folium.Icon(color='red', icon_size=(15, 15), shadow_size=(0, 0))
            circle_icon = folium.CircleMarker(location=[lat, lon],
                                              radius=3, color='red',
                                              fill=True, fill_color='red',
                                              fill_opacity=.6,
                                              tooltip=name).add_to(mymap)
        return mymap
