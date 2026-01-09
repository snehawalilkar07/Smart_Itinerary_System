import folium
from folium.plugins import LocateControl, MarkerCluster

def create_map(start_location, itinerary):
    # Default map centered on start location
    m = folium.Map(location=[start_location["lat"], start_location["lon"]], zoom_start=12)
    LocateControl().add_to(m)

    # Marker for start location
    folium.Marker(
        [start_location["lat"], start_location["lon"]],
        draggable=True,
        icon=folium.Icon(color="black", icon="star"),
        tooltip="Drag Start Point"
    ).add_to(m)

    if itinerary:
        colors = ["blue", "green", "purple", "red"]
        all_coords = [[start_location["lat"], start_location["lon"]]]  # for auto-fit bounds

        for i, day in enumerate(itinerary):
            fg = folium.FeatureGroup(f"Day {i+1}")
            cl = MarkerCluster().add_to(fg)

            for s, e, p in day:
                popup_text = f"{p['name']}<br>{s.strftime('%I:%M %p')} - {e.strftime('%I:%M %p')}"
                popup = folium.Popup(popup_text, max_width=400)

                color = "orange" if p["category"] == "Meal" else colors[i % 4]

                folium.Marker(
                    [p["lat"], p["lon"]],
                    popup=popup,
                    icon=folium.Icon(color=color)
                ).add_to(cl)

                all_coords.append([p["lat"], p["lon"]])

            m.add_child(fg)

        folium.LayerControl().add_to(m)

        # Auto-fit map to show all markers
        m.fit_bounds(all_coords, padding=(30, 30))

    return m
