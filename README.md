# pydlit

[![Build Status](https://travis-ci.com/MaibornWolff/pydlit.svg?branch=master)](https://travis-ci.com/MaibornWolff/pydlit)

**Daemon Less docker Image Transfer microservice on Python.**

Built in collaboration with **[@swoehrl-mw](https://github.com/swoehrl-mw)**

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
    "auth": { 
      "url": "<Authentication Endpoint. If authentication is requiring scope and service definition, include them in this URL.>",
      "token_type": "<Token type can either be JWT or Bearer>",
      "header": "<If authentication requires a header, put it here.>",
      "json": "<If authentication requires a JSON payload, put it here.>",
      "basicauth": {
        "user": "<username>",
        "password": "<password>"
      }
    }

  },
  "targets": [
    {
      "endpoint":  "<Docker registry V2 endpoint>",
      "overwrite": "<Boolean value: whether to overwrite an existing image in target registry. Default: 'false'>",
      "verify_tls": "<Boolean value: whether enable or disable TLS mode for network communication. Default: 'false'.>",
      "auth": "{...}"
    }
  ]
}
```
The "auth" block is **optional**. It is only needed if registry requires authentication. The same is true for the embedded
"basicauth" block. If the registry authenticates by BasicAuth, put the data here. **The token setup will be ignored, if BasicAuth is used.**
