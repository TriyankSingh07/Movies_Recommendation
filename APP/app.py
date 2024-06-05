import pickle
import streamlit as st
import requests
import pandas as pd
from datetime import datetime


# Function to fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    # Proxy settings (optional, if needed to bypass restrictions)
    proxy = {
        'http': 'http://your_proxy_host:your_proxy_port',
        'https': 'https://your_proxy_host:your_proxy_port'
    }

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    try:
        response = requests.get(url, proxies=proxy)  # Add proxies=proxy if needed
        response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
        data = response.json()
        poster_path = data.get('poster_path', '')
        full_poster_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
        rating = data.get('vote_average', 'N/A')
        return full_poster_path, movie_url, rating
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie details: {e}")
        return None, None, 'N/A'


# Function to get movie recommendations
def recommend(movie, num_recommendations=5):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_details = []
    for i in distances[1:num_recommendations + 1]:
        movie_id = movies.iloc[i[0]].movie_id
        poster_path, movie_url, rating = fetch_movie_details(movie_id)
        recommended_movie_details.append((movies.iloc[i[0]].title, poster_path, movie_url, rating))
    return recommended_movie_details


# Function to get the appropriate greeting based on the current time
def get_greeting():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


# Page layout and configuration
st.set_page_config(page_title='Movie Recommender System', layout='wide')

# Custom CSS for styling
st.markdown("""
    <style>
        .header {
            font-size: 3em;
            color: #FF6347;
            text-align: center;
            font-family: 'Courier New', Courier, monospace;
            margin-bottom: 0.5em;
        }
        .subheader {
            text-align: center;
            font-family: 'Courier New', Courier, monospace;
            margin-bottom: 2em;
        }
        .greeting {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 2em;
        }
        .movie-details {
            text-align: center;
        }
        .button {
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 10px;
            border-radius: 5px;
            background-color: #FF6347;
            color: white;
            border: none;
            cursor: pointer;
        }
        .button:hover {
            background-color: #FF4500;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'num_recommendations' not in st.session_state:
    st.session_state.num_recommendations = 5
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ''
if 'recommended_movie_details' not in st.session_state:
    st.session_state.recommended_movie_details = []

# Get username input if not already set
if not st.session_state.username:
    st.session_state.username = st.text_input("Please enter your name:")
    st.button("Submit")
else:
    st.markdown('<div class="header">TasteFlix</div>', unsafe_allow_html=True)
    greeting = get_greeting()
    st.markdown(f'<div class="greeting">{greeting}, {st.session_state.username} :)</div>', unsafe_allow_html=True)

    # Description
    st.markdown(
        '<div class="subheader">Welcome to the Movie Recommender System! Select a movie and get recommendations based on your favorite movies.</div>',
        unsafe_allow_html=True)

    # Load the movies dictionary and convert it to DataFrame
    movies_dict = pickle.load(open('movies_dic.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(open('similarity.pkl', 'rb'))

    movie_list = movies['title'].values

    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list,
        key='movie_select'
    )

    if st.button('Show Recommendation'):
        st.session_state.selected_movie = selected_movie
        st.session_state.num_recommendations = 5
        st.session_state.recommended_movie_details = recommend(st.session_state.selected_movie,
                                                               st.session_state.num_recommendations)

    if st.session_state.recommended_movie_details:
        recommended_movie_details = st.session_state.recommended_movie_details

        st.subheader('Top Recommended Movies')
        cols = st.columns(5)
        for idx, (name, poster, url, rating) in enumerate(recommended_movie_details[:5]):
            col = cols[idx % 5]
            with col:
                if poster:
                    st.image(poster)
                st.write(f"**{name}**")
                st.write(f"Rating: {rating}")
                button_html = f"""
                <a href="{url}" target="_blank">
                    <button class="button">Go Watch</button>
                </a>
                """
                st.markdown(button_html, unsafe_allow_html=True)

        if len(recommended_movie_details) > 5:
            st.subheader('Additional Recommended Movies')
            cols = st.columns(5)
            for idx, (name, poster, url, rating) in enumerate(recommended_movie_details[5:]):
                col = cols[idx % 5]
                with col:
                    if poster:
                        st.image(poster)
                    st.write(f"**{name}**")
                    st.write(f"Rating: {rating}")
                    button_html = f"""
                    <a href="{url}" target="_blank">
                        <button class="button">Go Watch</button>
                    </a>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)

        if st.session_state.num_recommendations < len(similarity[0]):
            if st.button('Show More'):
                st.session_state.num_recommendations += 5
                st.session_state.recommended_movie_details = recommend(st.session_state.selected_movie,
                                                                       st.session_state.num_recommendations)
                recommended_movie_details = st.session_state.recommended_movie_details

                st.subheader('Additional Recommended Movies')
                cols = st.columns(5)
                for idx, (name, poster, url, rating) in enumerate(recommended_movie_details[5:]):
                    col = cols[idx % 5]
                    with col:
                        if poster:
                            st.image(poster)
                        st.write(f"**{name}**")
                        st.write(f"Rating: {rating}")
                        button_html = f"""
                        <a href="{url}" target="_blank">
                            <button class="button">Go Watch</button>
                        </a>
                        """
                        st.markdown(button_html, unsafe_allow_html=True)

    # Additional content
    st.markdown("---")
    st.markdown("""
    ### About this App
    This Movie Recommender System uses a similarity matrix to find the top movies that are most similar to the selected movie. 
    The similarity matrix is precomputed using movie data, and the recommendations are fetched in real-time when you select a movie.

    ### How it Works
    1. **Select a Movie:** Use the dropdown to select a movie you like.
    2. **Show Recommendation:** Click the "Show Recommendation" button to fetch the top recommended movies.
    3. **Show More:** Click the "Show More" button to see more recommendations, up to 20 movies.
    4. **View Recommendations:** The recommended movies will be displayed along with their posters and ratings.

    ### Technologies Used
    - **Python:** The core programming language used to develop this application.
    - **Streamlit:** A fast and easy way to create and share data apps.
    - **Pandas:** For data manipulation and analysis.
    - **Requests:** To fetch movie posters from the TMDB API.
    - **TMDB API:** To get movie details and posters.

    We hope you enjoy using this Movie Recommender System!
    """)

    st.markdown("---")
    st.markdown("Developed by [Your Name](https://github.com/yourprofile)")

    st.text("")
    st.text("")
    st.text("")

if not st.session_state.username:
    st.warning("Please enter your name to continue.")
