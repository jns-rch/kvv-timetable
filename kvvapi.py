# FUNCTIONS FOR KVV API ###################
# 
# author: Jonas Rauch
# date: 2021-01-22
#

import requests
import pandas as pd

# ToDo: Make own function for API KEY checking
with open("API_KEY.txt") as key_file:
    API_KEY = key_file.read()
API_BASE = "https://live.kvv.de/webapp"
REQUEST_TYPES = ["stops_by_name", 
        "stops_by_id",
        "departues_by_stop", 
        "departues_by_route"]


def kvv_request(request_string):
    """Sends a REST call to "https://live.kvv.de/webapp/"
    """ 
    r = requests.get(request_string)
    
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        ValueError(f"Error in Request: {error}")
    else:
        return r.json()

def create_request_string(request_type, name="name", stop_id="0", line="S1", max_infos=10): 
    """Creates a request string
    """ 
    if request_type == "stops_by_name":
        request_string = f"{API_BASE}/stops/byname/{name}?key={API_KEY}"
    elif request_type == "stops_by_id":
        request_string = f"{API_BASE}/stops/bystop/{stop_id}?key={API_KEY}"
    elif request_type == "departues_by_stop":
        request_string = f"{API_BASE}/departures/bystop/{stop_id}?maxInfos={max_infos}&key={API_KEY}"
    elif request_type == "departues_by_route":
        request_string = f"{API_BASE}/departures/byroute/{line}/{stop_id}?maxInfos={max_infos}&key={API_KEY}"

    return request_string

def create_departure_dataframe(dict):
    """Creates a dataframe with departures for stop out of a dict
    """ 
    return pd.DataFrame(dict["departures"])

def update_departure_dataframe(stop_id="0", max_infos=10):
    """Updates the departure dataframe by calling a REST request
    """
    request_string = create_request_string(request_type = "departues_by_stop", stop_id=stop_id, max_infos=max_infos)
    response = kvv_request(request_string)
    departures = create_departure_dataframe(response)

    # Place modifications here
    return departures

def find_stop_id_by_name(data, stop_name):
    """Search for stop_id in Open Transport Data
    """
    stop_id_series = data["stops"][
        (data["stops"]["stop_name"] == stop_name) &
        (~data["stops"]["stop_id"].str.match("Parent"))
    ]["stop_id"]

    def split(x):
        y = x.split(":")[0:3]
        return ":".join(y)
    
    stop_id_series = stop_id_series.apply(split)

    if len(stop_id_series.unique()) == 1:
        unique_stop_id = stop_id_series.unique()[0]
    else:
        ValueError("Cannot found unique id")

    return unique_stop_id

def convert_stop_id_for_request(stop_id):
    """Convert stop_id to format for REST request
    """
    string_as_list = stop_id.split(":")
    string_as_list[1] = str(int(string_as_list[1]))
    string_as_list[2] = str(int(string_as_list[2]))

    return ":".join(string_as_list)

def request_stop_id_by_name(name):
    """Do a REST request do get stop_id by stop name
    """
    request_string = create_request_string(request_type = "stops_by_name", name=name)
    response = kvv_request(request_string)
    return response["stops"][0]["id"]

def search_for_stop_id_by_name(name):
    """Do a REST request do for searching a stop_id by inserting only fragment
    """
    request_string = create_request_string(request_type = "stops_by_name", name=name)
    response = kvv_request(request_string)
    return response["stops"]