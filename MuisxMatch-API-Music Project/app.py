from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField, validators
import requests
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16).hex()

""" ----------- I - JSON DOCUMENTS ----------- """


def save_to_file(data, filename):
    with open(filename, 'w') as write_file:
        json.dump(data, write_file, indent=2)


def read_from_file(filename):
    with open(filename, 'r') as read_file:
        data = json.load(read_file)
    return data


""" ----------- 2 - API KEY ----------- """
api_key = read_from_file('api_key.json')['key']


""" ----------- 3 - USEFUL LISTS ----------- """
countries = read_from_file('countries.json')


countries_list = list(countries.keys())

charts = [("top", "Editorial Chart"),
          ("hot", "Most viewed lyrics in the last 2 hours"),
          ("mxmweekly", "Most viewed lyrics in the last 7 days"),
          ("mxmweekly_new", "Most viewed lyrics in the last 7 days limited to new releases only")]

number_of_results = [5, 10, 15, 20]

""" ----------- FORMS ----------- """




class SearchForm(FlaskForm):
    country = SelectField('Country', choices=countries_list)
    chartType = SelectField('Chart Type', choices=charts)
    numberResults = IntegerField('Number of Results', validators=[validators.NumberRange(min=1, max=10)])
    # submit = SubmitField('Search')


""" ----------- API CALLS ----------- """



def request_top_artists(country_code, page_size):
    top_artists_url = "https://api.musixmatch.com/ws/1.1/chart.artists.get?country={0}&page_size={1}&apikey={2}" \
        .format(country_code, page_size, api_key)

    response = requests.get(top_artists_url)
    response.raise_for_status()

    data = response.json()

    save_to_file(data, 'top_artists.json')

    return data



def request_top_tracks(country_code, chart_name, page_size):
    top_tracks_url = "https://api.musixmatch.com/ws/1.1/chart.tracks.get?country={0}&chart_name={1}&page_size={2}&apikey={3}" \
        .format(country_code, chart_name, page_size, api_key)

    response = requests.get(top_tracks_url)
    response.raise_for_status()

    data = response.json()

    save_to_file(data, 'top_tracks.json')

    return data


""" ----------- ROUTES ----------- """



@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()

    if request.method == "POST":
        country = form.country.data
        chart = form.chartType.data
        number = form.numberResults.data

        """ TOP ARTISTS PER COUNTRY """
        top_artists = request_top_artists(countries[country], number)
        list_of_artists = []
        for artist in top_artists['message']['body']['artist_list']:
            list_of_artists.append(artist['artist']['artist_name'])

        """ TOP TRACKS PER COUNTRY AND CHART"""
        top_tracks = request_top_tracks(countries[country], chart, number)
        list_of_tracks = []
        for track in top_tracks['message']['body']['track_list']:
            list_of_tracks.append(
                (track['track']['track_name'], track['track']['artist_name'], track['track']['track_share_url']))

        return render_template(
            'results.html',
            list_of_artists=list_of_artists,
            list_of_tracks=list_of_tracks,
            country=country,
            quantity=number
        )

    return render_template('index.html', form=form)




if __name__ == '__main__':
    app.run(
        port=5050,
        debug=True
    )