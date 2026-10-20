"""Asset storage: uploads to AWS S3 when it's configured, and silently
falls back to serving files off local disk when it isn't (so the app is
fully usable in local dev with zero cloud setup).

Switching between the two is just setting/unsetting the AWS_* variables in
the environment — no code changes needed.
"""
from pathlib import Path
from fastapi import UploadFile, HTTPException
from starlette.concurrency import run_in_threadpool
import uuid

from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_S3_BUCKET,
    LOCAL_UPLOAD_DIR,
    PUBLIC_BASE_URL,
    MAX_UPLOAD_BYTES,
    storage_is_s3,
)
from app.models import AssetType

_CONTENT_TYPE_MAP = {
    "image": AssetType.IMAGE,
    "video": AssetType.VIDEO,
    "audio": AssetType.AUDIO,
}


def infer_asset_type(content_type: str | None) -> AssetType:
    if not content_type:
        return AssetType.OTHER
    prefix = content_type.split("/")[0]
    return _CONTENT_TYPE_MAP.get(prefix, AssetType.OTHER)


def _s3_client():
    import boto3

    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


class UploadResult:
    def __init__(self, url: str, size_bytes: int):
        self.url = url
        self.size_bytes = size_bytes


async def save_upload(file: UploadFile, project_id: uuid.UUID) -> UploadResult:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)}MB upload limit",
        )

    suffix = Path(file.filename or "").suffix
    key = f"{project_id}/{uuid.uuid4()}{suffix}"

    if storage_is_s3():
        url = await _upload_to_s3(key, data, file.content_type)
    else:
        url = _upload_to_local(key, data)

    return UploadResult(url=url, size_bytes=len(data))


async def _upload_to_s3(key: str, data: bytes, content_type: str | None) -> str:
    from botocore.exceptions import BotoCoreError, ClientError

    def _put():
        _s3_client().put_object(
            Bucket=AWS_S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type or "application/octet-stream",
        )

    try:
        await run_in_threadpool(_put)
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(status_code=502, detail=f"S3 upload failed: {exc}")

    return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


def _upload_to_local(key: str, data: bytes) -> str:
    base = Path(LOCAL_UPLOAD_DIR)
    full_path = base / key
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(data)
    return f"{PUBLIC_BASE_URL}/uploads/{key}"


def _s3_key_from_url(file_url: str) -> str | None:
    marker = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/"
    if not file_url.startswith(marker):
        return None
    return file_url[len(marker):]


async def delete_stored_file(file_url: str, project_id: uuid.UUID) -> None:
    """Best-effort cleanup of an asset's underlying file, whichever backend
    stored it. Silently no-ops on anything that doesn't look like ours (an
    externally-registered URL, for example) or on failure — a stray
    orphaned file is a much smaller problem than blocking a delete.

    Only files under this project's own key prefix are ever touched:
    file_url can be client-supplied (see POST /projects/{id}/assets), so
    without this check a crafted URL could delete another project's file
    or, via "..", anything on local disk."""
    prefix = f"{project_id}/"

    s3_key = _s3_key_from_url(file_url)
    if s3_key is not None:
        if not s3_key.startswith(prefix) or ".." in s3_key.split("/"):
            return

        from botocore.exceptions import BotoCoreError, ClientError

        def _delete():
            _s3_client().delete_object(Bucket=AWS_S3_BUCKET, Key=s3_key)

        try:
            await run_in_threadpool(_delete)
        except (BotoCoreError, ClientError):
            pass
        return

    marker = f"{PUBLIC_BASE_URL}/uploads/"
    if not file_url.startswith(marker):
        return
    relative = file_url[len(marker):]
    project_dir = (Path(LOCAL_UPLOAD_DIR) / str(project_id)).resolve()
    path = (Path(LOCAL_UPLOAD_DIR) / relative).resolve()
    if not path.is_relative_to(project_dir):
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
