import requests
import base64
from colorama import Fore, Style
import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

string_to_encode = config['azure_devops']['personal_access_token']
organization_url = config['azure_devops']['organization_url']
project_name = config['azure_devops']['project_name']
pipeline_name = config['azure_devops']['pipeline_name']
pipeline_id = config['azure_devops']['pipeline_id']
pipeline_to_compare_id = config['azure_devops']['pipeline_to_compare_id']

personal_access_token_base64 = base64.b64encode(f":{string_to_encode}".encode("ascii")).decode("ascii")

def get_pipeline_url(pipeline_id):
    return f"{organization_url}/{project_name}/_apis/release/definitions/{pipeline_id}?api-version=6.1-preview.4"

def get_request_data(url):
    headers = {
        "Authorization": f"Basic {personal_access_token_base64}",
        "Content-Type": "application/json",
    }

    return requests.get(url, headers=headers)

url = get_pipeline_url(pipeline_id)


response = get_request_data(url)
response_to_compare = get_request_data(get_pipeline_url(pipeline_to_compare_id))


def get_final_values_with_keys(obj, current_key=""):
    final_values = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = current_key + '.' + key if current_key else key
            final_values.extend(get_final_values_with_keys(value, new_key))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            new_key = current_key + '.' + str(index) if current_key else str(index)
            final_values.extend(get_final_values_with_keys(item, new_key))
    else:
        final_values.append((current_key, obj))
    return final_values

def get_value_from(my_list,key):
    for d in my_list:
        if d[0] == key:
            value = d[1]
            return value
    return ""

if response.status_code == 200:
    pipeline = response.json()
    pipeline_to_compare = response_to_compare.json()

    print(f"Pipeline ID: {pipeline['id']}, Name: {pipeline['name']}")
    print(f"Pipeline to compare ID: {pipeline_to_compare['id']}, Name: {pipeline_to_compare['name']}")

    pipeline_values = get_final_values_with_keys(pipeline["variables"])
    pipeline_values = sorted(pipeline_values, key=lambda x: x[0])
    pipeline_values_to_compare = get_final_values_with_keys(pipeline_to_compare["variables"])
    pipeline_values_to_compare = sorted(pipeline_values_to_compare, key=lambda x: x[0])

    for i in range(len(pipeline_values)):

        if pipeline_values[i][1] != get_value_from(pipeline_values_to_compare, pipeline_values[i][0]):
            print(Fore.RED + f"{pipeline_values[i][0]} : {pipeline_values[i][1]} - {get_value_from(pipeline_values_to_compare, pipeline_values[i][0])}" + Style.RESET_ALL)
        else:
            print(f"{pipeline_values[i][0]} : {pipeline_values[i][1]} - {get_value_from(pipeline_values_to_compare, pipeline_values[i][0])}")

else:
    print(f"Error: {response.status_code}, {response.text}")





