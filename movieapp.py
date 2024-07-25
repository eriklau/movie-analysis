import streamlit as st
import pandas as pd
from get_films import scrape_films, scrape_films_details, get_top_decades, get_rating_differences
from get_charts import show_top_20_films, show_years, show_avg_rating_by_year, show_top_decades, show_rating_differences, show_most_watched_actors, show_highest_rated_actors, show_most_watched_directors, show_highest_rated_directors, show_genres_chart, show_countries_chart, show_languages_chart
from recommend_films import recommend_movies
from openai import OpenAI
import json
import psutil
import os
from memory_profiler import profile
import base64
from PIL import Image
import io

# st.set_page_config(layout="wide")

def main():
    def get_memory_usage():
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return mem_info.rss / (1024 * 1024)  # Convert bytes to MB

    # Display memory usage
    memory_usage = get_memory_usage()
    st.write(f"Current memory usage: {memory_usage:.2f} MB")

    st.title("LETTERBOXD MOVIE STATS")

    if "analyze_button" not in st.session_state:
        st.session_state.analyze_button = False
    if "send_button" not in st.session_state:
        st.session_state.send_button = False

    username = st.text_input("LETTERBOXD USERNAME", placeholder="Ex. Attributions")

    if st.button("Analyze Profile"):
        st.session_state.analyze_button = True
        st.session_state.scraped_data = None

    if st.session_state.analyze_button and username:
        if st.session_state.scraped_data is None:
            st.subheader("Analyzing profile for " + username + "...")
            df_film = scrape_films(username)
            df_rating, df_actor, df_director, df_genre, df_country, df_language = scrape_films_details(df_film)
            merged_df = pd.merge(df_film, df_rating)

            top_decades = get_top_decades(df_film, df_rating)

            df_director_merged = pd.merge(df_film, df_director)
            df_temp_director = pd.merge(df_director_merged.groupby(['director', 'director_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                                        df_director['director'].value_counts().reset_index())

            df_actor_merged = pd.merge(df_film, df_actor)
            df_temp_actor = pd.merge(df_actor_merged.groupby(['actor', 'actor_link']).agg({'liked':'sum', 'rating':'mean'}).reset_index(),
                                    df_actor['actor'].value_counts().reset_index())

            df_genre_merged = pd.merge(df_film, df_genre)
            df_country_merged = pd.merge(df_film, df_country)
            df_language_merged = pd.merge(df_film, df_language)

            df_temp_director = df_temp_director.sort_values('count', ascending=False).reset_index(drop=True)
            n_director = df_temp_director.iloc[9]['count']
            df_temp_director = df_temp_director[df_temp_director['count']>=n_director]

            df_deviation = merged_df[['title', 'avg_rating', 'rating']]
            df_deviation['rating'] = pd.to_numeric(df_deviation['rating'])
            df_deviation['avg_rating'] = pd.to_numeric(df_deviation['avg_rating'])
            df_deviation['rating_difference'] = df_deviation['rating'] - df_deviation['avg_rating']

            higher_rated, lower_rated = get_rating_differences(df_film, df_rating)

            st.session_state.scraped_data = {
                "df_film": df_film,
                "df_rating": df_rating,
                "df_actor": df_actor,
                "df_director": df_director,
                "df_genre": df_genre,
                "df_country": df_country,
                "df_language": df_language,
                "merged_df": merged_df,
                "top_decades": top_decades,
                "df_director_merged": df_director_merged,
                "df_temp_director": df_temp_director,
                "df_actor_merged": df_actor_merged,
                "df_temp_actor": df_temp_actor,
                "df_genre_merged": df_genre_merged,
                "df_country_merged": df_country_merged,
                "df_language_merged": df_language_merged,
                "higher_rated": higher_rated,
                "lower_rated": lower_rated,
            }

        data = st.session_state.scraped_data

        # Rest of the code using data from st.session_state.scraped_data
        df_film = data["df_film"]
        df_rating = data["df_rating"]
        df_actor = data["df_actor"]
        df_director = data["df_director"]
        df_genre = data["df_genre"]
        df_country = data["df_country"]
        df_language = data["df_language"]
        merged_df = data["merged_df"]
        top_decades = data["top_decades"]
        df_director_merged = data["df_director_merged"]
        df_temp_director = data["df_temp_director"]
        df_actor_merged = data["df_actor_merged"]
        df_temp_actor = data["df_temp_actor"]
        df_genre_merged = data["df_genre_merged"]
        df_country_merged = data["df_country_merged"]
        df_language_merged = data["df_language_merged"]
        higher_rated = data["higher_rated"]
        lower_rated = data["lower_rated"]

        st.markdown("""
        <style>
            h1 {
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # USERNAME'S all time stats
        st.title(username + "'s all-time stats")
        st.markdown("""---""")
        cols = st.columns(2)
        with cols[0]:
            st.title(str(len(df_film.index)) + " FILMS")
            st.title(str(df_director['director'].nunique()) + " DIRECTORS")
        with cols[1]:
            st.title(str(int(df_rating['runtime'].sum()/60)) + " HOURS")
            st.title(str(df_country['country'].nunique()) + " COUNTRIES")

        st.markdown("""---""")

        st.subheader("TOP FILMS")
        show_top_20_films(merged_df)

        st.markdown("""---""")

        st.subheader("BY YEAR")
        year_tabs = st.tabs(["FILMS", "RATINGS"])
        with year_tabs[0]:
            show_years(df_film, df_rating)
        with year_tabs[1]:
            show_avg_rating_by_year(df_film, df_rating)

        st.markdown("""---""")

        st.subheader("HIGHEST RATED DECADES")
        show_top_decades(df_film, df_rating, top_decades)

        st.markdown("""---""")

        # Rating differences
        show_rating_differences(higher_rated, lower_rated)

        st.markdown("""---""")
        st.subheader("GENRES, COUNTRIES & LANGUAGES")
        genre_tabs = st.tabs(["MOST WATCHED", "HIGHEST RATED"])

        with genre_tabs[0]:
            col1, col2, col3 = st.columns(3)
            with col1:
                show_genres_chart(df_genre, "", "green", "lightgreen")
            with col2:
                show_countries_chart(df_country, "", "#00b0f0", "lightblue")
            with col3:
                show_languages_chart(df_language, "", "#ff8000", "#ffd700")

        with genre_tabs[1]:
            col1, col2, col3 = st.columns(3)
            with col1:
                show_genres_chart(df_genre_merged, "", "lightgreen", "green", avg_rating=True)
            with col2:
                show_countries_chart(df_country_merged, "", "lightblue", "#00b0f0", avg_rating=True)
            with col3:
                show_languages_chart(df_language_merged, "", "#ffd700", "#ff8000", avg_rating=True)

        st.markdown("""---""")

        st.subheader("TOP STARS")
        stars_tabs = st.tabs(["MOST WATCHED", "HIGHEST RATED"])
        with stars_tabs[0]:
            show_most_watched_actors(df_actor_merged, df_temp_actor)
        with stars_tabs[1]:
            show_highest_rated_actors(df_actor_merged, df_temp_actor)

        st.markdown("""---""")

        st.subheader("TOP DIRECTORS")
        directors_tabs = st.tabs(["MOST WATCHED", "HIGHEST RATED"])
        with directors_tabs[0]:
            show_most_watched_directors(df_director_merged, df_temp_director)
        with directors_tabs[1]:
            show_highest_rated_directors(df_director_merged, df_temp_director)

        st.markdown("""---""")

        user_info = {
            'top_20_films': merged_df.sort_values(by='rating', ascending=False).head(20)[['title', 'rating']].to_dict(orient='records'),
            'top_watched_genres': df_genre['genre'].value_counts().head(10).reset_index().to_dict(orient='records'),
            'top_watched_actors': df_actor_merged[df_actor_merged['actor'].isin(df_temp_actor['actor'])].groupby(['actor']).size().sort_values(ascending=False).head(20).reset_index(name='count').to_dict(orient='records'),
            'top_watched_directors': df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])].groupby(['director']).size().sort_values(ascending=False).head(20).reset_index(name='count').to_dict(orient='records'),
            'top_rated_genres': df_genre_merged.groupby('genre')['rating'].mean().sort_values(ascending=False).head(10).reset_index().to_dict(orient='records'),
            'top_rated_directors': df_director_merged[df_director_merged['director'].isin(df_temp_director['director'])].groupby(['director']).agg({'rating': 'mean'}).sort_values(by='rating', ascending=False).head(20).reset_index().to_dict(orient='records'),
            'top_higher_than_avg': higher_rated[['title', 'rating', 'avg_rating', 'rating_diff']].to_dict(orient='records'),
            'top_lower_than_avg': lower_rated[['title', 'rating', 'avg_rating', 'rating_diff']].to_dict(orient='records'),
            'top_rated_countries': df_country_merged.groupby('country')['rating'].mean().sort_values(ascending=False).head(10).reset_index().to_dict(orient='records'),
            'top_watched_countries': df_country['country'].value_counts().head(10).reset_index().to_dict(orient='records'),
            'top_watched_languages': df_language['language'].value_counts().head(10).reset_index().to_dict(orient='records'),
        }

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Set a default model
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o-mini"

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Image uploader
        uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

        # Function to encode image to base64
        def encode_image_to_base64(image):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str

        if uploaded_image:
            # Display the uploaded image
            image = Image.open(uploaded_image)
            st.image(image, caption='Uploaded Image', use_column_width=True)

            # Encode image to base64
            encoded_image = encode_image_to_base64(image)

        # Accept user input
        if prompt := st.chat_input(""):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Prepend background information to the prompt
            background_info_text = json.dumps(user_info)
            full_prompt = f"""You are a 'movie buddy' assistant.
            You take in JSON information about a user's Letterboxd movie preferences, and then recommend movies to the user. 
            For each recommended movie, provide a link to its Letterboxd page in the format https://letterboxd.com/film/FILM-NAME/, 
            where spaces in the film name are replaced by hyphens (-). Then, give a short, exciting summary of the movie based on user preferences. 
            Tailor these summaries to highlight aspects the user is likely to find interesting.
            DO NOT give more than 5 recommendations unless asked otherwise, and always keep your response short.
            Be able to identify scenes from user image uploaded screenshots, and then provide the link to its Letterboxd page.
            Generate reviews for movies based on user ratings and user reviews in their particular writing style.
            Here is the JSON data about the user's movie preferences: {background_info_text}
            """

            if uploaded_image:
                full_prompt += f"\nHere is an encoded image for scene identification: {encoded_image}"

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ] + [{"role": "user", "content": full_prompt}],
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()