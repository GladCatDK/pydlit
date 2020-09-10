from datetime import datetime
import time
import uuid

from .sync_job_manager import SyncJobRegistrar
from ..base_sync_manager import BaseSyncManager, now
from ..util.log import logger
from .model import JobStatus, DockerSyncDefinition, Status
from .docker_api import DockerAPI


class DockerImageSyncManager(BaseSyncManager):
    def __init__(self):
        super().__init__()
        self._docker_api = DockerAPI()
        self._sync_job_manager = SyncJobRegistrar()

    def add_job(self, job_def: DockerSyncDefinition):
        self._docker_api.authorize_for_endpoints(job_def)
        if not self._docker_api.image_exists_in_source(job_def.source):
            return None
        job_id = str(uuid.uuid4())
        status = JobStatus(value=Status.QUEUED, started_at=now().isoformat())
        job_def.id = job_id
        job_def.status = status
        self._sync_job_manager.register_job(job_def)
        return job_id

    def get_job_status(self, job_id):
        return self._sync_job_manager.get_job_status(job_id)

    def _sync_thread(self):
        while True:
            logger.debug("sync thread run")
            try:
                for job in self._sync_job_manager.get_jobs().values():
                    try:
                        if job.status.value == Status.QUEUED:
                            self._sync_job_manager.set_job_as_active(job)
                            self._sync_image(job)
                    except:
                        logger.exception(f"Exception during sync of {job.id}")
                    self._last_sync_run = datetime.now()
            except:
                logger.exception("Exception during sync run")
            time.sleep(5)
            self._last_sync_run = datetime.now()

    def _sync_image(self, job: DockerSyncDefinition):
        if not job.retries_left > 0:
            self._sync_job_manager.finish_job(job, status=Status.FAILED)
            logger.error(f"Job {job.id} exceeded number of retries. Job failed.")
            return
        job.retries_left -= 1
        failures = False
        image = None
        for target in job.targets:
            logger.info(f"Starting docker image sync of job {job.id} to {target.endpoint}")
            if target.endpoint in job.status.finished_endpoints or target.endpoint in job.status.skipped_clusters:
                logger.info(f"Sync of job {job.id} to {target.endpoint} already finished. Skipping.")
                continue
            try:
                if self._docker_api.image_exists_in_target(target, job.source) and not target.overwrite:
                    logger.info(f"Image {job.source.image}:{job.source.ref} already exists on {target.endpoint}. Skipping.")
                    job.status.skipped_clusters.append(target.endpoint)
                else:
                    if not image:
                        image = self._docker_api.pull_image_from_source(job.source)
                    self._docker_api.push_image_to_target(image, target)
                    job.status.finished_endpoints.append(target.endpoint)
            except:
                logger.exception(f"Exception during docker image sync of job {job.id} to {target.endpoint}")
                failures = True
        if failures:
            logger.error(f"Error in docker image sync job {job.id}")
        else:
            job.status.finished_at = now().isoformat()
            job.status.value = "finished"
            self._sync_job_manager.finish_job(job)
            logger.info(f"Finished docker image sync of job {job.id}")

