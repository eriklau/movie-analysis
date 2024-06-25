import pandas as pd
import streamlit as st
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

df_movie = pd.read_csv('./data/movie_data.csv', lineterminator='\n')
df_ratings = pd.read_csv('./data/ratings_export.csv')
df_users = pd.read_csv('./data/users_export.csv')

df_merged_input_user = pd.read_csv('./data/merged_df.csv')

DOMAIN = "https://letterboxd.com"

def recommend_movies(df_merged_input_user, username):
    # Drop unnecessary columns in the input user data
    df_merged_input_user.rename(columns={'title': 'movie_title'}, inplace=True)
    df_merged_input_user.rename(columns={'rating': 'rating_val'}, inplace=True)
    # Add a new column 'movie_id' to df_merged_input_user by extracting it from 'link' column
    df_merged_input_user['movie_id'] = df_merged_input_user['link'].str.extract(r'/film/(.*?)/')

    # Drop unnecessary columns in the ratings data and change rating value to 0.5-5 stars
    df_ratings.drop('_id', axis=1, inplace=True)
    df_ratings['rating_val'] = df_ratings['rating_val'] / 2

    # Drop unnecessary columns in the movie data
    df_movie.drop(['_id', 'image_url', 'imdb_id', 'imdb_link', 'original_language',
                'overview', 'production_countries', 'spoken_languages', 'tmdb_id', 'tmdb_link'], 
                axis=1, inplace=True)
    df_movie['vote_average'] = df_movie['vote_average'] / 2

    # Convert the 'release_date' column to datetime
    df_movie['release_date'] = pd.to_datetime(df_movie['release_date'])


    # Merge df_merged_input_user with df_ratings
    merged_data = pd.concat([df_ratings, df_merged_input_user])
    merged_data.drop(['id', 'movie_title', 'liked', 'link', 'avg_rating',
                'year', 'watched_by', 'liked_by'], 
                axis=1, inplace=True)
    
    merged_data['letterboxd_link'] = DOMAIN + "/film/" + merged_data['movie_id'] + "/"
    
    # print(merged_data.head(10))

    # Create Surprise dataset
    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(merged_data[['user_id', 'movie_id', 'rating_val']], reader)

    # Split the data into training and testing sets
    trainset, testset = train_test_split(data, test_size=0.2)

    # Build the collaborative filtering model (SVD)
    model = SVD()
    model.fit(trainset)

    # Get movie recommendations for the current user
    current_user_id = username
    user_unrated_movies = df_movie[~df_movie['movie_id'].isin(merged_data[merged_data['user_id'] == current_user_id]['movie_id'])]
    user_unrated_movies['predicted_rating'] = user_unrated_movies['movie_id'].apply(lambda x: model.predict(current_user_id, x).est)

    # Sort the recommendations based on predicted ratings
    user_unrated_movies = user_unrated_movies.sort_values(by='predicted_rating', ascending=False)

    print(user_unrated_movies.head(10))

    # Display the movie recommendations
    # st.write(user_unrated_movies[['movie_title', 'predicted_rating', "letterboxd_link"]].head(50))

    # Export the top 50 predicted movies to a CSV file
    # top_predicted_movies = user_unrated_movies[['movie_title', 'predicted_rating']].head(50)
    # top_predicted_movies.to_csv('top_predicted_movies.csv', index=False)

# recommend_movies(df_merged_input_user, 'MeatyRicky')

# USERNAME'S all time stats
# number of: films, hours, directors, countries, shown in a single row with biggish title
# TOP FILMS?? -
# watched movies graph by release year +
# average rating by release year
# 3 highest rated decades, with the average score as subtitle, top 10 respective films in each decade shown as a picture link
# 3 charts in single row, most watched in: GENRES, COUNTRIES, LANGUAGES
# 3 charts in single row, highest rated in: GENRES, COUNTRIES, LANGUAGES, on average
# THEMES AND NONGENRES: MOST WATCHED AND HIGHEST RATED
# LIST PROGRESS WITH CIRCLE PROGRESSION CHARTS -
# COLLECTIONS (MAYBE) -
# top 10 most watched movies with picture link, with how many times watched below
# top movies with deviation above and below with picture link and their rating vs avg rating?
# TOP ACTORS with picture profile link, then maybe with liked/not liked chart
# TOP DIRECTORS etc...
# CREWS AND STUDIOS -
#

# most watched by decade
# top movies with deviation above and below with picture link and their rating vs avg rating?




