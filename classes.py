from dataclasses import dataclass
from requests_html import AsyncHTMLSession, HTMLSession, Element

from typing import List, Union

CE_CLASSES = {('tw-flex', 'tw-flex-col', 'property-card__price-value'): "price",
              ('tw-text-xs', 'text--semibold', 'tw-flex', 'tw-items-start', 'tw-flex-wrap'): "type",
              ('property-card__place',): "location",
              ('property-card__feature', 'ng-star-inserted'): "furnished",
              ('property-card__feature',): "props",
              ('property-card__header-info',): "id"}

ROOM_NUM = {"Jednosoban": 1.0,
            "Jednoiposoban": 1.5,
            "Dvosoban": 2.0,
            "Dvoiposoban": 2.5,
            "Trosoban": 3.0,
            "Troiposoban": 3.5,
            "Četvorosoban": 4.0,
            "Četvoroiposoban": 4.5,
            "Petosoban": 5.0,
            "Petoiiposoban": 5.5,
            "Šestosoban": 6.0,
            "Šestoiposoban": 6.5,
            "Sedmosoban": 7.0,
            "Sedmoiposoban": 7.5,
            "Višesoban": 8.0 }

IS_FURNISHED = {"Namešten" : True,
                "Polunamešten": True,
                "Prazan": False}

CE_FLAT_TYPE = ["Stan", "Stan u kući", "Kuća"]

@dataclass
class CEFlat:
    id: str = ""
    price: str = ""
    type: str = ""
    location: str = ""
    furnished: str = ""
    area: str = ""
    bedrooms: str = ""


def from_url(url):
    parts = url.split('/')
    if any([x == 'cityexpert.rs' for x in parts]):
        return from_city_expert(url)


@dataclass
class FlatDescription:
    sourceId: str
    description: str
    city: str
    region: str
    roomNumber: float
    square: float
    floor: float
    isFurnished: bool
    linkToAds: str
    source: str
    price: str


def from_city_expert(url) -> List[FlatDescription]:
    city = url.split('/')[-1]
    session = HTMLSession()
    req = session.get(url)
    req.html.render()

    flats = req.html.find('app-property-card')
    description = []
    for flat in flats:
        flat_desc = flat_from_element_ce(flat)
        if flat_desc.type.split()[-1] not in CE_FLAT_TYPE:
            continue
        desc = FlatDescription(sourceId=flat_desc.id,
                               description="",
                               city=city,
                               region=flat_desc.location,
                               roomNumber=ROOM_NUM.get(flat_desc.bedrooms, 0.0),
                               square=float(flat_desc.area.split(' ')[0]),
                               floor=0,
                               isFurnished=IS_FURNISHED.get(flat_desc.furnished, False),
                               linkToAds=flat.absolute_links.pop(),
                               source='cityexpert.rs',
                               price=flat_desc.price)
        description.append(desc)
    return description


def flat_from_element_ce(flat: Element) -> CEFlat:
    divs = flat.find('div')
    description = {}
    for elem in divs:
        if elem.attrs['class'] in CE_CLASSES:
            if CE_CLASSES[elem.attrs['class']] == 'id':
                description['id'] = elem.text
            if CE_CLASSES[elem.attrs['class']] == "price":
                description["price"] = elem.text
            if CE_CLASSES[elem.attrs['class']] == "type":
                description["type"] = elem.text
            if CE_CLASSES[elem.attrs['class']] == "location":
                description["location"] = elem.text
            if CE_CLASSES[elem.attrs['class']] == "furnished":
                description["furnished"] = elem.text
            if CE_CLASSES[elem.attrs['class']] == "props":
                if "m²" in elem.text:
                    description["area"] = elem.text
                else:
                    description["bedrooms"] = elem.text
    return CEFlat(**description)
