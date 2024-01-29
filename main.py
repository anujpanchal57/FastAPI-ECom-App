from fastapi import FastAPI
from pymongo import MongoClient
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from pprint import pprint

mongo = MongoClient("mongodb://127.0.0.1:27017/cc-ecommerce-db")['cc-ecommerce-db']

# Create an instance of FastAPI
app = FastAPI()

class Item(BaseModel):
    productId: str
    boughtQuantity: int

class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str

class Order(BaseModel):
    createdOn: datetime = Field(default_factory=datetime.now)
    total_amount: int
    user_address: UserAddress
    items: List[Item]

class CreateOrder(BaseModel):
    items: List[Item]
    total_amount: float
    user_address: UserAddress

# GET products API as per query params passed
@app.get("/products")
def get_products(offset: int, limit: int, min_price: Optional[int] = None, max_price: Optional[int] = None):
    agg_pipeline = [{
        "$facet": {
            "page": [
                {
                    "$count": "totalResults",
                },
                {
                    "$project": {
                        "nextOffset": {
                            "$cond": [
                                {"$gte": [{"$add": [offset, limit]}, "$totalResults"]},
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
            ],
            "data": []
        }
    }]
    if min_price and max_price:
        agg_pipeline[0]['$facet']['data'].append({"$match": {
            "$and": [
                {"price": {"$gte": min_price}},
                {"price": {"$lte": max_price}}
            ]
        }})
    elif min_price:
        agg_pipeline[0]['$facet']['data'].append({"$match": {"price": {"$gte": min_price}}})
    elif max_price:
        agg_pipeline[0]['$facet']['data'].append({"$match": {"price": {"$lte": max_price}}})
    else:
        agg_pipeline[0]['$facet']['data'].append({"$skip": offset})
        agg_pipeline[0]['$facet']['data'].append({"$limit": limit})

    result = list(mongo['products'].aggregate(agg_pipeline))

    return {"result": result}

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