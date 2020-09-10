from artifactsync.docker.model import DockerSyncDefinition, Status


class SyncJobRegistrar:

    def __init__(self):
        self._jobs = {}

    def register_job(self, job: DockerSyncDefinition):
        self._jobs[job.id] = job

    def get_job_status(self, job_id: str):
        if job_id in self._jobs.keys():
            return self._jobs[job_id].status
        return None

    def get_jobs(self):
        return self._jobs

    def set_job_as_active(self, job: DockerSyncDefinition):
        self._jobs[job.id].status.value = Status.RUNNING

    def finish_job(self, job: DockerSyncDefinition, status=Status.FINISHED):
        job.status.value = status
