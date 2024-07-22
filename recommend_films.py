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
    df_merged_input_user.rename(columns={'title': 'movie_title'}, inplace=True)
    df_merged_input_user.rename(columns={'rating': 'rating_val'}, inplace=True)
    df_merged_input_user['movie_id'] = df_merged_input_user['link'].str.extract(r'/film/(.*?)/')
    df_ratings.drop('_id', axis=1, inplace=True)
    df_ratings['rating_val'] = df_ratings['rating_val'] / 2

    df_movie.drop(['_id', 'image_url', 'imdb_id', 'imdb_link', 'original_language',
                'overview', 'production_countries', 'spoken_languages', 'tmdb_id', 'tmdb_link'], 
                axis=1, inplace=True)
    df_movie['vote_average'] = df_movie['vote_average'] / 2

    df_movie['release_date'] = pd.to_datetime(df_movie['release_date'])

    merged_data = pd.concat([df_ratings, df_merged_input_user])
    merged_data.drop(['id', 'movie_title', 'liked', 'link', 'avg_rating',
                'year', 'watched_by', 'liked_by'], 
                axis=1, inplace=True)
    
    merged_data['letterboxd_link'] = DOMAIN + "/film/" + merged_data['movie_id'] + "/"
    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(merged_data[['user_id', 'movie_id', 'rating_val']], reader)
    trainset, testset = train_test_split(data, test_size=0.2)
    model = SVD()
    model.fit(trainset)
    current_user_id = username
    user_unrated_movies = df_movie[~df_movie['movie_id'].isin(merged_data[merged_data['user_id'] == current_user_id]['movie_id'])]
    user_unrated_movies['predicted_rating'] = user_unrated_movies['movie_id'].apply(lambda x: model.predict(current_user_id, x).est)
    user_unrated_movies = user_unrated_movies.sort_values(by='predicted_rating', ascending=False)