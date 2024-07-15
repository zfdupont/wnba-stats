from flask import Flask, request as req
from flask_cors import CORS, cross_origin
import pandas as pd
import logging

logging.getLogger('flask_cors').level = logging.DEBUG

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_ALWAYS_SEND'] = True
app.config['CORS_SEND_WILDCARD'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = False



# app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/players')
def list_players():
    df = pd.read_csv('../wnbabpm.csv', index_col=0).sort_values(req.args.get('sort'), ascending=req.args.get('order') == 'ASC').rename(columns={ 'Off. Role': 'offRole', 'Pos': 'position'}).round(3)
    df.columns = map(str.lower, df.columns)
    return df.to_dict(orient='records')