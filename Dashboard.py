import plotly.figure_factory as ff
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!",
                   page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart:SuperStore EDA")
st.markdown(
    '<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(
        region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(
    by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)[
            "Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
# print(filtered_df["month_year"])
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(
    filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
# print(linechart)
fig2 = px.line(linechart, x="month_year", y="Sales", labels={
               "Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Download Data of TimeSeries"):
    st.write(linechart.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data as CSV', data=csv,
                       file_name="TimeSeries.csv", mime='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales",
                 names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales",
                 names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City",
                         "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=[
                                       "Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(
        cmap="Oranges"))


state_abbreviations = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}


city_sales = filtered_df.groupby('State')['Sales'].sum().reset_index()

city_sales['State'] = city_sales['State'].map(state_abbreviations)

# Create a map using Plotly
fig = px.choropleth(locations=city_sales['State'],
                    locationmode='USA-states',
                    color=city_sales['Sales'],
                    hover_name=city_sales['State'],
                    title='Sales by State in USA',
                    scope='usa',
                    template="plotly_dark")

# Display the map using Streamlit
st.plotly_chart(fig, use_container_width=True)

with st.expander("View Data By Sate Wise Sales"):
    st.write(city_sales.style.background_gradient(
        cmap="Oranges"))
    csv = city_sales.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data as CSV', data=csv,
                       file_name="Choropleth.csv", mime='text/csv')
    

sub_category_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()

# Step 2: Generate the Bar Plot
fig = px.bar(sub_category_sales, x='Sub-Category', y='Sales', title='Sales by Sub-Category')
st.plotly_chart(fig,use_container_width=True)

with st.expander("View Sales By Sub Categories"):
    st.write(sub_category_sales.style.background_gradient(
        cmap="Oranges"))
    csv = sub_category_sales.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data as CSV', data=csv,
                       file_name="SubCategorySales.csv", mime='text/csv')
    
total_sales_by_subcategory_shipmode = df.groupby(['Sub-Category', 'Ship Mode'])['Sales'].sum().reset_index()

st.subheader('Sales Analysis on basis of Categories/Sub-Categories and Shipping Mode')

selected_modes = st.sidebar.multiselect('Select Shipping Modes', df['Ship Mode'].unique())
selected_categories = st.sidebar.multiselect('Select Sub-Categories', df['Sub-Category'].unique())

filtered_data = total_sales_by_subcategory_shipmode[
    (total_sales_by_subcategory_shipmode['Ship Mode'].isin(selected_modes)) & 
    (total_sales_by_subcategory_shipmode['Sub-Category'].isin(selected_categories))
]

if len(filtered_data) == 0:
    filtered_data = total_sales_by_subcategory_shipmode
colors = selected_colors = [
    "aquamarine", "blanchedalmond", "cadetblue", "chartreuse",
    "darkcyan", "darkgoldenrod", "darkmagenta", "darkorange",
    "dodgerblue", "lightcoral", "lightcyan", "lightgoldenrodyellow",
    "lightpink", "lightsalmon", "mediumseagreen", "mediumvioletred",
    "slateblue"
]

fig = px.bar(filtered_data, x='Ship Mode', y='Sales', color='Sub-Category',
             labels={'Sales': 'Total Sales'},
             title=f'Sales Analysis for {", ".join(selected_categories)} under {", ".join(selected_modes)} Shipping Modes',
             barmode='group',
             color_discrete_sequence=colors)  # Setting barmode to 'stack' for stacked bar plot

st.plotly_chart(fig, use_container_width=True)

with st.expander("View Sales By Sub Categories and Ship Mode"):
    st.write(filtered_data.style.background_gradient(
        cmap="Oranges"))
    csv = sub_category_sales.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data as CSV', data=csv,
                       file_name="SubCategoryShipMode.csv", mime='text/csv')
    

total_sales_by_category_shipmode = df.groupby(['Category', 'Ship Mode'])['Sales'].sum().reset_index()


selected_cat = st.sidebar.multiselect('Select Categories', df['Category'].unique())

filtered_data = total_sales_by_category_shipmode[
    (total_sales_by_category_shipmode['Ship Mode'].isin(selected_modes)) & 
    (total_sales_by_category_shipmode['Category'].isin(selected_cat))
]

if len(filtered_data) == 0:
    filtered_data = total_sales_by_category_shipmode

fig = px.bar(filtered_data, x='Ship Mode', y='Sales', color='Category',
             labels={'Sales': 'Total Sales'},
             title=f'Sales Analysis for {", ".join(selected_cat)} under {", ".join(selected_modes)} Shipping Modes',
             barmode='stack',
             color_discrete_sequence=colors)  # Setting barmode to 'stack' for stacked bar plot

st.plotly_chart(fig, use_container_width=True)

with st.expander("View Sales By Categories and Ship Mode"):
    st.write(filtered_data.style.background_gradient(
        cmap="Oranges"))
    csv = sub_category_sales.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data as CSV', data=csv,
                       file_name="CategoryShipMode.csv", mime='text/csv')
    

filtered_df['Order Date'] = pd.to_datetime(filtered_df['Order Date'])
filtered_df['Ship Date'] = pd.to_datetime(filtered_df['Ship Date'])
filtered_df['Delivery Time'] = (filtered_df['Ship Date'] - filtered_df['Order Date']).dt.days

# Step 3: Plot histogram using Plotly and Streamlit
st.subheader("Delivery Time Histogram")

# Add a slider to choose the number of bins
num_bins = st.slider("Number of Bins", min_value=5, max_value=50, value=10)

# Create histogram using Plotly
fig = px.histogram(filtered_df, x='Delivery Time', nbins=num_bins, title="Delivery Time Histogram")
st.plotly_chart(fig,use_container_width=True)

from wordcloud import WordCloud
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse', False)
product_names = filtered_df['Product Name'].str.cat(sep=' ')
# Step 2: Generate Word Cloud
wordcloud = WordCloud(width=700, height=400, background_color='white',max_words=100000).generate(product_names)
# Step 3: Plot using Plotly and Streamlit
st.subheader("Product Name Word Cloud")
# Display the word cloud using Matplotlib
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.pyplot()
