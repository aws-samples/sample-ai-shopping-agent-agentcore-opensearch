# OpenSearch Dashboards Dev Tools Commands

Run these commands in **OpenSearch Dashboards > Dev Tools** console.

Replace `<deployed model id>`, `<connector id>`, `<model group id>`, and
`<registered-model-id>` with actual values from previous steps.

---

## Create Model Group

```
POST /_plugins/_ml/model_groups/_register
{
  "name": "agent-conversational-search-model-group",
  "description": "A model group for bedrock Nova embedding models used for conversational search"
}
```

Note the `model_group_id` from the response.

## Register Model

Use the `connector_id` from `create_connector.py` and the `model_group_id` from above:

```
POST /_plugins/_ml/models/_register
{
  "name": "nova-2-multimodal-embedding-v1",
  "function_name": "remote",
  "model_group_id": "<model group id>",
  "description": "Nova 2 Multimodal Embeddings Model",
  "connector_id": "<connector id>",
  "interface": {}
}
```

Note the `model_id` (registered model ID) from the response.

## Deploy Model

```
POST /_plugins/_ml/models/<registered-model-id>/_deploy
```

---

## Create Ingest Pipeline

```
PUT /_ingest/pipeline/nova_multimodal_embedding
{
  "description": "Text embedding pipeline using nova_multimodal_embedding",
  "processors": [
    {
      "text_embedding": {
        "model_id": "<deployed model id>",
        "field_map": {
          "title": "title_vector"
        }
      }
    }
  ]
}
```

---

## Create Index

```
PUT /product
{
  "settings": {
    "index": {
      "default_pipeline": "nova_multimodal_embedding",
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "title_vector": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "lucene"
        }
      },
      "price": {
        "type": "float"
      },
      "description": {
        "type": "text"
      },
      "category": {
        "type": "keyword"
      },
      "image_url": {
        "type": "text"
      },
      "rating": {
        "properties": {
          "rate": {
            "type": "float"
          },
          "count": {
            "type": "integer"
          }
        }
      }
    }
  }
}
```

---

## Ingest Sample Data

```
POST /_bulk
{"index": {"_index": "product", "_id": "1"}}
{"id":1,"title":"Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops","price":109.95,"description":"Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday","category":"men's clothing","image":"https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png","rating":{"rate":3.9,"count":120}}
{"index": {"_index": "product", "_id": "2"}}
{"id":2,"title":"Mens Casual Premium Slim Fit T-Shirts","price":22.3,"description":"Slim-fitting style, contrast raglan long sleeve, three-button henley placket, light weight & soft fabric for breathable and comfortable wearing. And Solid stitched shirts with round neck made for durability and a great fit for casual fashion wear and diehard baseball fans. The Henley style round neckline includes a three-button placket.","category":"men's clothing","image":"https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_t.png","rating":{"rate":4.1,"count":259}}
{"index": {"_index": "product", "_id": "3"}}
{"id":3,"title":"Mens Cotton Jacket","price":55.99,"description":"great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions, such as working, hiking, camping, mountain/rock climbing, cycling, traveling or other outdoors. Good gift choice for you or your family member. A warm hearted love to Father, husband or son in this thanksgiving or Christmas Day.","category":"men's clothing","image":"https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_t.png","rating":{"rate":4.7,"count":500}}
{"index": {"_index": "product", "_id": "4"}}
{"id":4,"title":"Mens Casual Slim Fit","price":15.99,"description":"The color could be slightly different between on the screen and in practice. / Please note that body builds vary by person, therefore, detailed size information should be reviewed below on the product description.","category":"men's clothing","image":"https://fakestoreapi.com/img/71YXzeOuslL._AC_UY879_t.png","rating":{"rate":2.1,"count":430}}
{"index": {"_index": "product", "_id": "5"}}
{"id":5,"title":"John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet","price":695,"description":"From our Legends Collection, the Naga was inspired by the mythical water dragon that protects the ocean's pearl. Wear facing inward to be bestowed with love and abundance, or outward for protection.","category":"jewelery","image":"https://fakestoreapi.com/img/71pWzhdJNwL._AC_UL640_QL65_ML3_t.png","rating":{"rate":4.6,"count":400}}
```

---

## Query the Index (Test)

```
GET /product/_search
{
  "_source": false,
  "fields": [
    "title",
    "price",
    "category",
    "image"
  ],
  "size": 3,
  "query": {
    "neural": {
      "title_vector": {
        "query_text": "jacket",
        "model_id": "<deployed model id>",
        "k": 5
      }
    }
  }
}
```
