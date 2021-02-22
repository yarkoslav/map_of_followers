"""
This module provide functions, which can make web app, in which
generates map with followers of entered twitter user
"""
import folium
import requests
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request


app = Flask(__name__)


def get_data_about_friends(name: str, bearer_token: str) -> dict:
    """
    Read data about friends of entered(name) user
    Need bearer token to do it
    """
    data = {}
    base_url = "https://api.twitter.com/"
    search_url = "{}1.1/friends/list.json".format(base_url)
    search_headers = {
        'Authorization': 'Bearer {}'.format(bearer_token)
    }
    search_params = {
        'screen_name': name,
        'count': 200
    }
    response = requests.get(search_url, headers=search_headers, params=search_params)
    json_response = response.json()
    geolocator = Nominatim(user_agent="twitter_map.py")
    for user in json_response['users']:
        screen_name = user['screen_name']
        location = user['location']
        user_loc = geolocator.geocode(location)
        if user_loc is not None:
            data[screen_name] = [user_loc.latitude, user_loc.longitude]
    return data


def create_map(data: dict):
    """
    Create map, on which are displayed people from data dict
    """
    mp = folium.Map()
    fg = folium.FeatureGroup(name="Friends location")
    for user in data:
        fg.add_child(folium.Marker(location=data[user],
                                   popup=user,
                                   icon=folium.Icon()))
    mp.add_child(fg)
    mp.save("templates/map.html")


@app.route("/")
def index():
    """
    Show the start page in the internet
    """
    return render_template("index.html")


@app.route("/twitter_map", methods=["POST"])
def twitter_map():
    """
    Show the twitter map in the internet
    """
    name = request.form.get("screen_name")
    bearer_token = request.form.get("bearer_token")
    if not name:
        return render_template("failure.html")
    create_map(get_data_about_friends(name, bearer_token))
    return render_template("map.html")


if __name__ == "__main__":
    app.run(debug=False)
