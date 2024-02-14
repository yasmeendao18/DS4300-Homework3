from pymongo import MongoClient
import restaurant_queries

def main():
    # connecting to the Mongo
    client = MongoClient("mongodb://localhost:27017")
    print("connected")
    db = client.Restaurant

    # Example usage:
    restaurant_counts = restaurant_queries.restaurant_in_borough(db)
    print(restaurant_counts)

    result = restaurant_queries.get_grade("C", "Manhattan")
    print(result)

    borough_name = "Manhattan"
    stats = restaurant_queries.restaurant_stats(borough_name)
    print("Grade counts for each grade:", stats["grade_counts"])
    print("List of zip codes in", borough_name + ":", stats["zip_codes"])

    # Example usage:
    filtered_cuisines = restaurant_queries.filter_cuisines(min_count_threshold=200)
    restaurant_queries.plot_cuisine_pie_chart(filtered_cuisines)
if __name__ == "__main__":
    main()