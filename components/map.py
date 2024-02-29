import streamlit as st
import pydeck as pdk
import json

with open('data/features.geojson') as geojson_file:
    neighborhood_boundaries = json.load(geojson_file)

with open('data/properties.json', 'r') as properties_file:
    properties_data = json.load(properties_file)

view_state = pdk.ViewState(latitude=35.21256667364033, longitude=-80.8588429856899, zoom=13, bearing=0, pitch=0)


neighborhood_layer = pdk.Layer(
    "GeoJsonLayer",
    neighborhood_boundaries,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="properties.elevation",
    get_fill_color="[properties.fillColor, properties.fillColor, properties.fillColor, 100]", # Customize this based on your GeoJSON properties
    get_line_color=[255, 255, 255],
)

properties_layer = pdk.Layer(
    "ScatterplotLayer",
    properties_data,
    get_position="[long, lat]",
    get_color="[200, 30, 0, 160]",
    get_radius=32  # Adjust radius size to your liking
)

text_layer = pdk.Layer(
    "TextLayer",
    properties_data,
    get_position="[long, lat]",
    get_text="name", 
    get_color=[0, 0, 0, 200],  # Text color, RGBA
    get_size=16,  # Text size
    get_alignment_baseline="'bottom'",  # Align text to be above the marker
)


map = pdk.Deck(layers=[neighborhood_layer, properties_layer, text_layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9")