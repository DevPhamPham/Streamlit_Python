import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objects as go

st.set_page_config(page_title="Hotel Dashboard", page_icon=":bar_chart:", layout="wide")

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

def dashboard_sales_channel_analysis():
    st.subheader("Sales Channel Analysis")
    sales_channel_query = """
        SELECT 
            CASE 
                WHEN Choose_hoser='yes' THEN 'Room Service'
                ELSE 'No Room Service'
            END AS Service_Type,
            COUNT(Res_ID) AS Number_of_Bookings
        FROM 
            Reservation
        GROUP BY 
            CASE 
                WHEN Choose_hoser='yes' THEN 'Room Service'
                ELSE 'No Room Service'
            END;
    """
    sales_channel_data = run_query(sales_channel_query)
    # Chuyển đổi dữ liệu từ tuple chuỗi sang tuple số và Decimals
    converted_data = []
    for row in sales_channel_data:
        service_type, num_bookings_str = row
        num_bookings = int(num_bookings_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((service_type, num_bookings))

    # Tạo DataFrame từ dữ liệu
    df_sales_channel = pd.DataFrame(
        converted_data, columns=["Service_Type", "Number_of_Bookings"]
    )

    with st.expander("Data Preview"):
        st.dataframe(df_sales_channel)

    if df_sales_channel.empty:
        st.warning("No data available for sales channel analysis.")
    else:
        fig_sales_channel = px.pie(
            df_sales_channel,
            values="Number_of_Bookings",
            names="Service_Type",
            title="Room Service Distribution",
            hole=0.3,
        )

        st.plotly_chart(fig_sales_channel)

def dashboard_customer_bookings():
    st.subheader("Customer Bookings per Month")

    customer_bookings_query = """
    SELECT FORMAT(Res.Check_in_Date, 'yyyy-MM') AS MonthYear, COUNT(Res.Res_ID) AS Total_Bookings
    FROM Reservation AS Res
    GROUP BY FORMAT(Res.Check_in_Date, 'yyyy-MM')
    ORDER BY MonthYear
    """

    booking_data = run_query(customer_bookings_query)

    converted_data = []
    for row in booking_data:
        month_year, total_bookings_str = row
        total_bookings = int(total_bookings_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((month_year, total_bookings))

    df_booking = pd.DataFrame(
        converted_data, columns=["MonthYear", "Total_Bookings"]
    )

    if df_booking.empty:
        st.warning("No booking data available.")
    else:
        with st.expander("Data Preview"):
            st.dataframe(df_booking)

        fig_booking = px.bar(
            df_booking,
            x="MonthYear",
            y="Total_Bookings",
            title="Customer Bookings per Month",
            labels={"MonthYear": "Month-Year", "Total_Bookings": "Total Bookings"},
        )

        st.plotly_chart(fig_booking)

def dashboard_customer_demographics():
    st.subheader("Customer Demographics")

    # Query for customer demographics
    customer_demographics_query = """
    SELECT 
        CASE 
            WHEN Age < 18 THEN 'Under 18'
            WHEN Age >= 18 AND Age < 30 THEN '18-29'
            WHEN Age >= 30 AND Age < 40 THEN '30-39'
            WHEN Age >= 40 AND Age < 50 THEN '40-49'
            ELSE '50+'
        END AS Age_Group,
        COUNT(Cus_ID) AS Number_of_Customers
    FROM Customer
    GROUP BY 
        CASE 
            WHEN Age < 18 THEN 'Under 18'
            WHEN Age >= 18 AND Age < 30 THEN '18-29'
            WHEN Age >= 30 AND Age < 40 THEN '30-39'
            WHEN Age >= 40 AND Age < 50 THEN '40-49'
            ELSE '50+'
        END
    """

    customer_demographics_data = run_query(customer_demographics_query)

    converted_data = []
    for row in customer_demographics_data:
        age_group, num_customers_str = row
        num_customers = int(num_customers_str)  # Chuyển Decimal thành số nguyên
        converted_data.append((age_group, num_customers))

    df_customer_demographics = pd.DataFrame(
        converted_data, columns=["Age_Group", "Number_of_Customers"]
    )

    if df_customer_demographics.empty:
        st.warning("No customer demographics data available.")
    else:
        with st.expander("Data Preview"):
            st.dataframe(df_customer_demographics)

        fig_customer_demographics = px.bar(
            df_customer_demographics,
            x="Age_Group",
            y="Number_of_Customers",
            title="Customer Age Group Distribution",
            labels={"Number_of_Customers": "Number of Customers"},
        )

        st.plotly_chart(fig_customer_demographics)

def customer_view_rooms_per_hotel():
    st.subheader("Rooms per Hotel")

    rooms_per_hotel_query = """
    SELECT H.NameHotel, COUNT(R.Room_ID) AS Number_of_Rooms
    FROM Hotels AS H
    LEFT JOIN Room AS R ON H.Hotel_ID = R.Hotel_ID
    GROUP BY H.NameHotel
    """

    rooms_per_hotel_data = run_query(rooms_per_hotel_query)

    converted_data = []
    for row in rooms_per_hotel_data:
        hotel_name, num_rooms_str = row
        num_rooms = int(num_rooms_str)
        converted_data.append((hotel_name, num_rooms))

    df_rooms_per_hotel = pd.DataFrame(
        converted_data, columns=["HotelName", "Number_of_Rooms"]
    )

    if df_rooms_per_hotel.empty:
        st.warning("No data available for rooms per hotel.")
    else:
        with st.expander("Data Preview"):
            st.dataframe(df_rooms_per_hotel)
        fig_rooms_per_hotel = px.bar(
            df_rooms_per_hotel,
            x='HotelName',
            y='Number_of_Rooms',
            title='Rooms per Hotel',
            labels={'Number_of_Rooms': 'Number of Rooms'},
        )

        st.plotly_chart(fig_rooms_per_hotel)

def customer_view_room_types_per_hotel():
    st.subheader("Room Types per Hotel")

    room_types_per_hotel_query = """
    SELECT H.NameHotel, RT.RT_Name
    FROM Hotels AS H
    LEFT JOIN Room AS R ON H.Hotel_ID = R.Hotel_ID
    LEFT JOIN RoomType AS RT ON R.RT_ID = RT.RT_ID
    """

    room_types_per_hotel_data = run_query(room_types_per_hotel_query)

    converted_data = [(hotel_name, room_type) for hotel_name, room_type in room_types_per_hotel_data]

    df_room_types_per_hotel = pd.DataFrame(
        converted_data, columns=["HotelName", "RoomType"]
    )

    if df_room_types_per_hotel.empty:
        st.warning("No data available for room types per hotel.")
    else:
        with st.expander("Data Preview"):
            st.dataframe(df_room_types_per_hotel)
        fig = px.sunburst(
            df_room_types_per_hotel,
            path=['HotelName', 'RoomType'],
            title="Room Types per Hotel",
            width=700,
            height=500
        )
        st.plotly_chart(fig)

def customer_view_services_per_hotel():
    st.subheader("Services per Hotel")

    services_per_hotel_query = """
    SELECT H.NameHotel, HS.HoSer_name AS Service_Name
    FROM Hotels AS H
    LEFT JOIN HotelService AS HS ON H.Hotel_ID = HS.Hotel_ID
    """

    services_per_hotel_data = run_query(services_per_hotel_query)

    converted_data = [(hotel_name, service_name) for hotel_name, service_name in services_per_hotel_data]

    df_services_per_hotel = pd.DataFrame(
        converted_data, columns=["HotelName", "Service_Name"]
    )

    if df_services_per_hotel.empty:
        st.warning("No data available for services per hotel.")
    else:
        with st.expander("Data Preview"):
            st.dataframe(df_services_per_hotel)
        fig = px.sunburst(
            df_services_per_hotel,
            path=['HotelName', 'Service_Name'],
            title="Services per Hotel",
            width=700,
            height=500
        )
        st.plotly_chart(fig)

# Main App
def main():
    st.title("Hotel Management Dashboard")

    st.header("CEO")
    col1, col2 = st.columns(2)
    # col3, col4 = st.columns(2)
    with col1:
        dashboard_total_revenue_by_hotel()
        dashboard_total_revenue()
    with col2:
        dashboard_total_revenue_by_hotelAndMonth()
        dashboard_room_utilization()

    st.header("Manager")
    col3, col4 = st.columns(2)
    with col3:
        dashboard_staff_performance()
        dashboard_sales_channel_analysis()
    with col4:
        dashboard_customer_bookings()
        dashboard_customer_demographics()

    st.header("Customer")
    col5, col6 = st.columns(2)
    with col5:
        dashboard_customer_analysis()
        customer_view_rooms_per_hotel()
    with col6:
        customer_view_room_types_per_hotel()
        customer_view_services_per_hotel()

if __name__ == "__main__":
    main()
