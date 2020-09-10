import json

import requests
from requests.auth import HTTPBasicAuth

from .model import *
from ..util.log import logger

'''
This utility is built to transfer docker images from the GitLab docker registry in source to the registries in the targets.
'''
LAYER_KEY_V2 = "layers"
MANIFEST_V2_CONTENT_TYPE = "application/vnd.docker.distribution.manifest.v2+json"


class DockerAPI:
    def __init__(self):
        pass

    def _get_auth_token(self, auth: Auth, verify_tls: bool):
        response = requests.get(url=auth.url,
                                headers=auth.header,
                                json=auth.json,
                                verify=verify_tls)
        if response.status_code >= 400:
            raise Exception(f"Source registry authentication failure: {response.text}")
        return response.json().get('token')

    def authorize_for_endpoints(self, job: DockerSyncDefinition):
        if job.source.auth and not job.source.auth.basicauth:
            job.source.auth.token = self._get_auth_token(job.source.auth, job.source.verify_tls)
        for target in job.targets:
            if target.auth and not target.auth.basicauth:
                target.auth.token = self._get_auth_token(target.auth, target.verify_tls)

    def image_exists_in_source(self, source: SyncSource):
        url = f"{source.endpoint}/{source.image}/manifests/{source.ref}"
        return self._image_exists(url, source.auth, source.verify_tls)

    def image_exists_in_target(self, target: SyncTarget, source: SyncSource):
        url = f"{target.endpoint}/{source.image}/manifests/{source.ref}"
        return self._image_exists(url, target.auth, target.verify_tls)

    def _image_exists(self, url: str, auth: Auth, verify_tls: bool):
        basic_auth, header = self._build_auth_data(auth)
        manifest_response = requests.head(url=url,
                                          auth=basic_auth,
                                          headers=header,
                                          verify=verify_tls)
        code = manifest_response.status_code
        if code == 200:
            return True
        elif code == 404:
            return False
        else:
            raise Exception(f"Error while checking if image exists: {code}: {manifest_response.text}")

    def pull_image_from_source(self, source: SyncSource):
        '''
        Reference: https://docs.docker.com/registry/spec/api/#pulling-an-image
        '''
        manifest = self._download_manifest(source)
        manifest_json = json.loads(manifest)
        layers = []
        for layer_descriptor in manifest_json.get(LAYER_KEY_V2) + [manifest_json.get("config")]:
            layer = self._download_layer(source, layer_descriptor)
            layers.append(layer)
        logger.info("Downloaded all layers.")
        return DockerImage(name=source.image, ref=source.ref, manifest=manifest, layers=layers)

    def _download_manifest(self, source: SyncSource):
        header = {"Accept": MANIFEST_V2_CONTENT_TYPE}
        basic_auth, header = self._build_auth_data(source.auth, add_header=header)
        manifest_response = requests.get(
            url=f"{source.endpoint}/{source.image}/manifests/{source.ref}",
            headers=header,
            auth=basic_auth,
            verify=source.verify_tls
        )
        if manifest_response.status_code != 200:
            raise Exception(f"Error while downloading manifest for {source.image}: {manifest_response.text}")
        return manifest_response.content

    def _download_layer(self, source: SyncSource, layer_descriptor):
        media_type = layer_descriptor.get("mediaType")
        size = layer_descriptor.get("size")
        digest = layer_descriptor.get("digest")
        logger.info(f"Downloading image layer {digest}")
        basic_auth, header = self._build_auth_data(source.auth)
        layer_response = requests.get(url=f"{source.endpoint}/{source.image}/blobs/{digest}",
                                      auth=basic_auth,
                                      headers=header,
                                      verify=source.verify_tls)
        if not layer_response.ok:
            raise Exception(f"Error while pulling image layers: {layer_response.text}")
        return ImageLayer(media_type=media_type, size=size, digest=digest, data=layer_response.content)

    def _upload_layer(self, image, layer, target: SyncTarget):
        basic_auth, header = self._build_auth_data(target.auth)
        upload_request = requests.post(f"{target.endpoint}/{image.name}/blobs/uploads/",
                                       auth=basic_auth,
                                       headers=header,
                                       verify=target.verify_tls)
        location = upload_request.headers.get("location")
        logger.info(f"Uploading layer {layer.digest}")
        if not header:
            header = {}
        header["Content-Length"] = f"{layer.size}"
        header["Content-Type"] = "application/octet-stream"
        params = {"digest": layer.digest}
        layer_response = requests.put(url=location,
                                      auth=basic_auth,
                                      params=params,
                                      headers=header,
                                      data=layer.data,
                                      verify=target.verify_tls)
        if not layer_response.ok:
            raise Exception(f"Error while pushing image layers: {layer_response.text}")

    def push_image_to_target(self, image, target: SyncTarget):
        '''
        Reference: https://docs.docker.com/registry/spec/api/#pushing-an-image
        '''
        logger.info(f"Pushing image {image.name}:{image.ref} to {target.endpoint}")
        for layer in image.layers:
            self._upload_layer(image, layer, target)
        header = {"Content-Type": MANIFEST_V2_CONTENT_TYPE}
        basic_auth, header = self._build_auth_data(target.auth, add_header=header)
        manifest_response = requests.put(f"{target.endpoint}/{image.name}/manifests/{image.ref}",
                                         data=image.manifest,
                                         headers=header,
                                         auth=basic_auth,
                                         verify=target.verify_tls)
        if not manifest_response.ok:
            raise Exception(f"Error while uploading manifest: {manifest_response.text}")
        logger.info(f"Pushed image {image.name}:{image.ref} to {target}")

    def _build_auth_data(self, auth, add_header=None):
        basic_auth = None
        if auth:
            if auth.basicauth:
                basic_auth = HTTPBasicAuth(auth.basicauth.user, auth.basicauth.password)
            if auth.token:
                if not add_header:
                    add_header = {}
                add_header["Authorization"] = f"{auth.token_type} {auth.token}"
        return basic_auth, add_header
