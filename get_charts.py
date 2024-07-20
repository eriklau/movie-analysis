import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
from tabulate import tabulate
from get_films import get_top_decades, get_top_movies_for_decade, get_rating_differences

DOMAIN = "https://letterboxd.com"

def show_years(df_film, df_rating):
    df_rating_merged = pd.merge(df_film, df_rating)
    df_rating_merged['year'] = df_rating_merged['year'].astype(int)
    df_years = df_rating_merged.groupby('year').size().reset_index(name='count')
    all_years = pd.DataFrame({'year': range(df_years['year'].dropna().min(), df_years['year'].dropna().max() + 1)})
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

def show_top_decades(df_film, df_rating, top_decades):
    top_decades, df_rating_merged = get_top_decades(df_film, df_rating)
    hover_css = """
        <style>
            .movie-poster {
                border: 2px solid transparent;
                transition: border-color 0.3s;
            }
            .movie-poster:hover {
                border-color: white;
            }
        </style>
    """
    st.markdown(hover_css, unsafe_allow_html=True)

    for _, row in top_decades.iterrows():
        decade = row['decade']
        avg_rating = row['avg_rating']
        top_movies = get_top_movies_for_decade(df_rating_merged, decade)
        
        st.subheader(f"{int(decade)}s: ★ Average {avg_rating:.2f}")
        
        cols = st.columns(10)
        top_movies = top_movies.head(20)

        for idx, (i, movie) in enumerate(top_movies.iterrows()):
            with cols[idx % 10]:
                image_html = f'''
                <a href="{DOMAIN + movie['link']}" target="_blank">
                    <img src="{movie['image_url']}" width="70" class="movie-poster" alt="{movie['title']}">
                </a>
                '''
                st.markdown(image_html, unsafe_allow_html=True)

def show_rating_differences(higher_rated, lower_rated):
    hover_css = """
    <style>
    .movie-poster {
        border: 2px solid transparent;
        transition: border-color 0.3s;
    }
    .movie-poster:hover {
        border-color: white;
    }
    p {
        text-align: center;
    }
    </style>
    """
    st.markdown(hover_css, unsafe_allow_html=True)

    st.subheader("RATED HIGHER THAN AVERAGE")
    higher_container = st.container()
    with higher_container:
        cols = st.columns(6)
        for idx, (i, movie) in enumerate(higher_rated.iterrows()):
            with cols[idx % 6]:
                image_html = f'''
                <a href="{DOMAIN + movie['link']}" target="_blank">
                    <img src="{movie['image_url']}" width="110" class="movie-poster" alt="{movie['title']}">
                </a>
                '''
                st.markdown(image_html, unsafe_allow_html=True)
                st.write(f"{movie['rating']} vs {float(movie['avg_rating']):.2f}")
    
    st.markdown("""---""")

    st.subheader("RATED LOWER THAN AVERAGE")
    lower_container = st.container()
    with lower_container:
        cols = st.columns(6)
        for idx, (i, movie) in enumerate(lower_rated.iterrows()):
            with cols[idx % 6]:
                image_html = f'''
                <a href="{DOMAIN + movie['link']}" target="_blank">
                    <img src="{movie['image_url']}" width="110" class="movie-poster" alt="{movie['title']}">
                </a>
                '''
                st.markdown(image_html, unsafe_allow_html=True)
                st.write(f"{movie['rating']} vs {float(movie['avg_rating']):.2f}")

def show_most_watched_actors(df_actor_merged, df_temp_actor):
    filtered_actors = df_actor_merged[df_actor_merged['actor'].isin(df_temp_actor['actor'])]
    top_actors = filtered_actors.groupby(['actor']).size().sort_values(ascending=False).head(10).reset_index(name='count')

    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(top_actors).mark_bar().encode(
        y=alt.Y('actor:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Actor')),
        x=alt.X('count:Q', axis=alt.Axis(title='Count')),
        color=alt.value('#00b0f0'),
        tooltip=[alt.Tooltip('actor:O', title='Actor'), alt.Tooltip('count:Q', title='Count')]
    )

    hover = alt.Chart(top_actors).mark_bar(color='lightblue').encode(
        y=alt.Y('actor:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Actor')),
        x=alt.X('count:Q', axis=alt.Axis(title='Count')),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='MOST WATCHED ACTORS',
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
    )

    st.altair_chart(chart, use_container_width=True)


def show_highest_rated_actors(df_actor_merged, df_temp_actor):
    filtered_actors = df_actor_merged[df_actor_merged['actor'].isin(df_temp_actor['actor'])]
    top_actors = filtered_actors.groupby(['actor']).agg({'rating': 'mean'}).sort_values(by='rating', ascending=False).head(10).reset_index()
    
    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(top_actors).mark_bar().encode(
        y=alt.Y('actor:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Actor')),
        x=alt.X('rating:Q', axis=alt.Axis(title='Average Rating')),
        color=alt.value('#ff8000'),
        tooltip=[alt.Tooltip('actor:O', title='Actor'), alt.Tooltip('rating:Q', title='Average Rating')]
    )

    hover = alt.Chart(top_actors).mark_bar(color='lightblue').encode(
        y=alt.Y('actor:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Actor')),
        x=alt.X('rating:Q', axis=alt.Axis(title='Average Rating')),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='HIGHEST RATED ACTORS',
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
    )

    st.altair_chart(chart, use_container_width=True)

def show_most_watched_directors(df_director_merged, df_temp_director):
    filtered_directors = df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])]
    top_directors = filtered_directors.groupby(['director']).size().sort_values(ascending=False).head(10).reset_index(name='count')

    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(top_directors).mark_bar().encode(
        y=alt.Y('director:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Director')),
        x=alt.X('count:Q', axis=alt.Axis(title='Count')),
        color=alt.value('#00b0f0'),
        tooltip=[alt.Tooltip('director:O', title='Director'), alt.Tooltip('count:Q', title='Count')]
    )

    hover = alt.Chart(top_directors).mark_bar(color='lightblue').encode(
        y=alt.Y('director:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Director')),
        x=alt.X('count:Q', axis=alt.Axis(title='Count')),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='MOST WATCHED DIRECTORS',
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
    )

    st.altair_chart(chart, use_container_width=True)


def show_highest_rated_directors(df_director_merged, df_temp_director):
    filtered_directors = df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])]
    top_directors = filtered_directors.groupby(['director']).agg({'rating': 'mean'}).sort_values(by='rating', ascending=False).head(10).reset_index()
    
    highlight = alt.selection(type='single', on='mouseover', nearest=True)

    bars = alt.Chart(top_directors).mark_bar().encode(
        y=alt.Y('director:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Director')),
        x=alt.X('rating:Q', axis=alt.Axis(title='Average Rating')),
        color=alt.value('#ff8000'),
        tooltip=[alt.Tooltip('director:O', title='Director'), alt.Tooltip('rating:Q', title='Average Rating')]
    )

    hover = alt.Chart(top_directors).mark_bar(color='lightblue').encode(
        y=alt.Y('director:O', sort='-x', axis=alt.Axis(labelAngle=0, title='Director')),
        x=alt.X('rating:Q', axis=alt.Axis(title='Average Rating')),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
    ).add_selection(
        highlight
    )

    chart = alt.layer(
        bars, hover
    ).properties(
        title='HIGHEST RATED DIRECTORS',
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
    )

    st.altair_chart(chart, use_container_width=True)


def show_directors_table(df_temp_director):
    # Display the top 10 directors in a table
    tabulate(df_temp_director.sort_values('count', ascending=False).head(10), headers='keys', tablefmt='pretty', showindex=False)

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