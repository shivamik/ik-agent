import os

import pytest

import src.tools.beta.v2.files.upload_v2_beta_files as upload_module


class FakeUploadModelDump:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class FakeUploadDict:
    def __init__(self, data):
        self._data = data

    def dict(self):
        return self._data


class FakeFilesResource:
    def __init__(self, return_value):
        self.return_value = return_value
        self.kwargs = None

    async def upload(self, **kwargs):
        self.kwargs = kwargs
        return self.return_value


class FakeV2:
    def __init__(self, return_value):
        self.files = FakeFilesResource(return_value)


class FakeBeta:
    def __init__(self, return_value):
        self.v2 = FakeV2(return_value)


class FakeClient:
    def __init__(self, return_value):
        self.beta = FakeBeta(return_value)


@pytest.mark.asyncio
async def test_upload_v2_beta_files_serializes_model_dump(monkeypatch):
    client = FakeClient(FakeUploadModelDump({"file_id": "123"}))
    monkeypatch.setattr(upload_module, "CLIENT", client)

    result = await upload_module.upload_v2_beta_files(
        file="base64data",
        file_name="image.jpg",
    )

    assert result == {"file_id": "123"}


@pytest.mark.asyncio
async def test_upload_v2_beta_files_serializes_dict(monkeypatch):
    client = FakeClient(FakeUploadDict({"status": "ok"}))
    monkeypatch.setattr(upload_module, "CLIENT", client)

    result = await upload_module.upload_v2_beta_files(
        file="https://example.com/file.jpg",
        file_name="file.jpg",
    )

    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_upload_v2_beta_files_omits_none_parameters(monkeypatch):
    client = FakeClient({"file_id": "456"})
    monkeypatch.setattr(upload_module, "CLIENT", client)

    await upload_module.upload_v2_beta_files(
        file="binary",
        file_name="asset.png",
        token=None,
        folder=None,
        tags=None,
        use_unique_file_name=True,
    )

    assert client.beta.v2.files.kwargs == {
        "file": "binary",
        "file_name": "asset.png",
        "use_unique_file_name": True,
    }


@pytest.mark.asyncio
async def test_upload_v2_beta_files_applies_filter_spec(monkeypatch):
    client = FakeClient({"file_id": "789", "name": "asset.jpg"})
    monkeypatch.setattr(upload_module, "CLIENT", client)

    result = await upload_module.upload_v2_beta_files(
        file="base64",
        file_name="asset.jpg",
        filter_spec="file_id",
    )

    assert result == "789"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("IMAGEKIT_PRIVATE_KEY"),
    reason="IMAGEKIT_PRIVATE_KEY is required for real API upload",
)
async def test_upload_v2_beta_files_real_upload():
    with open("tests/fixtures/gemini_generated.png", "rb") as f:
        file_data = f.read()

    response = await upload_module.upload_v2_beta_files(
        file=file_data,
        file_name="gemini_test_image.png",
        use_unique_file_name=True,
    )

    assert response["file_type"] == "image"
    assert response["name"].endswith(".png")
    assert response["file_id"]
    assert response["url"].startswith("https://")
