from rdflib.namespace import XSD
from utils.namespaces import *
import rdflib

supported_literals = {
    "doi": {
        "type": XSD.string,
        "exactMatch": wd.P356,
        "lbl": "doi"
    },
    "title": {
        "type": XSD.string,
        "exactMatch": schema.name,
        "lbl": "title"
    },
    "abstract": {
        "type": XSD.string,
        "exactMatch": schema.abstract,
        "lbl": "abstract"
    },
    "description": {
        "type": XSD.string,
        "exactMatch": schema.description,
        "lbl": "description"
    },
    "language": {
        "type": XSD.string,
        "exactMatch": schema.inLanguage,
        "lbl": "language"
    },
    "citation": {
        "type": XSD.string,
        "exactMatch": schema.citation,
        "lbl": "citation"
    },
    "intellectualRights": {
        "type": XSD.string,
        "closeMatch": dct.accessRights,
        "lbl": "intellectualRights"
    },
    "license": {
        "type": XSD.string,
        "closeMatch": dct.license,
        "lbl": "license"
    },
    "dataFormat": {
        "type": XSD.string,
        "lbl": "data format"
    },
    "version": {
        "type": XSD.string,
        "exactMatch": schema.version,
        "lbl": "version"
    },
    "keywordSet": {
        "type": XSD.string,
        "exactMatch": schema.keywords,
        "lbl": "keywords"
    },
    "measurement": {
        "type": XSD.string,
        "lbl": "measurement"
    },
    "equipment": {
        "type": XSD.string,
        "lbl": "equipment"
    },
    "surName": {
        "type": XSD.string,
        "exactMatch": schema.familyName,
        "lbl": "surname"
    },
    "givenName": {
        "type": XSD.string,
        "exactMatch": schema.givenName,
        "lbl": "givenName"
    },
    "electronicMail": {
        "type": XSD.string,
        "exactMatch": schema.email,
        "lbl": "email"
    },
    "phone": {
        "type": XSD.string,
        "exactMatch": schema.telephone,
        "lbl": "phone"
    },
    "organization": {
        "type": XSD.string,
        "exactMatch": schema.organization,
        "lbl": "organization"
    },
    "city": {
        "type": XSD.string,
        "lbl": "city"
    },
    "country": {
        "type": XSD.string,
        "lbl": "country"
    },
    "deliveryPoint": {
        "type": XSD.string,
        "lbl": "deliveryPoint"
    },
    "postalCode": {
        "type": XSD.string,
        "exactMatch": schema.postalCode,
        "lbl": "postalCode"
    },
    "street": {
        "type": XSD.string,
        "exactMatch": schema.streetAddress,
        "lbl": "street"
    },
    "alternateIdentifier": {
        "type": XSD.url,
        "exactMatch": schema.identifier,
        "lbl": "alternateIdentifier"
    },
    "publicationDate": {
        "type": XSD.date,
        "exactMatch": schema.datePublished,
        "lbl": "publicationDate"
    },
    "numberOfRecords": {
        "type": XSD.int,
        "exactMatch": wd.P4876,
        "lbl": "numberOfRecords"
    },
    "northBoundingCoordinate": {
        "type": XSD.decimal,
        "lbl": "northBoundingCoordinate"
    },
    "southBoundingCoordinate": {
        "type": XSD.decimal,
        "lbl": "southBoundingCoordinate"
    },
    "eastBoundingCoordinate": {
        "type": XSD.decimal,
        "lbl": "eastBoundingCoordinate"
    },
    "westBoundingCoordinate": {
        "type": XSD.decimal,
        "lbl": "westBoundingCoordinate"
    },
    "numberOfMip": {
        "type": XSD.int,
        "lbl": "numberOfMIP"
    },
    "numberOfVip": {
        "type": XSD.int,
        "lbl": "numberOfVIP"
    },
    "numberOfGp": {
        "type": XSD.int,
         "lbl": "numberOfGP"
    },
    "numberOfEp": {
        "type": XSD.int,
        "lbl": "numberOfMIP"
    },
    "startDate": {
        "type": XSD.date,
        "exactMatch": schema.startDate,
        "lbl": "startDate"
    },
    "beginDate": {
        "type": XSD.date,
        "exactMatch": schema.startDate,
        "lbl": "startDate"
    },
    "endDate": {
        "type": XSD.date,
        "exactMatch": schema.startDate,
        "lbl": "startDate"
    },
    "taxonCommonName": {
        "type": XSD.string,
        "exactMatch": wd.P1843,
        "lbl": "taxonCommonName"
    },
    "taxonRankValue": {
        "type": XSD.string,
        "exactMatch": wd.P105,
        "lbl": "taxonRankValue"
    },
    "taxonRankName": {
        "type": XSD.string,
        "exactMatch": wd.P105,
        "lbl": "taxonRankName"
    },
    # "taxonKingdom": {
    #     "type": XSD.string,
    #     "map": wd.Q36732,
    #     "lbl": "taxonKingdom"
    # },
    # "taxonFamily": {
    #     "type": XSD.string,
    #     "map": wd.Q35409,
    #     "lbl": "taxonFamily"
    # },
    # "taxonDomain": {
    #     "type": XSD.string,
    #     "map": wd.Q146481,
    #     "lbl": "taxonDomain"
    # },
    "funding": {
        "type": XSD.string,
        "exactMatch": schema.funding,
        "lbl": "funding"
    },
    "introduction": {
        "type": XSD.string,
        "lbl": "introduction"
    }
}

def get_relation_existingvocab_match(relString, exactMatch=True):
    if relString in supported_literals.keys():
        rel = supported_literals[relString]
        if exactMatch:
            return rel.get('exactMatch', None)
        else:
            return rel.get('closeMatch', None)


def get_relation(relString):
    if relString in supported_literals.keys():
        rel = supported_literals[relString]
        return rdflib.URIRef('{}{}'.format(bmo, relString)), rel['lbl']
    else:
        print('relation for literal not supported for: {}'.format(relString))
        return rdflib.URIRef('{}{}'.format(bmo, relString)), relString


def get_literal_type(lit):
    if lit in supported_literals.keys():
        return supported_literals[lit]['type']

def get_node_type(nodeName):
    nodeName = nodeName.split('_')[0]
    if nodeName in ['temporalCoverage']:
        return bmo.TemporalCoverage, None, None
    elif nodeName in ['taxonomicCoverage', 'geographicCoverage']:
        return rdflib.URIRef('{}{}'.format(bmo, nodeName[0].upper()+nodeName[1:])), None, None
    elif nodeName in ['contactPerson', 'dataCreator', 'teamLeader', 'metadataProvider']:
        return bmo.Person, schema.Person, None
    elif nodeName in ['address']:
        return bmo.Address, schema.PostalAddress, None
    elif nodeName in ['boundingCoordinates']:
        return bmo.BoundingCoordinates, schema.GeoCoordinates, None
    elif nodeName in ['numberOfPlots']:
        return bmo.NumberOfPlots, None, None
    elif nodeName in ['project']:
        return bmo.Project, schema.Project, None
    elif nodeName in ['method']:
        return bmo.Method, None, None
    else:
        return None, None, None
