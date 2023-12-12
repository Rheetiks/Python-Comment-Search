from flask import Flask, jsonify, request
from datetime import datetime
from bson import json_util
import json
import requests

app=Flask(__name__)


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://root:root@cluster0.p3yfxed.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))


db = client.get_database("Cluster0")
collection = db.Comments 

@app.route("/delete/all")
def deleteAll():
    collection.delete_many({})
    return "success"


@app.route('/get/comments')
def getComments():
    doc=collection.find()
    json_data = json.dumps(list(doc), default=json_util.default)
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/add/all")
def addComments():
    response = requests.get("https://app.ylytic.com/ylytic/test")
    for comment in response.json()['comments']:
        comment['at'] = datetime.strptime(comment['at'], "%a, %d %b %Y %H:%M:%S %Z")
        collection.insert_one(comment)
    return "success"

@app.route('/search', methods=['GET'])
def search_comments():
    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    # Construct the query based on provided parameters
    query = {}
    if search_author:
        query['author'] = {'$regex': f'.*{search_author}.*', '$options': 'i'}
    if at_from and at_to:
        at_from_date = datetime.strptime(at_from, "%d-%m-%Y")
        at_to_date = datetime.strptime(at_to, "%d-%m-%Y")
        
        
        query['at'] = {'$gte': at_from_date, '$lte': at_to_date}    
    if like_from and like_to:
        query['like'] = {'$gte': int(like_from), '$lte': int(like_to)}
    if reply_from and reply_to:
        query['reply'] = {'$gte': int(reply_from), '$lte': int(reply_to)}
    if search_text:
        query['text'] = {'$regex': f'.*{search_text}.*', '$options': 'i'}

    result = collection.find(query)

    json_data = json.dumps(list(result), default=json_util.default)
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    return response
    

if __name__ == "__main__":
    app.run(debug=True)