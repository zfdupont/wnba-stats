from flask import Flask, request as req
from flask_cors import CORS, cross_origin
import pandas as pd
import logging

logging.getLogger('flask_cors').level = logging.DEBUG

app = Flask(__name__)
'''
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.config['CORS_ALWAYS_SEND'] = True
app.config['CORS_SEND_WILDCARD'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = False



# app.config['CORS_HEADERS'] = 'Content-Type'
'''
@app.before_request
def before_request():
    headers = {'Access-Control-Allow-Origin': 'https://www.zfdupont.com',
               'Access-Control-Allow-Credentials': True,
               'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
               'Access-Control-Allow-Headers': 'Content-Type'}
    if req.method.lower() == 'options':
        return jsonify(headers), 200


# @cross_origin(['https://www.zfdupont.com', 'http://127.0.0.1:3000'])dd
@app.route('/api/players')
def list_players():
    df = pd.read_csv('../wnbabpm.csv', index_col=0).sort_values(req.args.get('sort'), ascending=req.args.get('order') == 'ASC').rename(columns={ 'Off. Role': 'offRole', 'Pos': 'position'}).round(3)
    df.columns = map(str.lower, df.columns)
    return df.to_dict(orient='records')
