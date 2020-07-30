import json
import logging
import os

import azure.functions as func
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

formrec_endpoint = os.environ["FORM_RECOGNIZER_ENDPOINT"]
assert formrec_endpoint is not None

ocp_apim_key = os.environ["ENDPOINT_SECRET"]
assert ocp_apim_key is not None

model_id = os.environ["MODEL_ID"]
assert model_id is not None

credential = AzureKeyCredential(ocp_apim_key)

form_recognizer_client = FormRecognizerClient(formrec_endpoint, credential)


def get_value(fields, key):
    try:
        value = fields[key]
    except KeyError:
        return ""

    if not value.value_data:
        return ""

    return value.value_data.text


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    req_body = req.get_json()

    source_url = req_body.get("source_url")

    poller = form_recognizer_client.begin_recognize_custom_forms_from_url(
        model_id, source_url
    )
    custom_model_results = poller.result()

    if not custom_model_results:
        return func.HttpResponse("No custom results found.", status_code=202)

    fields = custom_model_results[0].fields

    response = json.dumps(
        {
            "nutriment_energy-kj": get_value(fields, "energy-kJ"),
            "nutriment_energy-kcal": get_value(fields, "energy-kcal"),
            "nutriment_fat": get_value(fields, "fat"),
            "nutriment_saturated-fat": get_value(fields, "saturated-fat"),
            "nutriment_carbohydrates": get_value(fields, "carbohydrates"),
            "nutriment_sugars": get_value(fields, "sugars"),
            "nutriment_proteins": get_value(fields, "proteins"),
            "nutriment_fiber": get_value(fields, "fiber"),
            "nutriment_salt": get_value(fields, "salt"),
            "nutriment_sodium": get_value(fields, "sodium"),
            "source_url": source_url,
        }
    )

    return func.HttpResponse(response, status_code=200)
