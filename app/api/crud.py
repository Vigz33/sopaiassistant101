# Author: Shomu Maitra
# Email: s.maitra@maersk.com
# Description: Crud core apis
# Date: 20th March 2024

from typing import Any
import requests
import json
import time

# Create Http POST call
def create(url, headers, payload):
    try:
        response = requests.post(url, headers=headers, data=payload, stream=True)
        # Check if the request was successful (status code 2xx)
        if response.status_code == requests.codes.ok:
            # Iterate over the response content, line by line
            for line in response.iter_lines():
                # Skip empty lines
                if line:
                    try:
                        received_line_data = line.decode() # Decode the bytes to string
                        if received_line_data.startswith("data:"):
                            truncated_string = received_line_data[len("data:"):]
                        else:
                            truncated_string = received_line_data
                        print(f"Received line data: {truncated_string}")

                        # Convert JSON string to JSON object (dictionary)
                        json_object = json.loads(truncated_string)

                        print("Who:", json_object.get('event'))
                        answer = ""
                        if json_object.get('event') == "message" or json_object.get('event') == "agent_message":
                            answer = json_object.get('answer')
                            print("Ans:", answer)
                            yield answer  # Yield the answer when available

                    except json.JSONDecodeError as e:
                        msg_string = f"Backend error parsing message JSON: {str(e)}"
                        print(msg_string)
                        #yield msg_string
                        
        else:
            msg_string = f"Backend failed with status code: {str(response.status_code)}"
            print(msg_string)
            yield msg_string
    except requests.exceptions.RequestException as e:
        msg_string = f"RequestException: {str(e)}"
        print(msg_string)
        yield msg_string
    except Exception as e:
        msg_string = f"Backend error: {str(e)}"
        print(msg_string)
        yield msg_string

