# Megan Johnson
# CS 230-1
# Data from New York Housing Market
# http://localhost:8501
# This program provides information for the New York Housing Market.

# This is a link to a video I referenced for a few of the features I implemented:
# https://www.youtube.com/watch?v=VqgUkExPvLY
# This is a link to a site I referenced for how to render my Folium map in Streamlit:
# https://discuss.streamlit.io/t/ann-streamlit-folium-a-component-for-rendering-folium-maps/4367
# This is a link to a site I referenced for how to find the correlation between column values:
# https://www.geeksforgeeks.org/python-pandas-dataframe-corr/

# import packages
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static

# set page layout ([ST4])
st.set_page_config(page_title = "NY Property Finder",
                   page_icon = ":cityscape:",
                   layout = "wide")
st.image("https://cdn.wallpapersafari.com/40/20/Dfa5ZM.jpg", use_container_width = True)
st.title(":house: New York Real Estate Finder")
st.markdown("Use the filters in the sidebar to find your perfect home!")
st.markdown("[View the original dataset here]"
            "(https://www.kaggle.com/datasets/nelgiriyewithana/new-york-housing-market)")
st.sidebar.header("🔎 Search Filters")

# load and clean initial data ([DA1])
def load_data():
    # [PY3]
    try:
        df = pd.read_csv("NY-House-Dataset.csv")
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {e}")
        return pd.DataFrame()  # return an empty dataframe if there’s any error

    # remove unwanted columns
    columns_to_remove = ["ADDRESS", "STATE", "ADMINISTRATIVE_AREA_LEVEL_2", "STREET_NAME", "LONG_NAME", "MAIN_ADDRESS",
                         "BROKERTITLE", "SUBLOCALITY"]
    df = df.drop(columns = columns_to_remove)

    # keep only rows where BATH is a whole number
    df = df[df["BATH"] % 1 == 0]

    # format column values
    df["BATH"] = df["BATH"].astype(int)
    df["BEDS"] = df["BEDS"].astype(int)
    df["PROPERTYSQFT"] = df["PROPERTYSQFT"].astype(int)
    df["PRICE"] = df["PRICE"].astype(int)

    return df

# define a function for getting the max and min values of a data frame column ([PY1], [PY2])
def get_max_min(col_name, data_frame = None, round_to_int = True):
    if data_frame is None:
        data_frame = df # uses df as the default dataframe
    clean_data = data_frame[col_name].dropna()
    if clean_data.empty:
        return None, None
    min_val = clean_data.min()
    max_val = clean_data.max()
    if round_to_int:
        return int(min_val), int(max_val)
    else:
        return float(min_val), float(max_val)

# loading the data
df = load_data()

# sidebar widgets for user filtering ([ST1], [ST2], [ST3])
property_types = df["TYPE"].dropna().unique().tolist()
selected_property_type = st.sidebar.selectbox("Property Type", property_types)

localities = df["LOCALITY"].dropna().unique().tolist()
selected_loc = st.sidebar.multiselect("Localities", options = localities, default = ["New York"])

min_price, max_price = get_max_min("PRICE")
price_range = st.sidebar.slider("Price Range ($)", min_value = min_price, max_value = max_price,
                                value = (min_price, max_price), format = "%d")

min_sqft, max_sqft = get_max_min("PROPERTYSQFT")
sqft_range = st.sidebar.slider("Square Footage Range", min_value = min_sqft, max_value = max_sqft,
                                value = (min_sqft, max_sqft), format = "%d")

min_bed, max_bed = get_max_min("BEDS")
bed_range = st.sidebar.slider("Bedroom Range", min_value = min_bed, max_value = max_bed,
                                value = (min_bed, max_bed))

min_bath, max_bath = get_max_min("BATH")
bath_range = st.sidebar.slider("Bathroom Range", min_value = min_bath, max_value = max_bath,
                                value = (min_bath, max_bath))

# filtering the data based on user input
def filter_properties(df, filters):
    # [DA5]
    return df[
        (df["TYPE"] == filters["property_type"]) &
        (df["LOCALITY"].isin(filters["localities"])) &
        df["PRICE"].between(filters["price_range"][0], filters["price_range"][1]) &
        df["PROPERTYSQFT"].between(filters["sqft_range"][0], filters["sqft_range"][1]) &
        df["BEDS"].between(filters["bed_range"][0], filters["bed_range"][1]) &
        df["BATH"].between(filters["bath_range"][0], filters["bath_range"][1])
    ]

# [PY5]
filters = {
    "property_type": selected_property_type,
    "localities": selected_loc,
    "price_range": price_range,
    "sqft_range": sqft_range,
    "bed_range": bed_range,
    "bath_range": bath_range}

filtered_df = filter_properties(df, filters)

if filtered_df.empty:
    st.warning("No properties match your criteria. Try adjusting the filters.")
else:
    # allow user to sort data based on price from highest to lowest or vice versa ([DA2])
    sort_order = st.radio(
        "Sort properties by price:",
        ("Lowest to Highest", "Highest to Lowest")
    )

    if sort_order == "Lowest to Highest":
        sorted_df = filtered_df.sort_values(by = "PRICE", ascending = True)
    else:
        sorted_df = filtered_df.sort_values(by = "PRICE", ascending = False)

    # displaying the data with cleaned column names
    display_columns = {
        "FORMATTED_ADDRESS": "Address",
        "LOCALITY": "Locality",
        "PRICE": "Price",
        "PROPERTYSQFT": "Square Footage",
        "BEDS": "Bedrooms",
        "BATH": "Bathrooms"
    }

    final_columns = ["FORMATTED_ADDRESS", "LOCALITY", "PRICE", "PROPERTYSQFT", "BEDS",
                     "BATH"]  # type, longitude, and latitude not displayed
    sorted_df = sorted_df[final_columns]
    display_df = sorted_df.rename(columns = display_columns)
    display_df["Price"] = display_df["Price"].map("${:,.0f}".format)
    display_df["Square Footage"] = display_df["Square Footage"].map("{:,.0f}".format)

    # display the number of properties that match user criteria
    property_count = filtered_df.shape[0]
    st.markdown(f"**Number of properties matching your criteria:** {property_count}")

    st.subheader(f"Filtered Properties ({sort_order})")
    st.dataframe(display_df, use_container_width = True, hide_index = True)

    # find and display the average price per sqft and the properties with the highest and lowest price per sqft ([DA3])
    # (this is a section of my code that I am most proud of because of how long it took me to make work)
    # [DA6], [DA9]
    filtered_df["Price/Sqft"] = filtered_df["PRICE"] / filtered_df["PROPERTYSQFT"]
    filtered_df = filtered_df.dropna(subset = ["Price/Sqft"])
    lowest_price_sqft, highest_price_sqft = get_max_min("Price/Sqft", filtered_df, round_to_int = False)

    if not(lowest_price_sqft is None or highest_price_sqft is None):
        # [DA4]
        highest_price_property = filtered_df[filtered_df["Price/Sqft"] == highest_price_sqft]
        lowest_price_property = filtered_df[filtered_df["Price/Sqft"] == lowest_price_sqft]

        highest_address = highest_price_property["FORMATTED_ADDRESS"].iloc[0]
        lowest_address = lowest_price_property["FORMATTED_ADDRESS"].iloc[0]

        highest_price_value = f"${highest_price_sqft:,.0f}"
        lowest_price_value = f"${lowest_price_sqft:,.0f}"

        st.markdown(f"**Property with Highest Price per Square Footage:** {highest_address} ({highest_price_value})")
        st.markdown(f"**Property with Lowest Price per Square Footage:** {lowest_address} ({lowest_price_value})")

        average_price_sqft = filtered_df["Price/Sqft"].mean()
        st.markdown(f"**Average Price per Square Footage:** ${average_price_sqft:,.0f}")
    else:
        st.warning("Not enough data to determine Price/Sqft range.")

    # map of filtered properties using Folium ([MAP], [FOLIUM1])
    avg_lat = filtered_df["LATITUDE"].mean()
    avg_lon = filtered_df["LONGITUDE"].mean()

    # this is another feature I'm proud of because the starting location is specific to the user's criteria
    m = folium.Map(location = [avg_lat, avg_lon], zoom_start = 12)

    filtered_df.apply(lambda row: folium.Marker(location = [row["LATITUDE"], row["LONGITUDE"]],
                                                popup = row["FORMATTED_ADDRESS"]).add_to(m), axis = 1)

    folium_static(m, width = 2000)

    # format specification for charts
    primaryColor = "#f48c06"
    backgroundColor = "#e3eef4"
    textColor = "#000000"

    col1, col2, col3 = st.columns(3)

    # scatter plot for price vs sqft of filtered data with regression line ([CHART1], SEA[1])
    fig1, ax1 = plt.subplots()
    fig1.patch.set_facecolor(backgroundColor)
    ax1.set_facecolor(backgroundColor)
    sns.regplot(data = filtered_df, x = "PROPERTYSQFT", y = "PRICE", ax = ax1)
    ax1.set_xlabel("Square Footage", color = textColor)
    ax1.set_ylabel("Price ($)", color = textColor)
    ax1.set_title("Regression of Property Price vs Square Footage", color = textColor)
    col1.pyplot(fig1)

    # histogram for price of filtered data with a density curve ([CHART2], SEA[2])
    fig2, ax2 = plt.subplots()
    fig2.patch.set_facecolor(backgroundColor)
    ax2.set_facecolor(backgroundColor)
    sns.histplot(data = filtered_df, x = "PRICE", kde = True, ax = ax2, color = primaryColor)
    ax2.set_xlabel("Price ($)", color = textColor)
    ax2.set_title("Price Distribution with Density Curve", color = textColor)
    col2.pyplot(fig2)

    # correlation matrix heatmap of filtered data for price, sqft, beds, and baths
    fig3, ax3 = plt.subplots()
    fig3.patch.set_facecolor(backgroundColor)
    ax3.set_facecolor(backgroundColor)
    corr_matrix = filtered_df[["PRICE", "BEDS", "BATH", "PROPERTYSQFT"]].corr()
    sns.heatmap(corr_matrix, annot = True, cmap = "rocket", fmt = ".2f", ax = ax3)
    ax3.set_title("Correlation Matrix (Filtered Data)", color = textColor)
    col3.pyplot(fig3)