import requests
import urllib.request
import json
import time
import re
import pymongo
import datetime
import bson
import pprint
from ast import literal_eval
import copy
import pandas as pd
from requests.exceptions import ConnectionError
from collections import defaultdict
import pymongo
# from .mongoflask import MongoJSONEncoder, ObjectIdConverter
from bson import ObjectId,json_util
from pymongo import MongoClient
from flask import Flask,request,jsonify
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from flask_pymongo import PyMongo

# def get_type(input_data):
#     try:
#         return type(literal_eval(input_data))
#     except (ValueError, SyntaxError):
#         # A string, so return str
#         return str

#######################################  API   ######################################################
app = Flask(__name__)
api = Api(app,
          default="Indicator",  # Default namespace
          title="World Bank Economic Indicators",  # Documentation Title
          description="This is just a API that allow customer to read and store some publicly available economic indicator data for countries around the world, and to access the data.")  # Documentation Description
# app.json_encoder = MongoJSONEncoder
# app.url_map.converters['objectid'] = ObjectIdConverter

indicator_model = api.model('Indicator', {
    'indicator_id': fields.String
})

# parser = reqparse.RequestParser()
# parser.add_argument('order', choices=list(column for column in indicator_model.keys()))
# parser.add_argument('ascending', type=inputs.boolean)

app.config["MONGO_DBNAME"] = "my-database"
app.config["MONGO_URI"] = "mongodb://Conlin:Tcgabcd123@ds111492.mlab.com:11492/my-database"

mongo = PyMongo(app)

# def get_data(indicator_id):
#     # url = 'http://api.worldbank.org/v2/countries/all/indicators/%s?date=2012:2017&format=json&page=1'
#     data_list = []
#     for i in range(1,3):
#         url = ("http://api.worldbank.org/v2/countries/all/indicators/%s?date=2012:2017&format=json&page=%d" %(indicator_id,i))
#         print(url)
#         json_val = requests.get(url).json()
#         for line in json_val[1]:
#             data_list.append(line)
#
#
#     sorted_data_list = []
#     for line in data_list:
#         sub = {'country': line['country']['value'],
#                'date': line['date'],
#                'value': line['value']}
#         sorted_data_list.append(sub)
#     return sorted_data_list


@api.route('/wb_ec_indicators')
class All_Class(Resource):
    # @api.expect(parser, validate=True)
    @api.response(200, 'OK')
    @api.doc(description="This operation retrieves all available collections.")
    def get(self):
        api_data = mongo.db.wb_ec_indicators

        output = []

        for q in api_data.find():
            output.append({'location': '/wb_ec_indicators/' + str(q['_id']),
                           'collection_id': str(q['_id']),
                           'creation_time': q['creation_time'],
                           'indicator': q['indicator']})

        return output, 200

    @api.expect(indicator_model)
    @api.response(200, 'OK')
    @api.response(201, 'Created')
    @api.response(400, 'Error')
    @api.doc(description="Add a new indicator data")
    def post(self):

        flg_1 = 0

        indicator = request.json

        indicator_id = indicator['indicator_id']

        data_list = []
        for i in range(1, 3):
            url = ("http://api.worldbank.org/v2/countries/all/indicators/%s?date=2012:2017&format=json&page=%d" % (
            indicator_id, i))
            # print(url)
            json_val = requests.get(url).json()
            try:
                for line in json_val[1]:
                    data_list.append(line)
            except IndexError:
                return "",400

        sorted_data_list = []
        for line in data_list:
            sub = {'country': line['country']['value'],
                   'date': line['date'],
                   'value': line['value']}
            sorted_data_list.append(sub)

        api_data = mongo.db.wb_ec_indicators
        for q in api_data.find():
            if indicator_id == q['indicator']:
                flg_1 = 1

        #######################################  get data from json   ######################################################

        json_sorted_data = {'indicator': indicator_id,
                            'indicator_value': 'GDP (current US$)',
                            'creation_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time())),
                            'entries': sorted_data_list}
        #######################################  input data to mongodb   ######################################################
        collection = db.wb_ec_indicators
        collection.insert_one(json_sorted_data)

        # id = json_sorted_data['indicator']

        # client.close()
        api_data = mongo.db.wb_ec_indicators
        q_1 = api_data.find_one({'indicator': indicator_id})
        q = json.loads(json_util.dumps(q_1))
        output = ({'location': '/wb_ec_indicators/' + str(q['_id']),
                   'collection_id': str(q['_id']),
                   'creation_time': q['creation_time'],
                   'indicator': q['indicator']})
        if flg_1 == 1:
            return output, 200
        elif flg_1 == 0:
            return output, 201

@api.route('/wb_ec_indicators/<string:id>')
@api.param('id', 'The collection ID')
class ID_Class(Resource):
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Get a collection by its ID")
    def get(self, id):
        # print(id)
        flg = 0
        api_data = mongo.db.wb_ec_indicators
        for q in api_data.find():
            # print(q)
            # print(id == str(q['_id']))
            if id == str(q['_id']):
                # print(q['_id'])
                # print('1111111')
                flg = 1
        print(flg)
        if flg:
            # print(api_data.find_one())
            q = api_data.find_one({'_id': ObjectId(id)})
            # print('qqqqqqq',q)
            output = ({'collection_id': str(q['_id']),
                       'indicator': q['indicator'],
                       'indicator_value': q['indicator_value'],
                       'creation_time': q['creation_time'],
                       'entries': q['entries']})
            # print(output)
            return output, 200
        else:
            return "", 400

    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Deletes an existing collection by collection ID")
    def delete(self, id):
        flg = 0

        api_data = mongo.db.wb_ec_indicators
        for q in api_data.find():
            if id == str(q['_id']):
                flg = 1
        # q = api_data.find_one({'indicator': id})
        if flg:
            try:
                mongo.db.wb_ec_indicators.remove({'_id': ObjectId(id)})
            except bson.errors.InvalidId:
                return "", 400
            output = {"message" :"Collection = %s is removed from the database!" % (id)}
            return output, 200
        else:
            return "", 400

@api.route('/wb_ec_indicators/<string:id>/<string:country>/<string:year>')
@api.param('id', 'The collection ID')
@api.param('country', 'given country')
@api.param('year', 'given year')
class Country_Year_Class(Resource):
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Retrieve economic indicator value for given country and a year")
    def get(self, id, country, year):
        api_data = mongo.db.wb_ec_indicators

        try:
            q = api_data.find_one({'_id': ObjectId(id)})
        except bson.errors.InvalidId:
            return "",400
        entry_list = q['entries']
        # print(q)
        # print(entry_list)
        # print(country, year)
        data_value = 0
        for l in entry_list:
            # print(l['country'],l['date'])
            if l['country'] == country and l['date'] == year:
                data_value = l['value']
        # print(country, year, data_value)
        if data_value:
            output = ({'collection_id': str(q['_id']),
                       'indicator': q['indicator'],
                       'country': country,
                       'year': year,
                       'value': data_value})
            return output, 200
        else:
            return '', 400
        # else:
        #     return "", 400

parser = reqparse.RequestParser()
parser.add_argument('query', required=True,
help="top or bottom + page numbers, e.g top10, bottom10")

@api.route('/wb_ec_indicators/<string:id>/<int:year>')
@api.param('id', 'The collection ID')
@api.param('year', 'given year')
# @api.param('query', 'top or bottom + num, e.g top10, bottom10')
class Country_Year_Class(Resource):
    @api.expect(parser, validate=True)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Retrieve top/bottom economic indicator values for a given year")
    def get(self, id, year):
        # print("id: ",id,"year: ",year,"query: ",query)
        # print(111)
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        args = parser.parse_args()

        query = args.get('query', True)

        api_data = mongo.db.wb_ec_indicators
        try:
            q = api_data.find_one({'_id': ObjectId(id)})
        except bson.errors.InvalidId:
            return "",400
        # print(q)
        entry_list = q['entries']
        # print(entry_list)
        sorted_data = []
        for line in entry_list:
            if line['date'] == str(year) and line['value']:
                sorted_data.append(line)
        ordered_data = sorted(sorted_data, key=lambda k: k['value'])
        ordered_data.reverse()
        print(ordered_data)
        Num = int(re.search(r'\d+', query).group())
        query_order = query.replace(str(Num),'')
        output = []
        if query_order == 'top':
            for i in range(0,Num):
                try:
                    output.append(ordered_data[i])
                except IndexError:
                    return "",400

        elif query_order == 'bottom':
            for i in range(-Num-1,-1):
                output.append(ordered_data[i])
        if output == []:
            return "",400
        else:
            return {"indicator":q['indicator'],
                    "indicator_value":"GDP (current US$)",
                    "entries":output}, 200

if __name__ == '__main__':
    #######################################  mongodb   ######################################################
    mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % ('Conlin', 'Tcgabcd123', 'ds111492.mlab.com', '11492', 'my-database')
    client = MongoClient(mongo_uri)
    db = client['my-database']

    app.run(debug=True)
