import streamlit as st
import requests

api_key = "7f575b68-fb5d-4af1-9121-f3e9ac3cc762"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

# Cache decorator for Streamlit
def st_cache(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@st_cache
def map_creator(latitude, longitude):
    from streamlit_folium import folium_static
    import folium
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)
    folium_static(m)

@st_cache
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    return requests.get(countries_url).json()

@st_cache
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    return requests.get(states_url).json()

@st_cache
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    return requests.get(cities_url).json()

# Category selection
category = st.sidebar.radio("Choose Location Method",
                            ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"])

if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [i["country"] for i in countries_dict["data"]]
        countries_list.insert(0, "")
        country_selected = st.selectbox("Select a country", options=countries_list)

        if country_selected:
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [i["state"] for i in states_dict["data"]]
                states_list.insert(0, "")
                state_selected = st.selectbox("Select a state", options=states_list)

                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [i["city"] for i in cities_dict["data"]]
                        cities_list.insert(0, "")
                        city_selected = st.selectbox("Select a city", options=cities_list)

                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()

                            if aqi_data_dict["status"] == "success":
                                data = aqi_data_dict["data"]
                                st.write(f"Weather in {city_selected}, {state_selected}, {country_selected}:")
                                st.write("Temperature:", data["current"]["weather"]["tp"], "°C")
                                st.write("Humidity:", data["current"]["weather"]["hu"], "%")
                                st.write("Air Quality Index:", data["current"]["pollution"]["aqius"])
                                map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        data = aqi_data_dict["data"]
        st.write("Weather in your nearest city:")
        st.write("Temperature:", data["current"]["weather"]["tp"], "°C")
        st.write("Humidity:", data["current"]["weather"]["hu"], "%")
        st.write("Air Quality Index:", data["current"]["pollution"]["aqius"])
        map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])

elif category == "By Latitude and Longitude":
    latitude = st.text_input("Latitude")
    longitude = st.text_input("Longitude")

    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)
            url = f"https://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
            aqi_data_dict = requests.get(url).json()

            if aqi_data_dict["status"] == "success":
                data = aqi_data_dict["data"]
                st.write("Weather at your coordinates:")
                st.write("Temperature:", data["current"]["weather"]["tp"], "°C")
                st.write("Humidity:", data["current"]["weather"]["hu"], "%")
                st.write("Air Quality Index:", data["current"]["pollution"]["aqius"])

                # Displaying the map for the given coordinates
                map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])