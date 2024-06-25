import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import numpy as np

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
        if (soup_movie.find('div', {'class': 'text-sluglist'}) is not None):
            country_div = soup_movie.find('div', {'class': 'text-sluglist'})
            country_tags = country_div.find_all('a', {'class': 'text-slug'})

            for country_tag in country_tags:
                country_name = country_tag.get_text().strip()
                movies_country['id'].append(id_movie)
                movies_country['country'].append(country_name)

        bar.progress(progress/len(df_film))

    df_rating = pd.DataFrame(movies_rating)
    df_actor = pd.DataFrame(movies_actor)
    df_director = pd.DataFrame(movies_director)
    df_genre = pd.DataFrame(movies_genre)
    # df_length = pd.DataFrame(movies_length)
    df_country = pd.DataFrame(movies_country)
    return df_rating, df_actor, df_director, df_genre, df_country

def get_total_films(df):
    return df['film_length'].count()
# in hours
def get_total_watched_time(df):
    return round(df['film_length'].sum() / 60) # convert to hours rounded

def get_total_directors(df):
    return df['director'].nunique()

def get_total_countries(df):
    return df['country'].nunique()

# data
# df_film = scrape_films('ther0')
# df_rating, df_actor, df_director, df_genre, df_length, df_country = scrape_films_details(df_film)
# merged_df = pd.merge(df_film, df_rating)


# print(df_length.head(20))
# print(get_total_films(df_length))
# print(get_total_watched_time(df_length))
# print(get_total_directors(df_director))
# print(get_total_countries(df_country))
# print(merged_df.head(10))


# def export_data():
    # df_film.to_csv('df_film.csv', index=False)
    # merged_df.to_csv('merged_df.csv', index=False)
    # df_rating.to_csv('df_rating.csv', index=False)
    # df_actor.to_csv('df_actor.csv', index=False)
    # df_director.to_csv('df_director.csv', index=False)
    # df_genre.to_csv('df_genre.csv', index=False)
    # df_length.to_csv('df_length.csv', index=False)

# export_data()


