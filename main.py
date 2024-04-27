import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objects as go

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Dashboard 1: Total Revenue
def dashboard_total_revenue():
    query = """
    SELECT YEAR(R.Check_in_Date) AS Year, MONTH(R.Check_in_Date) AS Month, SUM(P.Amount) AS TotalRevenue
    FROM Reservation AS R
    JOIN payments AS P ON R.Res_ID = P.Res_ID
    GROUP BY YEAR(R.Check_in_Date), MONTH(R.Check_in_Date);
    """
    data = run_query(query)

    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        year, month, total_revenue_str = row
        total_revenue = Decimal(str(total_revenue_str))  # Chuyển Decimal thành chuỗi trước khi chuyển đổi
        converted_data.append((year, month, total_revenue))

    # Tạo DataFrame từ dữ liệu đã chuyển đổi
    df = pd.DataFrame(converted_data, columns=["Year", "Month", "TotalRevenue"])

    st.subheader("Total Revenue by Month")
    # st.write(df)
    with st.expander("Data Preview"):
        st.dataframe(
            df,
            column_config={"Year": st.column_config.NumberColumn(format="%d")},
        )

    # Plot total revenue
    fig = px.line(df, x="Month", y="TotalRevenue", title="Total Revenue by Month")
    st.plotly_chart(fig)

# Dashboard 2: Room Utilization
def dashboard_room_utilization():
    query = """
    SELECT YEAR(R.Check_in_Date) AS Year, MONTH(R.Check_in_Date) AS Month, COUNT(*) AS RoomsOccupied
    FROM Reservation AS R
    GROUP BY YEAR(R.Check_in_Date), MONTH(R.Check_in_Date);
    """
    data = run_query(query)

    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        year, month, rooms_occupied_str = row
        rooms_occupied = Decimal(str(rooms_occupied_str))  # Chuyển Decimal thành chuỗi trước khi chuyển đổi
        converted_data.append((year, month, rooms_occupied))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["Year", "Month", "RoomsOccupied"])

    st.subheader("Room Utilization by Month")
    with st.expander("Data Preview"):
        st.dataframe(
            df,
            column_config={"Year": st.column_config.NumberColumn(format="%d")},
        )

    # Plot room utilization
    fig = px.bar(df, x="Month", y="RoomsOccupied", title="Room Utilization by Month")
    st.plotly_chart(fig)

# Dashboard 3: Customer Analysis
def dashboard_customer_analysis():
    query = """
    SELECT Gender, Country, COUNT(*) AS Count
    FROM Customer
    GROUP BY Gender, Country
    ORDER BY Gender, Country;
    """
    data = run_query(query)

    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        gender, country, count = row
        converted_data.append((gender.strip("'"), country.strip("'"), int(count)))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["Gender", "Country", "Count"])

    st.subheader("Customer Gender and Country Analysis")
    with st.expander("Data Preview"):
        st.dataframe(df)

    # Plot customer gender and country analysis
    fig = px.bar(df, x="Country", y="Count", color="Gender", title="Customer Gender and Country Analysis")
    st.plotly_chart(fig)


# Dashboard 4: Staff Performance
def dashboard_staff_performance():
    query = """
    SELECT H.NameHotel, S.Position, COUNT(S.Staff_ID) AS EmployeeCount
    FROM Hotels AS H
    LEFT JOIN Staff AS S ON H.Hotel_ID = S.Hotel_ID
    GROUP BY H.NameHotel, S.Position
    ORDER BY H.NameHotel, S.Position;
    """
    data = run_query(query)
    
    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        hotel_name, position, employee_count_str = row
        employee_count = int(employee_count_str)
        converted_data.append((hotel_name.strip("'"), position.strip("'"), employee_count))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["HotelName", "Position", "EmployeeCount"])

    st.subheader("Staff Performance by Hotel and Position")
    with st.expander("Data Preview"):
        st.dataframe(df)

    # Plot staff performance by hotel and position
    fig = px.bar(df, x="HotelName", y="EmployeeCount", color="Position", 
                 title="Staff Performance by Hotel and Position")
    st.plotly_chart(fig)


# Main App
def main():
    st.title("Hotel Management Dashboard")

    dashboard_total_revenue()
    dashboard_room_utilization()
    dashboard_customer_analysis()
    dashboard_staff_performance()

if __name__ == "__main__":
    main()
