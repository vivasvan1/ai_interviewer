import os
import requests


AZURE_COGNITIVE_SERVICE_URL = "https://vaato-vision.cognitiveservices.azure.com"
AZURE_AI_SERVICE_KEY="cb7eb0db004e40719e6d6d4cb836e713"

def videoIndexer(index_name):
    url = f"{os.environ.get("OPENAI_API_KEY")}/retrieval/indexes/{index_name}?api-version=2024-05-01-preview"

    data = {
            'metadataSchema': {
                'fields': [
                {
                    'name': 'cameraId',
                    'searchable': False,
                    'filterable': True,
                    'type': 'string'
                },
                {
                    'name': 'timestamp',
                    'searchable': False,
                    'filterable': True,
                    'type': 'datetime'
                }
                ]
            },
            'features': [
                {
                'name': 'vision',
                'domain': 'surveillance'
                },
                {
                'name': 'speech'
                }
            ]
        }
    headers = {
        "Ocp-Apim-Subscription-Key": os.environ.get("AZURE_AI_SERVICE_KEY"),
        "Content-Type": "application/json"
    }
    try:
        resposne = requests.put(url,data,headers=headers)
    except :
        raise
    
    