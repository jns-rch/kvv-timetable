"""
# Abfahrtstafel
  This is a table that shows the departures for a stop that can be searched before.
"""

import streamlit as st
import numpy as np
import requests
import json
import time

from kvvapi import *
from dataframes import *

response = {}

########################################################################
# Time
time_text = st.empty()
time_text.write(time.asctime())

########################################################################
# Titel
st.title('Abfahrtstafel')

########################################################################
# Button Aktualisieren
update_button = st.empty()
update_button.button('Aktualisieren')

########################################################################
# Stop Selection
stop_search_input = st.text_input("Haltenstellensuche", value="")
if stop_search_input == "":
    st.stop()

try:
    stop_search_result = search_for_stop_id_by_name(stop_search_input)
except:
    st.write("Kann Haltestelle nicht finden")
    st.stop()

stop_search_result_names = [e["name"] for e in stop_search_result]
selected_stop_name = st.selectbox(
    label='Haltestelle auswählen:',
    options=stop_search_result_names,
    index=0
)
for d in stop_search_result:
    if d["name"] == selected_stop_name:
        stop_id = d["id"]

########################################################################
# Maximum Lines per Table
max_infos = st.number_input("Maximale Infos", min_value=1, max_value=10, value=5, step=1)

########################################################################
# Table
departures_table = st.empty()
try:
    departures = update_departure_dataframe(stop_id=stop_id, max_infos=max_infos)
except:
    st.write("Kann für Haltestelle keine Daten finden.")
    st.stop()

departures_table.table(departures)
time_text.write(time.asctime())

########################################################################
# Checkbox Auto Update EXPERIMENAL
# Problem here: Streamlits behavior with refreshing the dashboard.
# Maybe solve with multiprocessing
set_auto_refresh = st.checkbox("Auto Update Table EXPERIMENAL", value=False, key=None)
refresh_intervall = st.number_input("Intervall (s) EXPERIMENAL", min_value=1, max_value=300, value=30, step=1)

while(set_auto_refresh):
    time.sleep(refresh_intervall)
    time_text.write(time.asctime())
    departures = update_departure_dataframe(stop_id=stop_id, max_infos=max_infos)
    departures_table.table(departures)

