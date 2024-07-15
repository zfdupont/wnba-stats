from flask import Flask
from flask_cors import CORS, cross_origin
import pandas as pd

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/players')
@cross_origin('http:localhost:3000')
def hello_world():
    df = pd.read_csv('../wnbabpm.csv', index_col=0).rename({ 'Off. Role': 'offRole'})
    # print(df)
    return df.to_dict(orient='records')