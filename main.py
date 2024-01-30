from fastapi import FastAPI
from pymongo import MongoClient
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from pprint import pprint
import json
from bson import json_util

# Created a Mongo instance to work with database
mongo = MongoClient("mongodb://127.0.0.1:27017/cc-ecommerce-db")['cc-ecommerce-db']

# Create an instance of FastAPI
app = FastAPI()

# Item Base Model (For the products bought by the user)
class Item(BaseModel):
    productId: str
    boughtQuantity: int

# User Address Base Model (For the information on user address)
class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str

# Order Base Model (Structure in which order will be saved in the DB)
class Order(BaseModel):
    createdOn: datetime = Field(default_factory=datetime.now)
    total_amount: int
    user_address: UserAddress
    items: List[Item]

# Base Model for request payload of the create order API
class CreateOrder(BaseModel):
    items: List[Item]
    total_amount: float
    user_address: UserAddress

# GET products API as per query params passed
@app.get("/products")
def get_products(offset: int, limit: int, min_price: Optional[int] = None, max_price: Optional[int] = None):
    agg_pipeline = []

    # Applying filters on the provided min and max price in the query param
    if min_price and max_price:
        agg_pipeline.append({
            "$match": {
                "$and": [
                    {"price": {"$gte": min_price}},
                    {"price": {"$lte": max_price}}
                ]
            }
        })
    elif min_price:
        agg_pipeline.append({
            "$match": {"price": {"$gte": min_price}}
        })
    elif  max_price:
        agg_pipeline.append({
            "$match": {"price": {"$lte": max_price}}
        })

    # BONUS: PAGINATION LOGIC APPLIED USING $FACET
    agg_pipeline.append({
        "$facet": {
            "data": [
                {"$skip": offset},
                {"$limit": limit}
            ],
            "page": [
                {"$skip": offset},
                {"$limit": limit},
                {
                    "$count": "count"
                },
                {
                    "$project": {
                        "total": "$count",
                        "nextOffset": {
                            "$cond": [
                                {"$lt": ["$count", limit]},
                                None,
                                {"$add": [offset, limit]}
                            ]
                        },
                        "prevOffset": {
                            "$cond": [
                                {"$lte": [offset, 0]},
                                None,
                                {"$subtract": [offset, limit]}
                            ]
                        }
                    }
                }
            ]
        }
    })

    result = list(mongo['products'].aggregate(agg_pipeline))

    result[0]['page'][0]['limit'] = limit

    return json.loads(json_util.dumps(result))

# API to create an order
@app.post("/orders", response_model=Order)
def create_order(order_data: CreateOrder):
    # Convert ObjectId to str (because of pydantic version compatibility)
    for item in order_data.items:
        item.productId = str(item.productId)

    # Create the order object
    order_obj = Order(
        items=order_data.items,
        total_amount=order_data.total_amount,
        user_address=order_data.user_address
    )

    # Inserting the order in the orders collection
    mongo['orders'].insert_one(order_obj.dict())

    return order_obj