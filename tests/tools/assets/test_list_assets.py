import pytest

import src.tools.assets.list_assets as list_assets_module


class FakeAssetModelDump:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class FakeAssetsResource:
    def __init__(self, return_value):
        self.return_value = return_value
        self.kwargs = None

    async def list(self, **kwargs):
        self.kwargs = kwargs
        return self.return_value


class FakeClient:
    def __init__(self, return_value):
        self.assets = FakeAssetsResource(return_value)


@pytest.mark.asyncio
async def test_list_assets_serializes_asset_objects(monkeypatch):
    assets = [
        FakeAssetModelDump({"name": "one", "type": "file"}),
        {"name": "two", "type": "folder"},
    ]
    client = FakeClient(assets)
    monkeypatch.setattr(list_assets_module, "CLIENT", client)

    result = await list_assets_module.list_assets()

    assert result == [
        {"name": "one", "type": "file"},
        {"name": "two", "type": "folder"},
    ]


@pytest.mark.asyncio
async def test_list_assets_applies_filter_spec(monkeypatch):
    assets = [
        {"name": "alpha", "size": 10},
        {"name": "beta", "size": 20},
    ]
    client = FakeClient(assets)
    monkeypatch.setattr(list_assets_module, "CLIENT", client)

    result = await list_assets_module.list_assets(filter_spec="0.name")

    assert result == "alpha"


@pytest.mark.asyncio
async def test_list_assets_omits_none_parameters(monkeypatch):
    client = FakeClient([])
    monkeypatch.setattr(list_assets_module, "CLIENT", client)

    await list_assets_module.list_assets(
        file_type="image",
        limit=None,
        path=None,
        search_query=None,
        skip=None,
        sort=None,
        type=None,
    )

    assert client.assets.kwargs == {"file_type": "image"}
