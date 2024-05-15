import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Load credentials from JSON key file
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = '1WpsBMMpp9KC3YYhySeAq1ZQ9mp5KFOrrlJlm-zqttb4'
sheet = client.open_by_key(sheet_id).sheet1  # Open the first sheet in the Google Sheet

# Function to get data based on the selected part and date
def get_data(part, eng, store_id ,  selected_date):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["รหัสร้าน"] = df["รหัสร้าน"].astype(str)
    if part != "All":
        df = df[df["ภาค"] == part]
    if eng != "ALL":
        df = df[df["ผู้รับเหมา"] == eng]
    if store_id != "ALL":
        df = df[df["รหัสร้าน"] == store_id]
    if selected_date:
        df = df[df["เวลา"].str.contains(selected_date)]
    return df

# Streamlit app
st.title("Helmet Detection Data")

# Get the list of parts from the Google Sheet
engs = sheet.col_values(5)[1:]
engs = list(set(engs))

store_ids = sheet.col_values(4)[1:]
store_ids = list(set(store_ids))


parts = ['BE', 'BG', 'BN', 'BS', 'BW', 'NEL', 'REL', 'RSL', 'RC', 'RN', 'NEU', 'REU', 'RSU']

# Multiple selector for parts
selected_part = st.selectbox("Select Part", ["All"] + parts)
# Multiple selector for engs
selected_eng = st.selectbox("Select Eng", ["ALL"] + engs)
# Multiple selector for store_id
selected_store_id = st.selectbox("Select Store_id", ["ALL"] + store_ids)


# Date input widget
selected_date = st.date_input("Select Date")

# Get data based on the selected part and date
df = get_data(selected_part, selected_eng , selected_store_id ,  selected_date.strftime("%Y-%m-%d"))

# Display the data
st.write(df)

# Display count of helmet, no helmet, and person
if selected_part != "All" or selected_eng or selected_store_id:
    helmet_count = df["จำนวนคนใส่หมวก"].sum()
    no_helmet_count = df["คนไม่ใส่หมวก"].sum()
    person_count = df["คนทั้งหมด"].sum()

    st.write(f"Total Helmet Count: {helmet_count}")
    st.write(f"Total No Helmet Count: {no_helmet_count}")
    st.write(f"Total Person Count: {person_count}")

