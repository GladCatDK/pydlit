from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from dataclasses_json import DataClassJsonMixin, dataclass_json


class Status(Enum):
    QUEUED = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3


@dataclass_json
@dataclass
class ImageLayer(DataClassJsonMixin):
    media_type: str
    size: int
    digest: str
    data: bytes


@dataclass_json
@dataclass
class DockerImage(DataClassJsonMixin):
    name: str
    ref: str
    manifest: bytes
    layers: List[ImageLayer]


@dataclass_json
@dataclass
class BasicAuth(DataClassJsonMixin):
    user: str
    password: str


@dataclass_json
@dataclass
class Auth(DataClassJsonMixin):
    url: str
    header: Optional[str] = None
    json: Optional[str] = None
    token_type: Optional[str] = None
    token: Optional[str] = None
    basicauth: Optional[BasicAuth] = None


@dataclass_json
@dataclass
class SyncSource(DataClassJsonMixin):
    endpoint: str
    image: str
    ref: str
    verify_tls: Optional[bool] = False
    auth: Optional[Auth] = None


@dataclass_json
@dataclass
class JobStatus:
    value: Status
    started_at: str
    finished_endpoints: List[str] = field(default_factory=list)
    skipped_clusters: List[str] = field(default_factory=list)
    finished_at: Optional[str] = None


@dataclass_json
@dataclass
class SyncTarget:
    endpoint: str
    auth: Optional[Auth] = None
    overwrite: Optional[bool] = False
    verify_tls: Optional[bool] = False


@dataclass_json
@dataclass
class DockerSyncDefinition(DataClassJsonMixin):
    source: SyncSource
    targets: List[SyncTarget]
    issuer: Optional[str] = None
    retries_left: int = 3
    id: Optional[str] = None
    status: Optional[JobStatus] = None
