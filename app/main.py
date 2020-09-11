import json
from dataclasses import asdict

from flask import Flask, request

from artifactsync.docker.docker_sync import DockerImageSyncManager
from artifactsync.docker.model import DockerSyncDefinition

app = Flask(__name__)

docker_sync_service = DockerImageSyncManager()


@app.route('/api/distribute/image', methods=["POST"])
def distribute_image():
    try:
        data = request.get_json()
        data = DockerSyncDefinition.schema().load(data)
    except KeyError as ex:
        return dict(status="error", msg=f"Failed to parse data: Missing field: {ex}"), 400
    except Exception as ex:
        return dict(status="error", msg=f"Failed to parse data: {ex}"), 400

    job_id = docker_sync_service.add_job(data)
    if job_id:
        return dict(status="success", msg="Image sync started", id=job_id), 201
    return dict(status="error", msg="Image not found"), 404


@app.route('/api/distribute/image/<job_id>', methods=["GET"])
def get_image_sync_status(job_id):
    job_status = docker_sync_service.get_job_status(job_id)
    if job_status:
        job_dct = asdict(job_status)
        job_dct["value"] = job_status.value.name
        return json.dumps(job_dct)
    else:
        return dict(status="error", msg="job with id not found"), 404


if __name__ == '__main__':
    docker_sync_service.start_background_sync()
    app.run(host="0.0.0.0", port=5001, threaded=True)
