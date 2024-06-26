import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
from tabulate import tabulate

# df_merged = pd.read_csv('./data/merged_df.csv')
# df_film = pd.read_csv('./data/df_film.csv')
# df_rating = pd.read_csv('./data/df_rating.csv')
# df_actor = pd.read_csv('./data/df_actor.csv')
# df_director = pd.read_csv('./data/df_director.csv')
# df_genre = pd.read_csv('./data/df_genre.csv')

# df_director_merged = pd.merge(df_film, df_director)
# # Calculate aggregate values for directors and actors
# df_temp_director = pd.merge(df_director_merged.groupby(['director', 'director_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
#                             df_director['director'].value_counts().reset_index().rename(columns = {'index':'director', 'director':'count'}))

# df_actor_merged = pd.merge(df_film, df_actor)
# df_temp_actor = pd.merge(df_actor_merged.groupby(['actor', 'actor_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
#                         df_actor['actor'].value_counts().reset_index().rename(columns = {'index':'actor', 'actor':'count'}))

# df_temp_director = df_temp_director.sort_values('count', ascending=False).reset_index(drop=True)
# n_director = df_temp_director.iloc[9]['count']
# df_temp_director = df_temp_director[df_temp_director['count']>=n_director]

# df_deviation = df_merged[['title', 'avg_rating', 'rating']]
# df_deviation['rating_difference'] = df_deviation['rating'] - df_deviation['avg_rating']

# print(type(df_deviation['rating'][0]))
# print(type(df_deviation['avg_rating'][0]))

import altair as alt

import altair as alt

def show_years(df_film, df_rating):
    df_rating_merged = pd.merge(df_film, df_rating)
    df_rating_merged['year'] = df_rating_merged['year'].astype(int)
    df_years = df_rating_merged.groupby('year').size().reset_index(name='count')
    all_years = pd.DataFrame({'year': range(df_years['year'].min(), df_years['year'].max() + 1)})
    df_years = all_years.merge(df_years, on='year', how='left').fillna(0.5)
    df_years['tooltip_count'] = df_years['count'].apply(lambda x: 0 if x == 0.5 else x)

    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(df_years).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(labelAngle=90)),
        y='count:Q',
        color=alt.condition(
            alt.datum.count > 0.5,
            alt.value('#00b0f0'),
            alt.value('#A9A9A9') 
        ),
        tooltip=[alt.Tooltip('year:O', title='Year'), alt.Tooltip('tooltip_count:Q', title='Count')]
    )

    hover = alt.Chart(df_years).mark_bar(color='lightblue').encode(
        x=alt.X('year:O', axis=alt.Axis(labelAngle=90)),
        y='count:Q',
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='Films',
        width=800,
        height=400
    )

    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelColor='#ffffff',
        titleColor='#ffffff'
    ).configure_view(
        strokeOpacity=0
    ).configure_axisX(
        labelAngle=0,
        labelOverlap=True,
        labelFontSize=10,
        tickCount=10,
        labelExpr="datum.value % 10 === 0 ? datum.label : ''"
    )

    st.altair_chart(chart, use_container_width=True)

import altair as alt
import pandas as pd
import streamlit as st

def show_avg_rating_by_year(df_film, df_rating):
    df_rating_merged = pd.merge(df_film, df_rating, on='id')
    df_rating_merged['year'] = df_rating_merged['year'].astype(int)

    df_avg_rating = df_rating_merged.groupby('year')['rating'].mean().reset_index()
    all_years = pd.DataFrame({'year': range(df_avg_rating['year'].min(), df_avg_rating['year'].max() + 1)})
    df_avg_rating = all_years.merge(df_avg_rating, on='year', how='left').fillna(0.5)
    df_avg_rating['tooltip_avg_rating'] = df_avg_rating['rating'].apply(lambda x: 0 if x == 0.5 else x)

    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(df_avg_rating).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(labelAngle=90)),
        y='rating:Q',
        color=alt.condition(
            alt.datum.rating > 0.5,
            alt.value('#ff8000'),  # Orange for average rating
            alt.value('#A9A9A9')  # Grey for no rating
        ),
        tooltip=[alt.Tooltip('year:O', title='Year'), alt.Tooltip('tooltip_avg_rating:Q', title='Average Rating')]
    )

    hover = alt.Chart(df_avg_rating).mark_bar(color='#ffa500').encode(
        x=alt.X('year:O', axis=alt.Axis(labelAngle=90)),
        y='rating:Q',
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='Ratings',
        width=800,
        height=400
    )

    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelColor='#ffffff',
        titleColor='#ffffff'
    ).configure_view(
        strokeOpacity=0
    ).configure_axisX(
        labelAngle=0,
        labelOverlap=True,
        labelFontSize=10,
        tickCount=10,
        labelExpr="datum.value % 10 === 0 ? datum.label : ''"
    ).configure_axisY(
        title='Average Rating',
        labels=False,
        titleColor='#ffffff'
    )

    st.altair_chart(chart, use_container_width=True)

def show_decades(df_film, df_rating):
    # Merge df_film and df_rating
    df_rating_merged = pd.merge(df_film, df_rating)

    # Replace True/False in 'liked' column with 'Liked'/'Not Liked'
    df_rating_merged['liked'] = df_rating_merged['liked'].map({True: 'Liked', False: 'Not Liked'})

    # Extract decade from the 'year' column and create a new 'decade' column
    df_rating_merged['decade'] = df_rating_merged['year']

    # Create a pivot table to get counts of liked and not liked movies for each decade
    pivot_table = df_rating_merged.pivot_table(index='decade', columns='liked', values='id', aggfunc='count', fill_value=0)

    # Ensure the pivot table has both 'Liked' and 'Not Liked' columns
    if 'Liked' not in pivot_table.columns:
        pivot_table['Liked'] = 0
    if 'Not Liked' not in pivot_table.columns:
        pivot_table['Not Liked'] = 0

    # Reverse the order of columns to switch stacking order
    pivot_table = pivot_table[['Liked', 'Not Liked']]  # <-- Switched the order here

    # Create the stacked bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_table.plot(kind='bar', stacked=True, ax=ax, color=['#ff8000', '#00b020',], edgecolor='black')

    # Set labels and title
    ax.set_xlabel('Decade')
    ax.set_ylabel('Count')
    ax.set_title('Movies Liked and Not Liked by Decade')

    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Show the plot
    st.pyplot(fig)

def show_directors_table(df_temp_director):
    # Display the top 10 directors in a table
    tabulate(df_temp_director.sort_values('count', ascending=False).head(10), headers='keys', tablefmt='pretty', showindex=False)

def show_actors_table(df_temp_actor):
    # Display the top 10 actors in a table
    tabulate(df_temp_actor.sort_values('count', ascending=False).head(10), headers='keys', tablefmt='pretty', showindex=False)

def show_directors(df_director_merged, df_temp_director):
    # Filter the DataFrame to include only directors present in df_temp_director
    filtered_directors = df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])]

    # Calculate the count of liked and not liked movies per director
    director_likes = filtered_directors.groupby('director')['liked'].sum()
    director_dislikes = filtered_directors.groupby('director')['liked'].count() - director_likes

    # Get the top 10 most watched directors
    top_directors = director_likes.add(director_dislikes).sort_values(ascending=False).head(10)

    # Create the horizontal stacked bar plot using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_positions = np.arange(len(top_directors))
    bar_width = 0.6

    colors = ['#ff8000', '#00b020']

    bottom = np.zeros(len(top_directors))

    for color, label in zip(colors, ['Liked', 'Not Liked']):
        values = [director_likes.get(director, 0) if label == 'Liked' else director_dislikes.get(director, 0) for director in top_directors.index]
        ax.barh(bar_positions, values,
                color=color, edgecolor='black', height=bar_width, label=label, left=bottom)
        bottom += values

    # Set the axis labels and title
    plt.xlabel('Number of Movies')
    plt.ylabel('Director')
    plt.title('Top 10 Most Watched Directors and Liked/Not Liked Movies')
    plt.yticks(bar_positions, top_directors.index)

    # Invert y-axis to show the director with the highest count at the top
    plt.gca().invert_yaxis()

    # Add legend
    plt.legend()

    # Display the plot
    st.pyplot(fig)

def show_actors(df_actor_merged, df_temp_actor):
    # Filter the DataFrame to include only actors present in df_temp_actor
    filtered_actors = df_actor_merged[df_actor_merged['actor'].isin(df_temp_actor['actor'])]

    # Calculate the count of liked and not liked movies per actor
    actor_likes = filtered_actors.groupby('actor')['liked'].sum()
    actor_dislikes = filtered_actors.groupby('actor')['liked'].count() - actor_likes

    # Get the top 10 most watched actors
    top_actors = actor_likes.add(actor_dislikes).sort_values(ascending=False).head(10)

    # Create the horizontal stacked bar plot using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_positions = np.arange(len(top_actors))
    bar_width = 0.6

    colors = ['#ff8000', '#00b020']

    bottom = np.zeros(len(top_actors))

    for color, label in zip(colors, ['Liked', 'Not Liked']):
        values = [actor_likes.get(actor, 0) if label == 'Liked' else actor_dislikes.get(actor, 0) for actor in top_actors.index]
        ax.barh(bar_positions, values,
                color=color, edgecolor='black', height=bar_width, label=label, left=bottom)
        bottom += values

    # Set the axis labels and title
    plt.xlabel('Number of Movies')
    plt.ylabel('Actor')
    plt.title('Top 10 Most Watched Actors and Liked/Not Liked Movies')
    plt.yticks(bar_positions, top_actors.index)

    # Invert y-axis to show the actor with the highest count at the top
    plt.gca().invert_yaxis()

    # Add legend
    plt.legend()

    # Display the plot
    st.pyplot(fig)

def show_deviation_below(df_deviation):
    # Sort the DataFrame by "rating_difference" in ascending order
    lowest_deviation_movies = df_deviation.sort_values('rating_difference', ascending=True)

    # Select the 10 lowest rows
    top_lowest_deviation = lowest_deviation_movies.head(10)

    # Create a bar graph using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.barh(top_lowest_deviation['title'], top_lowest_deviation['rating_difference'], color='#00b020')
    plt.xlabel('Rating Difference')
    plt.ylabel('Movie Title')
    plt.title('Top 10 Movies with Lowest Rating Deviation')
    plt.gca().invert_yaxis()  # Invert y-axis to have the movie with the lowest deviation at the top
    st.pyplot(plt)



def show_deviation_above(df_deviation):
    # Sort the DataFrame by "rating_difference" in descending order
    highest_deviation_movies = df_deviation.sort_values('rating_difference', ascending=False)

    # Select the 10 highest rows
    top_highest_deviation = highest_deviation_movies.head(10)

    # Create a bar graph using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.barh(top_highest_deviation['title'], top_highest_deviation['rating_difference'], color='orange')
    plt.xlabel('Rating Difference')
    plt.ylabel('Movie Title')
    plt.title('Top 10 Movies with Highest Rating Deviation')
    plt.gca().invert_yaxis()  # Invert y-axis to have the movie with the highest deviation at the top
    st.pyplot(plt)


def show_scatterplots(df_merged):
    # Number of Likes vs Number of Watches
    plt.figure(figsize=(10, 6))
    plt.scatter(df_merged['liked_by'], df_merged['watched_by'], alpha=0.5)
    plt.xlabel('Number of Likes')
    plt.ylabel('Number of Watches')
    plt.title('Scatterplot: Number of Likes vs Number of Watches')
    plt.grid(True)
    plt.show()

    # Release Year vs Number of Likes
    plt.figure(figsize=(10, 6))
    plt.scatter(df_merged['year'], df_merged['liked_by'], alpha=0.5)
    plt.xlabel('Release Year')
    plt.ylabel('Number of Likes')
    plt.title('Scatterplot: Release Year vs Number of Likes')
    plt.grid(True)
    plt.show()

    # Release Year vs Average User Rating
    plt.figure(figsize=(10, 6))
    plt.scatter(df_merged['year'], df_merged['avg_rating'], alpha=0.5)
    plt.xlabel('Release Year')
    plt.ylabel('Average User Rating')
    plt.title('Scatterplot: Release Year vs Average User Rating')
    plt.grid(True)
    plt.show()