import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from tabulate import tabulate

df_merged = pd.read_csv('./data/merged_df.csv')
df_film = pd.read_csv('./data/df_film.csv')
df_rating = pd.read_csv('./data/df_rating.csv')
df_actor = pd.read_csv('./data/df_actor.csv')
df_director = pd.read_csv('./data/df_director.csv')
df_genre = pd.read_csv('./data/df_genre.csv')

df_director_merged = pd.merge(df_film, df_director)
# Calculate aggregate values for directors and actors
df_temp_director = pd.merge(df_director_merged.groupby(['director', 'director_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                            df_director['director'].value_counts().reset_index().rename(columns = {'index':'director', 'director':'count'}))

df_actor_merged = pd.merge(df_film, df_actor)
df_temp_actor = pd.merge(df_actor_merged.groupby(['actor', 'actor_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                        df_actor['actor'].value_counts().reset_index().rename(columns = {'index':'actor', 'actor':'count'}))

df_temp_director = df_temp_director.sort_values('count', ascending=False).reset_index(drop=True)
n_director = df_temp_director.iloc[9]['count']
df_temp_director = df_temp_director[df_temp_director['count']>=n_director]

def show_years():
    # Merge df_film and df_rating
    df_rating_merged = pd.merge(df_film, df_rating)

    # Replace True/False in 'liked' column with 'Liked'/'Not Liked'
    df_rating_merged['liked'] = df_rating_merged['liked'].map({True: 'Liked', False: 'Not Liked'})

    # Create a pivot table to get counts of liked and not liked movies for each year
    pivot_table = df_rating_merged.pivot_table(index='year', columns='liked', values='id', aggfunc='count', fill_value=0)

    # Reverse the order of columns to switch stacking order
    pivot_table = pivot_table[['Liked', 'Not Liked']]  # <-- Switched the order here

    # Create the stacked bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_table.plot(kind='bar', stacked=True, ax=ax, color=['#ff8000','#00b020'], edgecolor='black')

    # Set labels and title
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    ax.set_title('Movies Liked and Not Liked by Year')

    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=90)

    # Show the plot
    plt.tight_layout()
    plt.show()

def show_decades():
    # Merge df_film and df_rating
    df_rating_merged = pd.merge(df_film, df_rating)

    # Replace True/False in 'liked' column with 'Liked'/'Not Liked'
    df_rating_merged['liked'] = df_rating_merged['liked'].map({True: 'Liked', False: 'Not Liked'})

    # Extract decade from the 'year' column and create a new 'decade' column
    df_rating_merged['decade'] = df_rating_merged['year'] // 10 * 10

    # Create a pivot table to get counts of liked and not liked movies for each decade
    pivot_table = df_rating_merged.pivot_table(index='decade', columns='liked', values='id', aggfunc='count', fill_value=0)

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
    plt.tight_layout()
    plt.show()

def show_directors_table():
    # Display the top 10 directors in a table
    tabulate(df_temp_director.sort_values('count', ascending=False).head(10), headers='keys', tablefmt='pretty', showindex=False)

def show_actors_table():
    # Display the top 10 actors in a table
    tabulate(df_temp_actor.sort_values('count', ascending=False).head(10), headers='keys', tablefmt='pretty', showindex=False)


def show_directors():
    # Filter the DataFrame to include only directors present in df_temp_director
    filtered_directors = df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])]

    # Calculate the count of liked directors
    director_likes = filtered_directors.groupby('director')['liked'].sum()

    # Create the area plot using Matplotlib
    colors = ['#ff8000' if liked else '#00b020' for liked in director_likes.index]
    plt.barh(director_likes.index, director_likes, color=colors)

    # Set the axis labels and title
    plt.xlabel('Count of Liked Directors')
    plt.ylabel('Director')
    plt.title('Director Statistics')

    # Rotate the y-axis labels to avoid overlap
    plt.yticks(rotation=0)

    # Display the plot
    plt.show()





# show_years()
# show_decades()
# show_directors_table()
# show_actors_table()
show_directors()
# show_years()
# show_decades()
# show_directors_table()
# show_actors_table()

