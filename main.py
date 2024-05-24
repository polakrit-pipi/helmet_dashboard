import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.graph_objects as go
import calendar
import datetime

# Load credentials from JSON key file
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = '1WpsBMMpp9KC3YYhySeAq1ZQ9mp5KFOrrlJlm-zqttb4'
sheet = client.open_by_key(sheet_id).sheet1  # Open the first sheet in the Google Sheet

# Function to get data based on the selected part, eng, store_id, and date
def get_data(part, eng, store_id, selected_date):
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
page = st.sidebar.selectbox("Select Page", ["ข้อมูลรวม", "ตรวจสอบตาม Area", "ตรวจสอบตาม ผู้รับเหมา", "รายงานรายเดือน"])

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
df = get_data(selected_part, selected_eng, selected_store_id, selected_date.strftime("%Y-%m-%d"))

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
            title="จำนวนการใส่หมวกตาม Area",
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
            title="จำนวนการใส่หมวกตาม ผู้รับเหมา",
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

elif page == "รายงานรายเดือน":
    current_date = datetime.datetime.now()
    default_month = current_date.month
    default_year = current_date.year
    selected_month = st.sidebar.selectbox("Select Month", range(1, 13), index=default_month - 1)
    selected_year = st.sidebar.selectbox("Select Year", range(2020, 2025), index=default_year - 2020)

    # Get the data for the selected month
    month_start = f"{selected_year}-{selected_month:02d}-01"
    month_end = f"{selected_year}-{selected_month:02d}-{calendar.monthrange(selected_year, selected_month)[1]}"
    df_month = get_data(selected_part, selected_eng, selected_store_id, "")
    df_month = df_month[(df_month["เวลา"] >= month_start) & (df_month["เวลา"] <= month_end)]

    if not df_month.empty:
        helmet_count = df_month["จำนวนคนใส่หมวก"].sum()
        no_helmet_count = df_month["คนไม่ใส่หมวก"].sum()
        person_count = df_month["คนทั้งหมด"].sum()
       
        
        # Insights
        total_days = df_month["เวลา"].nunique()
        average_helmet_per_day = helmet_count / total_days
        average_no_helmet_per_day = no_helmet_count / total_days

        # Vendor-wise analysis
        vendor_analysis = df_month.groupby("ผู้รับเหมา").agg({
            "จำนวนคนใส่หมวก": "sum",
            "คนไม่ใส่หมวก": "sum",
            "คนทั้งหมด": "sum"
        }).reset_index()

        # Display the data
        st.write(f"### Monthly Report for {calendar.month_name[selected_month]} {selected_year}")

        # Overall monthly report
        st.write(f"#### Overall Monthly Report:")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Wearing Helmet", "Not Wearing Helmet"],
            y=[helmet_count, no_helmet_count],
            text=[helmet_count, no_helmet_count],
            textposition='auto',
            marker_color=["#8bd49c", "#ff7f7f"],
        ))
        fig.update_layout(title_text='Monthly Helmet Usage Statistics')
        st.plotly_chart(fig)

        # HTML and CSS for insights and summary
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Monthly Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    padding: 20px;
                }}
                .report {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    max-width: 800px;
                    margin: auto;
                }}
                .report h1 {{
                    color: #333333;
                    font-size: 2em;
                    margin: 0 0 20px;
                }}
                .summary {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-around;
                    margin-bottom: 20px;
                }}
                .summary div {{
                    background-color: #f0f0f0;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px;
                    text-align: center;
                    flex: 1 1 calc(33% - 40px);
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                }}
                .summary div h2 {{
                    margin: 0;
                    font-size: 1.5em;
                    color: #555555;
                }}
                .summary div p {{
                    margin: 10px 0 0;
                    font-size: 1.2em;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="report">
                <h1>รายงานประจำเดือน {calendar.month_name[selected_month]} {selected_year}</h1>
                <div class="summary">
                    <div>
                        <h2>จำนวนคนใส่หมวก</h2>
                        <p>{helmet_count} คน</p>
                    </div>
                    <div>
                        <h2>จำนวนคนไม่ใส่หมวก</h2>
                        <p>{no_helmet_count} คน</p>
                    </div>
                    <div>
                        <h2>จำนวนคนทั้งหมด</h2>
                        <p>{person_count} คน</p>
                    </div>
                    <div>
                        <h2>เฉลี่ยจำนวนคนใส่หมวกต่อวัน</h2>
                        <p>{average_helmet_per_day:.2f} คน</p>
                    </div>
                    <div>
                        <h2>เฉลี่ยจำนวนคนไม่ใส่หมวกต่อวัน</h2>
                        <p>{average_no_helmet_per_day:.2f} คน</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Vendor Analysis
        
        st.markdown(html_content , unsafe_allow_html=True)
        st.write(f"#### Vendor-wise Analysis:")
        for index, row in vendor_analysis.iterrows():
            st.write(f"##### ผู้รับเหมา: {row['ผู้รับเหมา']}")
            st.write(f"จำนวนคนใส่หมวก: {row['จำนวนคนใส่หมวก']} คน")
            st.write(f"จำนวนคนไม่ใส่หมวก: {row['คนไม่ใส่หมวก']} คน")
            st.write(f"จำนวนคนทั้งหมด: {row['คนทั้งหมด']} คน")
            st.write("---")  # Separator between vendors

    else:
        st.write(f"No data available for {calendar.month_name[selected_month]} {selected_year}.")