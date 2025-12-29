import pytest

from src.tools.accounts.usage.get_accounts_usage import get_accounts_usage


class FakeUsageResponse:
    def __init__(self, data):
        self._data = data

    def dict(self):
        return self._data


class FakeUsage:
    def __init__(self, data):
        self._data = data

    async def get(self, **kwargs):
        return FakeUsageResponse(self._data)


class FakeAccounts:
    def __init__(self, data):
        self.usage = FakeUsage(data)


class FakeClient:
    def __init__(self, data):
        self.accounts = FakeAccounts(data)


@pytest.mark.asyncio
async def test_get_accounts_usage_rejects_bad_date_format():
    client = FakeClient({})
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        await get_accounts_usage(
            client=client, start_date="20240101", end_date="2024-02-01"
        )


@pytest.mark.asyncio
async def test_get_accounts_usage_rejects_range_over_90_days():
    client = FakeClient({})
    with pytest.raises(ValueError, match="less than 90 days"):
        await get_accounts_usage(
            client=client, start_date="2024-01-01", end_date="2024-04-01"
        )


@pytest.mark.asyncio
async def test_get_accounts_usage_returns_full_response_and_aliases():
    data = {
        "bandwidth_bytes": 43416701233,
        "extension_units_count": 5997,
        "media_library_storage_bytes": 34209249206,
        "original_cache_storage_bytes": 0,
        "video_processing_units_count": 19757,
        "bandwidthBytes": 43416701233,
        "mediaLibraryStorageBytes": 34209249206,
        "videoProcessingUnitsCount": 19757,
        "extensionUnitsCount": 5997,
        "originalCacheStorageBytes": 0,
    }
    client = FakeClient(data)

    result = await get_accounts_usage(
        client=client,
        start_date="2024-01-01",
        end_date="2024-01-15",
    )

    # Snake_case fields are preserved
    for key, value in data.items():
        assert result[key] == value

    # CamelCase aliases are added
    assert result["bandwidthBytes"] == 43416701233
    assert result["mediaLibraryStorageBytes"] == 34209249206
    assert result["videoProcessingUnitsCount"] == 19757
    assert result["extensionUnitsCount"] == 5997
    assert result["originalCacheStorageBytes"] == 0


@pytest.mark.asyncio
async def test_get_accounts_usage_respects_filter_spec():
    data = {
        "bandwidth_bytes": 123,
        "extension_units_count": 0,
        "media_library_storage_bytes": 0,
        "original_cache_storage_bytes": 0,
        "video_processing_units_count": 0,
    }
    client = FakeClient(data)

    result = await get_accounts_usage(
        client=client,
        start_date="2024-01-01",
        end_date="2024-01-02",
        filter_spec="bandwidth_bytes",
    )

    assert result == 123
