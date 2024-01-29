
![ALTERNATE-TEXT](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue
)
![](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

# FastAPI E-Commerce App

Super fast E-Commerce App developed using [FastAPI](https://fastapi.tiangolo.com/) where you can find tonnes of products.


## Installation

**Step 1:** Clone or download the project in your PC.

**Step 2:** Run the below mentioned command to install all the required libraries and packages in your PC using [pip](https://pypi.org/project/pip/)

```bash
  pip install -r requirements.txt
```
Try uing **pip3** if pip doesn't work in your PC.

**Step 3:** Execute the following command to run the project on your PC

```bash
  uvicorn main:app --reload
```
After executing the above command, project will be served on your local machine on port 8000



## API Reference

#### 1) GET products

```http
  GET /products?offset=0&limit=5&min_price=1000&max_price=5000
```

Query Params:
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `offset` | `string` | **Required**. Skip the number of records for a single page |
| `limit` | `string` | **Required**. Limit the number of records for a single page |
| `min_price` | `string` | **Optional**. Filter products that have prices greater than or equal to the value of `min_price` |
| `max_price` | `string` | **Optional**. Filter products that have prices lesser than or equal to the value of `max_price` |

cURL of the request:
```
curl --location '127.0.0.1:8000/products?offset=0&limit=10&min_price=1000&max_price=10000' \
--header 'Cookie: csrftoken=EprbYHEFXXH3AU6boqdJV61Sp1soXwPv'
```

#### 2) Create order

```http
  POST /orders
```

cURL of the request:
```
curl --location '127.0.0.1:8000/orders' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=EprbYHEFXXH3AU6boqdJV61Sp1soXwPv' \
--data '{
    "total_amount": 2000,
    "user_address": {
        "city": "Thane",
        "country": "India",
        "zip_code": "400610"
    },
    "items": [
        {
            "productId": "65b61836f578c08709bc8c34",
            "boughtQuantity": 2
        }
    ]
}'
```
*Alternatively, you can refer to the docs created by FastAPI on the following URL: [127.0.0.1:8000/docs](127.0.0.1:8000/docs)*



