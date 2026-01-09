import random
from datetime import datetime, timedelta, time as dt_time
from helpers import haversine, travel_minutes

# Define fillers (optional activities)
fillers = [
    {"name":"Street Walk","lat":19.07,"lon":72.87,"category":"Walk","ideal_duration_hours":0.5},
    {"name":"Shopping Time","lat":19.08,"lon":72.88,"category":"Shopping","ideal_duration_hours":1},
]

def insert_filler(day, cur, end, lat, lon, next_meal_time=None):
    if (end - cur).total_seconds() < 30*60:
        return cur, lat, lon
    if next_meal_time and cur >= next_meal_time - timedelta(hours=1):
        return cur, lat, lon  # skip filler near meal

    f_type = random.choice(fillers)
    delta_lat = random.uniform(-0.005, 0.005)
    delta_lon = random.uniform(-0.005, 0.005)
    f_lat = lat + delta_lat
    f_lon = lon + delta_lon

    leave = cur + timedelta(hours=f_type["ideal_duration_hours"])
    filler = {"name": f_type["name"], "lat": f_lat, "lon": f_lon, "category": f_type["category"], "ideal_duration_hours": f_type["ideal_duration_hours"]}
    day.append((cur, leave, filler))
    return leave, f_lat, f_lon

def build_itinerary(df_city, start_location, days, start_time, end_time, speed):
    pois = df_city.to_dict("records")
    random.shuffle(pois)
    buckets = [[] for _ in range(days)]
    for i, p in enumerate(pois):
        buckets[i % days].append(p)

    full = []
    for d in range(days):
        cur = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        lat, lon = start_location["lat"], start_location["lon"]
        day = []

        MEALS = [("Breakfast", None), ("Lunch", dt_time(13,0)), ("Dinner", dt_time(19,0))]

        for mname, min_time in MEALS:
            min_meal_time = datetime.combine(datetime.today(), min_time) if min_time else cur

            while buckets[d] and cur < min_meal_time:
                poi = min(buckets[d], key=lambda x: haversine(lat, lon, x["lat"], x["lon"]))
                buckets[d].remove(poi)

                travel = travel_minutes(haversine(lat, lon, poi["lat"], poi["lon"]), speed)
                arrive = cur + timedelta(minutes=travel)
                leave = arrive + timedelta(hours=poi.get("ideal_duration_hours",1))

                if leave > min_meal_time:
                    cur, lat, lon = insert_filler(day, cur, min_meal_time, lat, lon, next_meal_time=min_meal_time)
                    break

                day.append((arrive, leave, poi))
                cur, lat, lon = leave, poi["lat"], poi["lon"]

            meal_start = max(cur, min_meal_time)
            if meal_start < end:
                day.append((meal_start, meal_start + timedelta(hours=1), {"name":mname, "lat":lat, "lon":lon, "category":"Meal"}))
                cur = meal_start + timedelta(hours=1)

        while buckets[d] and cur < end:
            poi = min(buckets[d], key=lambda x: haversine(lat, lon, x["lat"], x["lon"]))
            buckets[d].remove(poi)

            travel = travel_minutes(haversine(lat, lon, poi["lat"], poi["lon"]), speed)
            arrive = cur + timedelta(minutes=travel)
            leave = arrive + timedelta(hours=poi.get("ideal_duration_hours",1))

            if leave > end:
                cur, lat, lon = insert_filler(day, cur, end, lat, lon)
                break

            day.append((arrive, leave, poi))
            cur, lat, lon = leave, poi["lat"], poi["lon"]

        if cur < end:
            cur, lat, lon = insert_filler(day, cur, end, lat, lon)

        full.append(day)
    return full
