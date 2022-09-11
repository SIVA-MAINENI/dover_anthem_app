import json
from datetime import datetime, date
import random as rnd
import certifi
import pymongo
import os
from flask import Flask, jsonify, request, send_from_directory
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
#from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes

app = Flask(__name__, static_folder='./build', static_url_path='/')

@app.route('/')
def serve():
    #return send_from_directory(app.static_folder, 'index.html')
    return app.send_static_file('index.html')

@app.route('/monitor')
def monitor():  # put application's code here
    return jsonify(status="success")

def return_image_attr(img_url1, img_url2):
    """
    returns brand of the car in the image and
    whether there are kids in the photo or not
    """
    
    credential = json.load(open('api_key.json'))
    api_key = credential['API_KEY']
    endpoint = credential['END_POINT']
    cv_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(api_key))
    kids = False
    brand = None
    try:
        result = cv_client.analyze_image(img_url1,
                                         visual_features=['brands', 'faces', 'categories', 'adult', 'description'])
        if set(['child', 'young', 'baby']).intersection(set(result.description.tags)):
            kids = True
        if len(result.brands) >0:
            brand = result.brands[0].name
    except Exception as e:
        type(e)

    try:
        result = cv_client.analyze_image(img_url2,
                                         visual_features=['brands', 'faces', 'categories', 'adult', 'description'])
        if set(['child', 'young', 'baby']).intersection(set(result.description.tags)):
            kids = True
        if len(result.brands) >0:
            brand = result.brands[0].name
    except Exception as e:
        type(e)
        
    return kids, brand


@app.route('/personalize_ads', methods=["POST"])
def updateActivity():
    ca = certifi.where()
    connectionString = "mongodb://doverhackathon2022-database:uYtbE1mzGJYZPXBJgEsXuU7Fi2N9jEJ26KF4H5oW2GTKKJyWivpPYABwenEeMQcr3jrRMQe2Z2FKXjizcPjZsA==@doverhackathon2022-database.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@doverhackathon2022-database@"
    client  = pymongo.MongoClient(connectionString)
    db = client.get_database('RewardSystem')
    activityByUser = db.get_collection('ActivityByUser')
    ad_db = client.get_database('AdSystem')
    product_collect = ad_db.get_collection('ProfileMappings')
    cars_collect = ad_db.get_collection('VehicleMap')
    send = request.json
    updateDate = str(datetime.now())
    active_user = activityByUser.find_one({"token": send["token"], "storeID": send["storeID"]})

    if active_user is None:
        rewardPoints = (send["gallonCount"] / 10) * 5
        if rewardPoints < 1:
            rewardPoints = 0
        activityByUser.insert_one({"token": send["token"], "storeID": send["storeID"],
                                   "gallonCount": send["gallonCount"], "updateDate": str(datetime.now()),
                                   "Rewards": rewardPoints})
        active_user = activityByUser.find_one({"token": send["token"], "storeID": send["storeID"]})

    else:
        if (datetime.now() - datetime.strptime(active_user['updateDate'], "%Y-%m-%d %H:%M:%S.%f")).days <= 30:
            rewardPoints = (send['gallonCount'] / 10) * 5 + active_user['Rewards']
        else:
            rewardPoints = (send['gallonCount'] / 10) * 5

            #  Update the User account with rewards
        activityByUser.update_one({"token": send["token"], "storeID": send["storeID"]},
                                  {
                                      '$set': {'Rewards': rewardPoints,
                                               'updateDate': str(datetime.now())}
                                  })
    kids, brand = return_image_attr(send['img_url1'], send['img_url2'])
    x = rnd.randint(0, 1)
    if x:
        weather = True
    else:
        weather = False
    products = product_collect.find({'kids': kids, 'weather': weather,
                                     'QuantityAvailable': {'$gte': 0},
                                     'Rewards': {'$lte': rewardPoints}})
    

    # print(products)
    product_url = []
    product_rewards = []
    for document in products:
        product_url.append(document['Producturl'])
        product_rewards.append(document['Rewards'])
    print(len(product_url))
    x = rnd.randint(0, int(len(product_url)/2) )
    y = rnd.randint(int(len(product_url)/2) + 1 , len(product_url) -1 )
    print(x, y)
    product_url_f = [product_url[x]] + [product_url[y]] 
    product_rewards_f = [product_rewards[x]] + [product_rewards[y]]
    cars_ad = cars_collect.find_one({'car_brand': brand.capitalize()})['image']

    return (jsonify(token=active_user["token"], storeID=active_user["storeID"],
                    rewardPoints=rewardPoints, cars_ad=cars_ad, product_url=product_url_f, product_rewards=product_rewards_f))


@app.route('/weather')
def weather():
    return jsonify(status=rnd.randint(0, 1))

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=80)
    
