# -*- coding: utf-8 -*-
"""S3 / MinIO 存储后端。

使用标准 S3 签名请求（stdlib + hmac），零第三方依赖即可对接
AWS S3 或自建 MinIO（兼容 S3 API）。需要安装 boto3 时可用
更完整的实现（见 docs/storage-s3.md）。
"""
from __future__ import annotations

import hashlib
import hmac
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import formatdate
from typing import Any, Optional

from ..errors import StorageError
from ..types import StorageBackend
from .base import SnapshotStore


class _S3Client:
    """极简 S3 客户端（AWS Signature V4）。"""

    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str,
                 region: str = "us-east-1", prefix: str = "snapshots/"):
        self.endpoint = endpoint.rstrip("/")
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.prefix = prefix

    def _sign(self, method: str, key: str, payload_hash: str, headers: dict[str, str]) -> str:
        date = datetime.now(timezone.utc)
        amz_date = date.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = date.strftime("%Y%m%d")
        headers["x-amz-date"] = amz_date
        headers["x-amz-content-sha256"] = payload_hash
        canonical_headers = "".join(f"{k}:{headers[k].strip()}\n" for k in sorted(headers))
        signed_headers = ";".join(sorted(headers))
        canonical_request = f"{method}\n{key}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        scope = f"{date_stamp}/{self.region}/s3/aws4_request"
        string_to_sign = (
            f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n"
            f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        )
        def _hmac(k, msg):
            return hmac.new(k, msg.encode(), hashlib.sha256).digest()
        k_date = _hmac(("AWS4" + self.secret_key).encode(), date_stamp)
        k_region = _hmac(k_date, self.region)
        k_service = _hmac(k_region, "s3")
        k_signing = _hmac(k_service, "aws4_request")
        sig = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        headers["Authorization"] = (
            f"AWS4-HMAC-SHA256 Credential={self.access_key}/{scope}, "
            f"SignedHeaders={signed_headers}, Signature={sig}"
        )
        return amz_date

    def _request(self, method: str, key: str, body: bytes = b"") -> tuple[int, bytes]:
        url = f"{self.endpoint}/{self.bucket}/{urllib.parse.quote(key)}"
        headers = {"host": urllib.parse.urlparse(self.endpoint).netloc}
        payload_hash = hashlib.sha256(body).hexdigest()
        self._sign(method, "/" + self.bucket + "/" + key, payload_hash, headers)
        req = urllib.request.Request(url, data=body or None, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def put(self, key: str, data: bytes) -> None:
        code, _ = self._request("PUT", key, data)
        if code >= 300:
            raise StorageError(f"S3 PUT 失败: HTTP {code}")

    def get(self, key: str) -> Optional[bytes]:
        code, body = self._request("GET", key)
        if code == 404:
            return None
        if code >= 300:
            raise StorageError(f"S3 GET 失败: HTTP {code}")
        return body

    def delete(self, key: str) -> None:
        self._request("DELETE", key)


class S3Store(SnapshotStore):
    backend = StorageBackend.S3

    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str,
                 region: str = "us-east-1", prefix: str = "snapshots/"):
        self.client = _S3Client(endpoint, bucket, access_key, secret_key, region, prefix)

    def _key(self, sid: str) -> str:
        return f"{self.client.prefix}{sid}.snap"

    def put(self, snapshot_id: str, data: bytes, meta: dict[str, Any]) -> None:
        self.client.put(self._key(snapshot_id), data)
        self.client.put(self._key(snapshot_id) + ".meta", json.dumps(meta).encode())

    def get_bytes(self, snapshot_id: str) -> Optional[bytes]:
        return self.client.get(self._key(snapshot_id))

    def delete(self, snapshot_id: str) -> None:
        self.client.delete(self._key(snapshot_id))
        self.client.delete(self._key(snapshot_id) + ".meta")

    def list(self) -> list[dict[str, Any]]:
        # 简化：S3 列表需额外实现，此处返回空（生产用 boto3 见 docs）
        return []


class MinioStore(S3Store):
    """MinIO 别名（同为 S3 API）。"""
    backend = StorageBackend.MINIO


from ..storage import store_registry  # noqa: E402

store_registry.register("s3", S3Store)
store_registry.register("minio", MinioStore)

__all__ = ["S3Store", "MinioStore"]
