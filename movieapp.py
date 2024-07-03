import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from get_films import transform_ratings, scrape_films, scrape_films_details, get_top_decades, get_rating_differences
from get_charts import show_years, show_avg_rating_by_year, show_actors, show_actors_table, show_directors, show_directors_table, show_top_decades, show_rating_differences
from recommend_films import recommend_movies

# st.set_page_config(layout="wide")

def main():
    st.title("LETTERBOXD PROFILE ANALYZER")

    username = st.text_input("Letterboxd Username", placeholder="Ex. Ther0")

    if st.button("Analyze Profile"):
        if username:
            st.subheader("Analyzing profile for " + username + "...") 
            df_film = scrape_films(username)
            df_rating, df_actor, df_director, df_genre, df_country = scrape_films_details(df_film)
            merged_df = pd.merge(df_film, df_rating)

            top_decades = get_top_decades(df_film, df_rating)

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

            higher_rated, lower_rated = get_rating_differences(df_film, df_rating)

            # USERNAME'S all time stats
            st.title(username + "'s all-time stats")
            cols = st.columns(4)
            with cols[0]:
                st.write(str(len(df_film.index)) + " FILMS")
            with cols[1]:
                st.write(str(int(df_rating['runtime'].sum()/60)) + " HOURS")
            with cols[2]:
                st.write(str(df_director['director'].nunique()) + " DIRECTORS")
            with cols[3]:
                st.write(str(df_country['country'].nunique()) + " COUNTRIES")

            st.markdown("""---""")

            st.subheader("BY YEAR")
            tabs = st.tabs(["Films", "Ratings"])
            with tabs[0]:
                show_years(df_film, df_rating)
            with tabs[1]:
                show_avg_rating_by_year(df_film, df_rating)

            st.markdown("""---""")

            st.subheader("HIGHEST RATED DECADES")
            show_top_decades(df_film, df_rating, top_decades)

            st.markdown("""---""")

            # Rating differences
            show_rating_differences(higher_rated, lower_rated)

            st.markdown("""---""")

            st.subheader("BY ACTOR")
            show_actors(df_actor_merged, df_temp_actor)

            st.markdown("""---""")

            st.subheader("BY DIRECTOR")
            show_directors(df_director_merged, df_temp_director)
            
        else:
            st.warning("Please enter a valid username")


if __name__ == "__main__":
    main()