import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.graph_objects as go

# Load credentials from JSON key file
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = '1WpsBMMpp9KC3YYhySeAq1ZQ9mp5KFOrrlJlm-zqttb4'
sheet = client.open_by_key(sheet_id).sheet1  # Open the first sheet in the Google Sheet


# Function to get data based on the selected part and date
def get_data(part, eng, store_id , selected_date):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["รหัสร้าน"] = df["รหัสร้าน"].astype(str)
    if part != "ทั้งหมด":
        df = df[df["ภาค"] == part]
    if eng != "ทั้งหมด":
        df = df[df["ผู้รับเหมา"] == eng]
    if store_id != "ทั้งหมด":
        df = df[df["รหัสร้าน"] == store_id]
    if selected_date:
        df = df[df["เวลา"].str.contains(selected_date)]
    return df

# Streamlit app
st.title("Safty-CAFM")

# Add a sidebar for navigation
page = st.sidebar.selectbox("Select Page", ["ข้อมูลรวม", "ตรวจสอบตาม Area","ตรวจสอบตาม ผู้รับเหมา"])

# Get the list of parts from the Google Sheet
engs = sheet.col_values(5)[1:]
engs = list(set(engs))

store_ids = sheet.col_values(4)[1:]
store_ids = list(set(store_ids))

parts = ['BE', 'BG', 'BN', 'BS', 'BW', 'NEL', 'REL', 'RSL', 'RC', 'RN', 'NEU', 'REU', 'RSU']

# Multiple selector for parts
selected_part = st.selectbox("เลือก Area", ["ทั้งหมด"] + parts)
# Multiple selector for engs
selected_eng = st.selectbox("เลือก Vendor", ["ทั้งหมด"] + engs)
# Multiple selector for store_id
selected_store_id = st.selectbox("เลือก รหัสร้าน", ["ทั้งหมด"] + store_ids)

# Date input widget
selected_date = st.date_input("Select Date")

# Get data based on the selected part and date
df = get_data(selected_part, selected_eng , selected_store_id , selected_date.strftime("%Y-%m-%d"))

if page == "ข้อมูลรวม":
    # Display the data
    if selected_part != "ทั้งหมด" or selected_eng or selected_store_id:
        helmet_count = df["จำนวนคนใส่หมวก"].sum()
        no_helmet_count = df["คนไม่ใส่หมวก"].sum()
        person_count = df["คนทั้งหมด"].sum()
        html_content = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Helmet Usage Poster</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .poster {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 70%;
                    margin: auto;
                    margin-bottom: 1em;
                }}
                .poster h1 {{
                    color: #333333;
                    font-size: 2em;
                    margin: 0;
                    padding-bottom: 20px;
                }}
                .box {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: left;
                }}
                .statistics {{
                    width: 100%;
                    display: table;
                    margin-bottom: 20px;
                }}
                .statistics div {{
                    display: table-cell;
                    padding: 20px;
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 1.2em;
                    margin: 10px;
                }}
                .helmet {{
                    background-color: #8bd49c;
                }}
                .no-helmet {{
                    background-color: #ff7f7f;
                }}
                .total {{
                    background-color: #7fc7ff;
                    padding: 20px;
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 1.5em;
                    margin: 10px auto;
                    width: 70%;
                }}
            </style>
        </head>
        <body>
            <div class="poster">
                <h1>สถิติการสวมหมวกนิรภัย</h1>
                <div class="box">
                    <strong>วันที่:</strong> {selected_date.strftime("%Y-%m-%d")}
                </div>
                <div class="box">
                    <strong>พื้นที่:</strong> {selected_part}
                </div>
                <div class="box">
                    <strong>รหัสร้าน:</strong> {selected_eng}
                </div>
                <div class="box">
                    <strong>รหัสร้าน:</strong> {selected_store_id}
                </div>
                <div class="statistics">
                    <div class="helmet">สวมหมวก: {helmet_count} คน</div>
                    <div class="no-helmet">ไม่สวมหมวก: {no_helmet_count} คน</div>
                </div>
                <div class="total">จำนวนคน: {person_count} คน</div>
            </div>
        </body>
        </html>
        """
        st.markdown(html_content, unsafe_allow_html=True)
    st.write(df)

elif page == "ตรวจสอบตาม Area":
    if not df.empty:
        df_part = df.groupby("ภาค").sum().reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_part["ภาค"],
            y=df_part["จำนวนคนใส่หมวก"],
            name='จำนวนคนใส่หมวก',
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            x=df_part["ภาค"],
            y=df_part["คนไม่ใส่หมวก"],
            name='คนไม่ใส่หมวก',
            textposition='outside'
        ))

        fig.update_layout(
            barmode='group',
            title="Helmet Detection Data by Part",
            xaxis_title="Part",
            yaxis_title="Count",
            legend_title="Type",
            dragmode="pan"
        )

        st.plotly_chart(fig)

        helmet_count = df_part["จำนวนคนใส่หมวก"].sum()
        no_helmet_count = df_part["คนไม่ใส่หมวก"].sum()
        person_count = df_part["คนทั้งหมด"].sum()

        html_content = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Helmet Usage Statistics</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .statistics {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 70%;
                    margin: auto;
                    margin-bottom: 1em;
                }}
                .statistics h1 {{
                    color: #333333;
                    font-size: 2em;
                    margin: 0;
                    padding-bottom: 20px;
                }}
                .box {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: left;
                    border: 1px solid #ccc;
                }}
                .statistics-item {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    margin-bottom: 20px;
                }}
                .statistics-item div {{
                    flex: 1;
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #ffffff;
                    margin: 10px;
                    max-width: 300px;
                    border: 1px solid #ccc;
                }}
                .statistics-item div h2 {{
                    margin: 0;
                    padding-bottom: 10px;
                }}
                .statistics-item div p {{
                    margin: 0;
                    font-size: 1.5em;
                }}
            </style>
        </head>
        <body>
            <div class="statistics">
                <h1>สถิติการสวมหมวกนิรภัย</h1>
                <div class="box">
                    <strong>วันที่:</strong> {selected_date.strftime("%Y-%m-%d")}
                </div>
                <div class="box">
                    <strong>ผู้รับเหมา:</strong> {selected_eng}
                </div>
                <div class="box">
                    <strong>พื้นที่:</strong> {selected_part}
                </div>
                <div class="box">
                    <strong>รหัสร้าน:</strong> {selected_store_id}
                </div>
                <div class="statistics-item">
                    <div>
                        <h2>จำนวนคนใส่หมวกทั้งหมด</h2>
                        <p>{helmet_count}</p>
                    </div>
                    <div>
                        <h2>จำนวนคนไม่ใส่หมวกทั้งหมด</h2>
                        <p>{no_helmet_count}</p>
                    </div>
                    <div>
                        <h2>จำนวนคนทั้งหมด</h2>
                        <p>{person_count}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        st.markdown(html_content, unsafe_allow_html=True)

    else:
        st.write("No data available for the selected filters.")

elif page == "ตรวจสอบตาม ผู้รับเหมา":
    if not df.empty:
        df_part = df.groupby("ผู้รับเหมา").sum().reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_part["ผู้รับเหมา"],
            y=df_part["จำนวนคนใส่หมวก"],
            name='จำนวนคนใส่หมวก',
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            x=df_part["ผู้รับเหมา"],
            y=df_part["คนไม่ใส่หมวก"],
            name='คนไม่ใส่หมวก',
            textposition='outside'
        ))

        fig.update_layout(
            barmode='group',
            title="Helmet Detection Data by Part",
            xaxis_title="Part",
            yaxis_title="Count",
            legend_title="Type",
            dragmode="pan"
        )

        st.plotly_chart(fig)
        helmet_count = df_part["จำนวนคนใส่หมวก"].sum()
        no_helmet_count = df_part["คนไม่ใส่หมวก"].sum()
        person_count = df_part["คนทั้งหมด"].sum()
        html_content = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Helmet Usage Statistics</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .statistics {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 70%;
                    margin: auto;
                    margin-bottom: 1em;
                }}
                .statistics h1 {{
                    color: #333333;
                    font-size: 2em;
                    margin: 0;
                    padding-bottom: 20px;
                }}
                .box {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: left;
                    border: 1px solid #ccc;
                }}
                .statistics-item {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    margin-bottom: 20px;
                }}
                .statistics-item div {{
                    flex: 1;
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #ffffff;
                    margin: 10px;
                    max-width: 300px;
                    border: 1px solid #ccc;
                }}
                .statistics-item div h2 {{
                    margin: 0;
                    padding-bottom: 10px;
                }}
                .statistics-item div p {{
                    margin: 0;
                    font-size: 1.5em;
                }}
            </style>
        </head>
        <body>
            <div class="statistics">
                <h1>สถิติการสวมหมวกนิรภัย</h1>
                <div class="box">
                    <strong>วันที่:</strong> {selected_date.strftime("%Y-%m-%d")}
                </div>
                <div class="box">
                    <strong>ผู้รับเหมา:</strong> {selected_eng}
                </div>
                <div class="box">
                    <strong>พื้นที่:</strong> {selected_part}
                </div>
                <div class="box">
                    <strong>รหัสร้าน:</strong> {selected_store_id}
                </div>
                <div class="statistics-item">
                    <div>
                        <h2>จำนวนคนใส่หมวกทั้งหมด</h2>
                        <p>{helmet_count}</p>
                    </div>
                    <div>
                        <h2>จำนวนคนไม่ใส่หมวกทั้งหมด</h2>
                        <p>{no_helmet_count}</p>
                    </div>
                    <div>
                        <h2>จำนวนคนทั้งหมด</h2>
                        <p>{person_count}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        st.markdown(html_content, unsafe_allow_html=True)

    else:
        st.write("No data available for the selected filters.")