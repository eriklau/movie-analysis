import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import numpy as np
import json

DOMAIN = "https://letterboxd.com"

def transform_ratings(some_str):
    stars = {
        "½": 0.5,
        "★": 1,
        "★½": 1.5,
        "★★": 2,
        "★★½": 2.5,
        "★★★": 3,
        "★★★½": 3.5,
        "★★★★": 4,
        "★★★★½": 4.5,
        "★★★★★": 5,
    }
    try:
        return stars[some_str]
    except:
        return -1

def scrape_films(username):
    movies_dict = {}
    movies_dict['id'] = []
    movies_dict['title'] = []
    movies_dict['rating'] = []
    movies_dict['liked'] = []
    movies_dict['link'] = []
    url = DOMAIN + "/" + username + "/films/"
    url_page = requests.get(url)
    if url_page.status_code != 200:
        raise Exception("")
    soup = BeautifulSoup(url_page.content, 'html.parser')
    
    # check number of pages
    li_pagination = soup.findAll("li", {"class": "paginate-page"})
    if len(li_pagination) == 0:
        ul = soup.find("ul", {"class": "poster-list"})
        if (ul != None):
            movies = ul.find_all("li")
            for movie in movies:
                movies_dict['id'].append(movie.find('div')['data-film-id'])
                movies_dict['title'].append(movie.find('img')['alt'])
                movies_dict['rating'].append(transform_ratings(movie.find('p', {"class": "poster-viewingdata"}).get_text().strip()))
                movies_dict['liked'].append(movie.find('span', {'class': 'like'})!=None)
                movies_dict['link'].append(movie.find('div')['data-target-link'])
    else:
        for i in range(int(li_pagination[-1].find('a').get_text().strip())):
            url = DOMAIN + "/" + username + "/films/page/" + str(i+1)
            url_page = requests.get(url)
            if url_page.status_code != 200:
                raise Exception("")
            soup = BeautifulSoup(url_page.content, 'html.parser')
            ul = soup.find("ul", {"class": "poster-list"})
            if (ul != None):
                movies = ul.find_all("li")
                for movie in movies:
                    movies_dict['id'].append(movie.find('div')['data-film-id'])
                    movies_dict['title'].append(movie.find('img')['alt'])
                    movies_dict['rating'].append(transform_ratings(movie.find('p', {"class": "poster-viewingdata"}).get_text().strip()))
                    movies_dict['liked'].append(movie.find('span', {'class': 'like'})!=None)
                    movies_dict['link'].append(movie.find('div')['data-target-link'])
    
    df_film = pd.DataFrame(movies_dict)    
    df_film['user_id'] = username
    return df_film

def scrape_films_details(df_film):
    df_film = df_film[df_film['rating']!=-1].reset_index(drop=True)
    # df_film = df_film.reset_index(drop=True)
    movies_rating = {}
    movies_rating['id'] = []
    movies_rating['avg_rating'] = []
    movies_rating['year'] = []
    movies_rating['watched_by'] = []
    movies_rating['liked_by'] = []
    movies_rating['runtime'] = []
    movies_rating['image_url'] = []
    
    movies_actor = {}
    movies_actor['id'] = []
    movies_actor['actor'] = []
    movies_actor['actor_link'] = []
    
    movies_director = {}
    movies_director['id'] = []
    movies_director['director'] = []
    movies_director['director_link'] = []
    
    movies_genre = {}
    movies_genre['id'] = []
    movies_genre['genre'] = []

    movies_country = {}
    movies_country['id'] = []
    movies_country['country'] = []

    movies_language = {}
    movies_language['id'] = []
    movies_language['language'] = []

    progress = 0
    bar = st.progress(progress)

    for link in df_film['link']:
        progress += 1
        print('scraping details of '+df_film[df_film['link'] == link]['title'].values[0])
        
        id_movie = df_film[df_film['link'] == link]['id'].values[0]
        url_movie = DOMAIN + link
        url_movie_page = requests.get(url_movie)
        if url_movie_page.status_code != 200:
            raise Exception("")
        soup_movie = BeautifulSoup(url_movie_page.content, 'html.parser')
        for sc in soup_movie.findAll("script"):
            if sc.string != None:
                if "ratingValue" in sc.string:
                    rating = sc.string.split("ratingValue")[1].split(",")[0][2:]
                if "releaseYear" in sc.string:
                    year = sc.string.split("releaseYear")[1].split(",")[0][2:].replace('"','')

        script_w_data = soup_movie.select_one('script[type="application/ld+json"]')
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
        image_url = json_obj['image']
        movies_rating['image_url'].append(image_url)
        
        url_stats = DOMAIN + "/csi" + link + "stats"
        url_stats_page = requests.get(url_stats)
        soup_stats = BeautifulSoup(url_stats_page.content, 'html.parser')
        watched_by = int(soup_stats.findAll('li')[0].find('a')['title'].replace(u'\xa0', u' ').split(" ")[2].replace(u',', u''))
        liked_by = int(soup_stats.findAll('li')[2].find('a')['title'].replace(u'\xa0', u' ').split(" ")[2].replace(u',', u''))
        try:
            runtime = int(soup_movie.find('p',{'class':'text-link text-footer'}).get_text().strip().split('\xa0')[0])
        except:
            runtime = np.nan
        movies_rating['id'].append(id_movie)
        movies_rating['avg_rating'].append(rating)
        movies_rating['year'].append(year)
        movies_rating['watched_by'].append(watched_by)
        movies_rating['liked_by'].append(liked_by)
        movies_rating['runtime'].append(runtime)

        # finding the actors
        if (soup_movie.find('div', {'class':'cast-list'}) != None):
            for actor in soup_movie.find('div', {'class':'cast-list'}).findAll('a'):
                if actor.get_text().strip() != 'Show All…':
                    movies_actor['id'].append(id_movie)
                    movies_actor['actor'].append(actor.get_text().strip())
                    movies_actor['actor_link'].append(actor['href'])

        # finding the directors
        if (soup_movie.find('div', {'id':'tab-crew'}) != None):
            for director in soup_movie.find('div', {'id':'tab-crew'}).find('div').findAll('a'):
                movies_director['id'].append(id_movie)
                movies_director['director'].append(director.get_text().strip())
                movies_director['director_link'].append(director['href'])

        # finding the genres
        if (soup_movie.find('div', {'id':'tab-genres'}) != None):
            for genre in soup_movie.find('div', {'id':'tab-genres'}).find('div').findAll('a'):
                movies_genre['id'].append(id_movie)
                movies_genre['genre'].append(genre.get_text().strip())

        # finding the countries
        details_div = soup_movie.find('div', {'id': 'tab-details'})
        if details_div is not None:
            all_divs = details_div.find_all('div')
            if len(all_divs) > 1:
                second_div = all_divs[1]
                for country in second_div.find_all('a'):
                    movies_country['id'].append(id_movie)
                    movies_country['country'].append(country.get_text().strip())

        # finding the languages
        details_div = soup_movie.find('div', {'id': 'tab-details'})
        if details_div is not None:
            all_divs = details_div.find_all('div')
            if len(all_divs) > 1:
                third_div = all_divs[2]
                for language in third_div.find_all('a'):
                    movies_language['id'].append(id_movie)
                    movies_language['language'].append(language.get_text().strip())

        bar.progress(progress/len(df_film))

    df_rating = pd.DataFrame(movies_rating)
    df_actor = pd.DataFrame(movies_actor)
    df_director = pd.DataFrame(movies_director)
    df_genre = pd.DataFrame(movies_genre)
    df_country = pd.DataFrame(movies_country)
    df_language = pd.DataFrame(movies_language)
    return df_rating, df_actor, df_director, df_genre, df_country, df_language

def get_top_decades(df_film, df_rating):
    df_rating_merged = pd.merge(df_film, df_rating)

    df_rating_merged['year'] = df_rating_merged['year'].astype(int)

    df_rating_merged['decade'] = (df_rating_merged['year'] // 10) * 10

    df_decade = df_rating_merged.groupby('decade').agg({'rating': 'mean', 'id': 'count'}).reset_index()
    df_decade = df_decade.rename(columns={'rating': 'avg_rating', 'id': 'film_count'})

    top_decades = df_decade.sort_values(by='avg_rating', ascending=False).head(3)
    
    return top_decades, df_rating_merged

def get_top_movies_for_decade(df_rating_merged, decade, top_n=20):
    decade_movies = df_rating_merged[df_rating_merged['decade'] == decade]

    decade_movies = decade_movies.sort_values(by=['rating', 'liked'], ascending=[False, False])

    liked_movies = decade_movies[decade_movies['liked']]
    not_liked_movies = decade_movies[~decade_movies['liked']]

    prioritized_movies = pd.concat([liked_movies, not_liked_movies])

    if len(prioritized_movies) > top_n:
        top_movies = prioritized_movies.head(top_n)
    else:
        top_movies = prioritized_movies
    
    return top_movies

def get_rating_differences(df_film, df_rating):
    df_rating_merged = pd.merge(df_film, df_rating, on='id')
    print(df_rating_merged['rating'].dtypes)
    print(df_rating_merged['avg_rating'].dtypes)
    df_rating_merged['rating_diff'] = df_rating_merged['rating'] - df_rating_merged['avg_rating'].astype(float)
    
    higher_rated = df_rating_merged[df_rating_merged['rating_diff'] > 0]
    lower_rated = df_rating_merged[df_rating_merged['rating_diff'] < 0]
    
    higher_rated = higher_rated.sort_values(by='rating_diff', ascending=False).head(12)
    lower_rated = lower_rated.sort_values(by='rating_diff').head(12)
    
    return higher_rated, lower_rated

# def export_data():
    # df_film.to_csv('df_film.csv', index=False)
    # merged_df.to_csv('merged_df.csv', index=False)
    # df_rating.to_csv('df_rating.csv', index=False)
    # df_actor.to_csv('df_actor.csv', index=False)
    # df_director.to_csv('df_director.csv', index=False)
    # df_genre.to_csv('df_genre.csv', index=False)
    # df_length.to_csv('df_length.csv', index=False)

# export_data()