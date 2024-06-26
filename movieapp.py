import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from get_films import transform_ratings, scrape_films, scrape_films_details
from get_charts import show_years, show_avg_rating_by_year, show_decades, show_actors, show_actors_table, show_deviation_above, show_deviation_below, show_directors, show_directors_table, show_scatterplots
from recommend_films import recommend_movies

st.set_page_config(layout="wide")

def main():
    st.title("LETTERBOXD PROFILE ANALYZER")

    username = st.text_input("Letterboxd Username", placeholder="Ex. Ther0")

    if st.button("Analyze Profile"):
        if username:
            st.write("Analyzing profile for username:", username)
            # progress bar, or loading bar
            df_film = scrape_films(username)
            df_rating, df_actor, df_director, df_genre, df_country = scrape_films_details(df_film)
            merged_df = pd.merge(df_film, df_rating)

            df_director_merged = pd.merge(df_film, df_director)
            # df_temp_director = pd.merge(df_director_merged.groupby(['director', 'director_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
            #                             df_director['director'].value_counts().reset_index().rename(columns = {'index':'director', 'director':'count'}))

            df_temp_director = pd.merge(df_director_merged.groupby(['director', 'director_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                                        df_director['director'].value_counts().reset_index())


            df_actor_merged = pd.merge(df_film, df_actor)
            # df_temp_actor = pd.merge(df_actor_merged.groupby(['actor', 'actor_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
            #                         df_actor['actor'].value_counts().reset_index().rename(columns = {'index':'actor', 'actor':'count'}))
            df_temp_actor = pd.merge(df_actor_merged.groupby(['actor', 'actor_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                                    df_actor['actor'].value_counts().reset_index())

            df_temp_director = df_temp_director.sort_values('count', ascending=False).reset_index(drop=True)
            n_director = df_temp_director.iloc[9]['count']
            df_temp_director = df_temp_director[df_temp_director['count']>=n_director]

            df_deviation = merged_df[['title', 'avg_rating', 'rating']]
            df_deviation['rating'] = pd.to_numeric(df_deviation['rating'])
            df_deviation['avg_rating'] = pd.to_numeric(df_deviation['avg_rating'])
            df_deviation['rating_difference'] = df_deviation['rating'] - df_deviation['avg_rating']

            # USERNAME'S all time stats
            st.header(username + "'s all-time stats")
            # number of: films, hours, directors, countries, etc.

            st.header("BY YEAR")
            col1, col2 = st.columns(2)
            with col1:
                show_years(df_film, df_rating)
            with col2:
                show_avg_rating_by_year(df_film, df_rating)

            st.header("BY DECADE")
            show_decades(df_film, df_rating)

            st.header("BY ACTOR")
            show_actors(df_actor_merged, df_temp_actor)

            st.header("BY DIRECTOR")
            show_directors(df_director_merged, df_temp_director)

            st.header("RATED HIGHER THAN AVERAGE")
            show_deviation_above(df_deviation)
            
            st.header("RATED LOWER THAN AVERAGE")
            show_deviation_below(df_deviation)
            # show_scatterplots()

            # st.title("Here are some recommendations")
            # recommend_movies(merged_df, username)
            
        else:
            st.warning("Please enter a valid username")


if __name__ == "__main__":
    main()