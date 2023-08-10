from typing import Dict, Optional

from truss.remote.baseten.auth import AuthService
from truss.remote.truss_remote import TrussService
from truss.truss_handle import TrussHandle

DEFAULT_STREAM_ENCODING = "utf-8"


class BasetenService(TrussService):
    def __init__(
        self,
        model_id: str,
        model_version_id: str,
        is_draft: bool,
        api_key: str,
        service_url: str,
        truss_handle: Optional[TrussHandle] = None,
    ):

        super().__init__(is_draft=is_draft, service_url=service_url)
        self._model_id = model_id
        self._model_version_id = model_version_id
        self._auth_service = AuthService(api_key=api_key)
        self._truss_handle = truss_handle

    def is_live(self) -> bool:
        raise NotImplementedError

    def is_ready(self) -> bool:
        raise NotImplementedError

    def predict(self, model_request_body: Dict):
        invocation_url = f"{self._service_url}/predict"
        response = self._send_request(
            invocation_url, "POST", data=model_request_body, stream=True
        )

        if response.headers.get("transfer-encoding") == "chunked":
            # Case of streaming response, the backend does not set an encoding, so
            # manually decode to the contents to utf-8 here.
            def decode_content():
                for chunk in response.iter_content(
                    chunk_size=8192, decode_unicode=True
                ):
                    yield chunk.decode(response.encoding or DEFAULT_STREAM_ENCODING)

            return decode_content()

        return response.json()["model_output"]

    def authenticate(self) -> dict:
        return self._auth_service.authenticate().header()
