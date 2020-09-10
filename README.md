# pydlit
**Daemon Less docker Image Transfer microservice on Python.**

## Overview

It is designed to distribute a docker image from one source to multiple target repositories.
It runs purely on HTTP requests without using the Docker Daemon or other frameworks.

## Example Usage

Deploy a local registry for the test: `docker run -p 5000:5000 --restart=always --name registry registry:2`

Use the JSON file in the 'example' directory as your request: `curl -XPOST -H "Content-Type: application/json" -d @example_request.json http://localhost:5001/api/distribute/image`
This request will clone the hello-world image from Docker Hub to your local registry.

You will receive the following confirmation response:
```json
{
  "id": "<job-uuid>", 
  "msg": "Image sync started", 
  "status": "success"
}
```

You can check on the status of your job by calling: `curl -GET http://localhost:5001/api/distribute/image/"<job-uuid>"`
A response for the finished job will look as follows:
```json
{
    "value": "FINISHED",
    "started_at": "2020-09-10T14:17:07.880471+00:00",
    "finished_endpoints": ["http://localhost:5000/v2"],
    "skipped_clusters": [],
    "finished_at": "2020-09-10T14:17:13.412657+00:00"
}
```
Possible job states are: `QUEUED`, `RUNNING`, `FINISHED` and `FAILED`.

## Request reference
```json
{
  "source": {
    "endpoint": "<Docker registry V2 endpoint>",
    "image": "<Image name / path>",
    "ref": "<Image version>",
    "auth": { <Optional. Onyl requiered if registry requiers authentication>
      "url": "<Authentication Endpoint. If authentication is requieres scope and service definition, include them in this URL.>",
      "token_type": "<Token type can either be JWT or Baerer>"
      "header": "<If authentication requieres a header, put it here.>"
      "json": "<If authentication requieres a JSON payload, put it here.>"
      "basicauth": { <Optional. If the registry authentifies by BasicAtuh, put the data here. Token setup will be ignored, if BasicAuth is used.>
        "user": "<username>",
        "password": "<password>"
      }
    }

  },
  "targets": [
    {
      "endpoint":  "<Docker registry V2 endpoint>",
      "overwrite": "<Boolean value: whether to overwrite an existing image in target registry. Default: 'false'>"
      "verify_tls": "<Boolean value: whether enable or disable TLS mode for network communication. Default: 'false'.>"
      "auth": {...}
    }
  ]
}
```
