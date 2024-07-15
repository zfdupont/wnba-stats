from flask import Flask
import pandas as pd

app = Flask(__name__)

@app.route('/')
def hello_world():
    df = pd.read_csv('../wnbabpm.csv', index_col=0)
    # print(df)
    return df.to_dict(orient='records')