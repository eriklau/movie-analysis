import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

df_merged_input_user = pd.read_csv('./data/merged_df.csv')

df_movie = pd.read_csv('./data/movie_data.csv', lineterminator='\n')
df_ratings = pd.read_csv('./data/ratings_export.csv')
df_users = pd.read_csv('./data/users_export.csv')

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

# Create Surprise dataset
reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(merged_data[['user_id', 'movie_id', 'rating_val']], reader)

# Split the data into training and testing sets
trainset, testset = train_test_split(data, test_size=0.2)

# Build the collaborative filtering model (SVD)
model = SVD()
model.fit(trainset)

# Get movie recommendations for the current user
current_user_id = 'MeatyRicky'
user_unrated_movies = df_movie[~df_movie['movie_id'].isin(merged_data[merged_data['user_id'] == current_user_id]['movie_id'])]
user_unrated_movies['predicted_rating'] = user_unrated_movies['movie_id'].apply(lambda x: model.predict(current_user_id, x).est)

# Sort the recommendations based on predicted ratings
user_unrated_movies = user_unrated_movies.sort_values(by='predicted_rating', ascending=False)

# Display the movie recommendations
print(user_unrated_movies[['movie_title', 'predicted_rating']].head(10))

# Export the top 50 predicted movies to a CSV file
top_predicted_movies = user_unrated_movies[['movie_title', 'predicted_rating']].head(50)
top_predicted_movies.to_csv('top_predicted_movies.csv', index=False)