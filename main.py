import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objects as go

# Khởi tạo kết nối.
# Sử dụng st.cache_resource để chỉ chạy một lần thôi.
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

# Thực hiện truy vấn.
# Sử dụng st.cache_data để chỉ chạy lại khi truy vấn thay đổi hoặc sau 10 phút.
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
    WHERE P.Status = 'Completed'
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
        rooms_occupied = int(rooms_occupied_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((year, month, rooms_occupied))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["Year", "Month", "RoomsOccupied"])

    st.subheader("Room Utilization by Month")
    with st.expander("Data Preview"):
        st.dataframe(
            df,
            column_config={"Year": st.column_config.NumberColumn(format="%d")},
        )

    # Biểu đồ đường biểu diễn Room Utilization
    fig = px.line(df, x="Month", y="RoomsOccupied", title="Room Utilization by Month")
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


# Dashboard 5: Total Revenue by Hotel and month
def dashboard_total_revenue_by_hotelAndMonth():
    query = """
SELECT 
    YEAR(R.Check_in_Date) AS Year, 
    MONTH(R.Check_in_Date) AS Month, 
    H.NameHotel, 
    SUM(P.Amount) AS TotalRevenue
FROM 
    Reservation AS R
    JOIN Payments AS P ON R.Res_ID = P.Res_ID
    JOIN Room AS RM ON R.Room_ID = RM.Room_ID
    JOIN Hotels AS H ON RM.Hotel_ID = H.Hotel_ID
WHERE 
    P.Status = 'Completed'
GROUP BY 
    YEAR(R.Check_in_Date), MONTH(R.Check_in_Date), H.NameHotel;
    """
    data = run_query(query)

    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        year, month, hotel_name, total_revenue_str = row
        total_revenue = int(total_revenue_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((year, month, hotel_name, total_revenue))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["Year", "Month", "HotelName", "TotalRevenue"])

    st.subheader("Total Revenue by Hotel and Month")
    with st.expander("Data Preview"):
        st.dataframe(
            df,
            column_config={"Year": st.column_config.NumberColumn(format="%d")},
        )

    # Biểu đồ đường biểu diễn Total Revenue của từng khách sạn theo từng tháng
    fig = px.line(df, x="Month", y="TotalRevenue", color="HotelName", title="Total Revenue by Hotel and Month", 
                  markers=True)
    st.plotly_chart(fig)

#Dashboard 6: total revenue by hotel
def dashboard_total_revenue_by_hotel():
    query = """
    SELECT 
        H.NameHotel, 
        SUM(P.Amount) AS TotalRevenue
    FROM 
        Reservation AS R
        JOIN Payments AS P ON R.Res_ID = P.Res_ID
        JOIN Room AS RM ON R.Room_ID = RM.Room_ID
        JOIN Hotels AS H ON RM.Hotel_ID = H.Hotel_ID
    WHERE 
        P.Status = 'Completed'
    GROUP BY 
        H.NameHotel;
    """
    data = run_query(query)

    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in data:
        hotel_name, total_revenue_str = row
        total_revenue = int(total_revenue_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((hotel_name, total_revenue))

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(converted_data, columns=["HotelName", "TotalRevenue"])

    st.subheader("Total Revenue by Hotel")
    with st.expander("Data Preview"):
        st.dataframe(df)

    # Biểu đồ cột biểu diễn Total Revenue của từng khách sạn
    fig = px.bar(df, x="HotelName", y="TotalRevenue", title="Total Revenue by Hotel")
    st.plotly_chart(fig)

# Main App
def main():
    st.title("Hotel Management Dashboard")

    dashboard_total_revenue()
    dashboard_room_utilization()
    dashboard_customer_analysis()
    dashboard_staff_performance()
    dashboard_total_revenue_by_hotelAndMonth()
    dashboard_total_revenue_by_hotel()

if __name__ == "__main__":
    main()
