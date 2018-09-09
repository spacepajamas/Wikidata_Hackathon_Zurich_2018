from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask import render_template
import matplotlib.pyplot as plt
import sys
from gastrodon import RemoteEndpoint,QName,ttl,URIRef,inline
import pandas as pd
import json
from ast import literal_eval





prefixes=inline("""
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
""").graph

endpoint=RemoteEndpoint(
    "http://query.wikidata.org/sparql"
    ,prefixes=prefixes
)






app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def home():
    my_query = """

    SELECT ?item ?itemLabel ?itemDescription WHERE {
     ?item wdt:P31 wd:Q1172284.
     SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
     ?item wdt:P31 wd:Q192909.
    }
    LIMIT 10
    """

    scandals = endpoint.select(my_query)
    datasetname = list(zip([item.replace('wd:', '').replace(';','') for item in scandals['item']],
             scandals['itemLabel'],scandals['itemDescription']))

    return render_template('home.html', datasetname = datasetname)





def make_c3_data(my_query, labelname):
    panama_people = endpoint.select(my_query)
    panama_people["countbycountry"] = panama_people.groupby(['country_code', 'occupationLabel'])[
        'genderLabel'].transform(
        'count')

    panama_people = endpoint.select(my_query)
    # print(panama_people)
    panama_people["countbycountry"] = panama_people.groupby(['country_code', 'occupationLabel'])[
        'genderLabel'].transform(
        'count')
    panama_people.drop_duplicates(['item'], inplace=True)
    x = panama_people[labelname].value_counts()
    out =  [[k,v] for k,v in x.items()]

    return out


@app.route('/welcome/<Q_ID>/dashboard', methods=['GET'])
def make_dashboard(Q_ID):
    my_query = """SELECT ?item ?itemLabel ?property ?country ?countryLabel ?genderLabel ?occupationLabel ?country_code
   WHERE
   {  ?item ?property wd:"""+Q_ID+""".
   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
   ?item wdt:P31 wd:Q5.
   ?item wdt:P27 ?country.
   ?item wdt:P21 ?gender.
   ?item wdt:P106 ?occupation.
   ?country wdt:P298 ?country_code.
   }
    """
    gender = make_c3_data(my_query, 'genderLabel')
    occupation = make_c3_data(my_query, 'occupationLabel')
    country = make_c3_data(my_query, 'countryLabel')

    return render_template("dashboard.html", gender = gender,
                           occupation = occupation,
                           country= country)







if __name__ == '__main__':

    app.run(debug=True,host='0.0.0.0',port=9000)