# Sirius Lite Web Client for Dify

* Code structure *
```
.
├── CODEOWNERS
├── Dockerfile
├── README.md
├── app
   ├── __init__.py
   ├── api
   │   ├── __init__.py
   │   ├── __pycache__
   │   │   ├── __init__.cpython-311.pyc
   │   │   ├── __init__.cpython-312.pyc
   │   │   ├── crud.cpython-311.pyc
   │   │   ├── crud.cpython-312.pyc
   │   │   ├── dify.cpython-311.pyc
   │   │   ├── dify.cpython-312.pyc
   │   │   ├── handle_token.cpython-311.pyc
   │   │   └── jwt_token.cpython-311.pyc
   │   ├── crud.py
   │   └── dify.py
   ├── config.py
   ├── main.py
   ├── requirements.txt
   └── ui
       └── SiriusLiteUI.html
```

# Install FastAPI 
```
cd to root of the project.
pip install -r requirements.txt
```

# Run Project
```
#Tenant id Maersk AD is fixed as 05d75c05-fa1a-42e7-9cf1-eb416c396f2d
export tenant_id="05d75c05-fa1a-42e7-9cf1-eb416c396f2d" 
export client_id="****"
export client_secret="****"
export redirect_base_uri="http://localhost:8080"
export dify_base_url="http://shared-siriuslite-api.dev.maersk-digital.net/v1"
export dify_api_key="app-***"

cd app && python main.py
```


# Api URLs
Helth: 
``` 
http://127.0.0.1:8080/health 
```
Chat:  
```
http://127.0.0.1:8080/dify/chat #use payload as below
```
Payload
```
{
    "inputs": {},
    "query": "What is the Enterprise SQL Dremio Data Platform?",
    "response_mode": "streaming",
    "user": "shomu-123"
}
```

# Curl Example
```
curl -X POST '<DIFY_API_URL>/chat-messages' \
--header 'Authorization: Bearer <DIFY_API_TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "inputs": {},
    "query": "What is the Enterprise SQL Dremio Data Platform?",
    "response_mode": "streaming",
    "conversation_id": "12345",
    "user": "user-123"
}'
```


# Docker 
```
export APP=sirius-lite-dify
export TAG=v2.3
docker build . -t ${APP}:${TAG}
docker run -p 8080:8080 ${APP}:${TAG}
```


# Read More about uvicorn  
    https://fastapi.tiangolo.com/?h=install#installation
    https://www.youtube.com/watch?v=tLKKmouUams

# Read more about fast-api streaming
    https://github.com/adamcyber1/fastapi-streaming/blob/main/Makefile

# Read Dify Apis 
    https://docs.dify.ai/user-guide/launching-dify-apps/developing-with-apis
