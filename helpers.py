import math
from math import radians
from datetime import datetime

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = radians(lat1), radians(lon1)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def travel_minutes(dist, speed):
    return max(5, int((dist / speed) * 60 * 1.1))

def parse_time(t):
    return datetime.strptime(t, "%I:%M %p").time()

def clean_text(txt):
    return txt.encode("latin-1", "ignore").decode("latin-1")
