import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

df_reviews = pd.read_csv("./datasets/customer_reviews.csv",header=0,delimiter=",")
df_top100_books = pd.read_csv("./datasets/Top-100 Trending Books.csv",header=0,delimiter=",")

price_max = df_top100_books["book price"].max()
price_min = df_top100_books["book price"].min()
max_price =  st.sidebar.slider("Price Range", price_min, price_max, ((price_max+price_min)/2))

year_max = df_top100_books["year of publication"].max()
year_min = df_top100_books["year of publication"].min()
max_year =  st.sidebar.slider("Max year of publication", year_min, year_max, (year_max))

df_books = df_top100_books[(df_top100_books["book price"] <= max_price) & (df_top100_books["year of publication"] <= max_year)]
df_books

fig_bar = px.bar(df_books,
                 x="year of publication",
                 y="book price")

fig_scatter = px.scatter(df_books,
                 y="rating",
                 x="year of publication",
                #  color="genre",
                 size="book price",
                 hover_name="book title")


st.plotly_chart(fig_bar)
st.plotly_chart(fig_scatter)