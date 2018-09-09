import matplotlib.pyplot as plt
import sys
from gastrodon import RemoteEndpoint,QName,ttl,URIRef,inline
import pandas as pd

prefixes=inline("""
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
""").graph

endpoint=RemoteEndpoint(
    "http://query.wikidata.org/sparql"
    ,prefixes=prefixes
)

Q_ID = 'Q23702848'
my_query = """SELECT ?item ?itemLabel ?property ?country ?countryLabel ?genderLabel ?occupationLabel ?country_code
WHERE
{  ?item ?property wd:""" + Q_ID + """.
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
?item wdt:P31 wd:Q5.
?item wdt:P27 ?country.
?item wdt:P21 ?gender.
?item wdt:P106 ?occupation.
?country wdt:P298 ?country_code.
}
 """


def make_csv_happen(my_query):
    print('begin read')
    panama_people = endpoint.select(my_query)
    #print(panama_people)
    print(panama_people.head())
    #panama_people.to_csv('templates/test_country.csv')
    panama_people["countbycountry"] = panama_people.groupby(['country_code', 'occupationLabel'])['genderLabel'].transform(
        'count')

    panama_people = endpoint.select(my_query)
    #print(panama_people)
    panama_people["countbycountry"] = panama_people.groupby(['country_code', 'occupationLabel'])['genderLabel'].transform(
        'count')
    panama_people.drop_duplicates(['country_code'], inplace=True)
    x = panama_people

    test_df = panama_people[['country_code', 'countryLabel', 'countryLabel', 'countbycountry']]
    test_df = test_df.drop_duplicates(['country_code'])
    test_df.index.name = 'OBJECTID'
    test_df.columns = ['ISO_3DIGIT', 'NAME', 'LONG_NAME', 'Species']
    test_df.to_csv('test_country.csv')


make_csv_happen(my_query)