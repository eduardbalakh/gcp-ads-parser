from fastapi import FastAPI
from dataclasses import dataclass, asdict
import requests
import json
import uuid
import logging

logging.basicConfig(datefmt='[%Y-%m-%d %H:%M:%S]', format='%(asctime)s %(message)s')

with open('config.json', 'r') as f:
    params = json.load(f)

app = FastAPI()


@dataclass
class Flat():
    sourceId: str
    description: str
    city: str
    region: str
    roomNumber: float
    square: float
    floor: int
    isFurnished: bool
    linkToAds: str
    source: str


@app.get("/")
async def root():
    return {"message": "To get test flat visti /new_flat"}


@app.post("/newflat")
async def post_test_flat():
    params['description']['sourceId'] = str(uuid.uuid1())
    flat = Flat(**params['description'])
    try:
        requests.post(params['url'], json=asdict(flat))
    except requests.exceptions.InvalidSchema as e:
        logging.error(e)
        return {"message": "Invalid URL", "error": str(e)}
    logging.info(f"Flat {flat.sourceId} was sent to {params['url']}")
    return "Ok! Flat was added to database. Flat id is: " + flat.sourceId
