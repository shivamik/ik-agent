from typing import List, Union, Any, Optional
from imagekitio.types.file import File
from imagekitio.types.folder import Folder
from imagekitio.types.accounts.origin_response import (
    S3,
    S3Compatible,
    CloudinaryBackup,
    WebFolder,
    WebProxy,
    Gcs,
    AzureBlob,
    AkeneoPim,
)
from imagekitio.types.accounts.usage_get_response import UsageGetResponse
from imagekitio.types.beta.v2.file_upload_response import FileUploadResponse
from imagekitio.types.cache.invalidation_create_response import (
    InvalidationCreateResponse,
)
from imagekitio.types.custom_metadata_field import CustomMetadataField
from imagekitio.types.file_update_response import FileUpdateResponse
from imagekitio.types.files.bulk_add_tags_response import BulkAddTagsResponse
from imagekitio.types.files.bulk_delete_response import BulkDeleteResponse
from imagekitio.types.files.bulk_remove_ai_tags_response import BulkRemoveAITagsResponse
from imagekitio.types.files.bulk_remove_tags_response import BulkRemoveTagsResponse
from imagekitio.types.metadata import Metadata
from imagekitio.types.folders.job_get_response import JobGetResponse
from imagekitio.types.folder_copy_response import FolderCopyResponse
from imagekitio.types.folder_rename_response import FolderRenameResponse

ORIGIN_ACCOUNT_KEYS = (
    set(S3.model_fields.keys())
    .union(set(S3Compatible.model_fields.keys()))
    .union(set(CloudinaryBackup.model_fields.keys()))
    .union(set(WebFolder.model_fields.keys()))
    .union(set(WebProxy.model_fields.keys()))
    .union(set(Gcs.model_fields.keys()))
    .union(set(AzureBlob.model_fields.keys()))
    .union(set(AkeneoPim.model_fields.keys()))
)

TOOL_RESPONSE_MAP = {
    "list_assets": {
        "type": List[Union[File, Folder]],
        "keys": set(File.model_fields.keys()).union(set(Folder.model_fields.keys())),
    },
    "create_accounts_origins": {
        "type": Union[
            S3,
            S3Compatible,
            CloudinaryBackup,
            WebFolder,
            WebProxy,
            Gcs,
            AzureBlob,
            AkeneoPim,
        ],
        "keys": ORIGIN_ACCOUNT_KEYS,
    },
    "get_accounts_origins": {
        "type": Union[
            S3,
            S3Compatible,
            CloudinaryBackup,
            WebFolder,
            WebProxy,
            Gcs,
            AzureBlob,
            AkeneoPim,
        ],
        "keys": ORIGIN_ACCOUNT_KEYS,
    },
    "list_accounts_origins": {
        "type": List[
            Union[
                S3,
                S3Compatible,
                CloudinaryBackup,
                WebFolder,
                WebProxy,
                Gcs,
                AzureBlob,
                AkeneoPim,
            ]
        ],
        "keys": ORIGIN_ACCOUNT_KEYS,
    },
    "update_accounts_origins": {
        "type": List[
            Union[
                S3,
                S3Compatible,
                CloudinaryBackup,
                WebFolder,
                WebProxy,
                Gcs,
                AzureBlob,
                AkeneoPim,
            ]
        ],
        "keys": ORIGIN_ACCOUNT_KEYS,
    },
    "get_accounts_usage": {
        "type": UsageGetResponse,
        "keys": set(UsageGetResponse.model_fields.keys()),
    },
    "imagekit_generate_image": {
        "type": str,
        "keys": None,
    },
    "upload_v2_beta_files": {
        "type": FileUploadResponse,
        "keys": set(FileUploadResponse.model_fields.keys()),
    },
    "create_cache_invalidation": {
        "type": InvalidationCreateResponse,
        "keys": set(InvalidationCreateResponse.model_fields.keys()),
    },
    "get_cache_invalidation": {
        "type": InvalidationCreateResponse,
        "keys": set(InvalidationCreateResponse.model_fields.keys()),
    },
    "create_custom_metadata": {
        "type": CustomMetadataField,
        "keys": set(CustomMetadataField.model_fields.keys()),
    },
    "delete_custom_metadata": {
        "type": None,
        "keys": None,
    },
    "list_custom_metadata_fields": {
        "type": List[CustomMetadataField],
        "keys": set(CustomMetadataField.model_fields.keys()),
    },
    "update_custom_metadata_fields": {
        "type": CustomMetadataField,
        "keys": set(CustomMetadataField.model_fields.keys()),
    },
    "copy_file": {
        "type": None,
        "keys": None,
    },
    "delete_files": {
        "type": None,
        "keys": None,
    },
    "get_files": {
        "type": File,
        "keys": set(File.model_fields.keys()),
    },
    "move_files": {
        "type": None,
        "keys": None,
    },
    "rename_files": {
        "type": None,
        "keys": None,
    },
    "update_files": {
        "type": FileUpdateResponse,
        "keys": set(FileUpdateResponse.model_fields.keys()),
    },
    "upload_files": {
        "type": FileUploadResponse,
        "keys": set(FileUploadResponse.model_fields.keys()),
    },
    "add_tags_files_bulk": {
        "type": BulkAddTagsResponse,
        "keys": set(BulkAddTagsResponse.model_fields.keys()),
    },
    "delete_files_bulk": {
        "type": BulkDeleteResponse,
        "keys": set(BulkDeleteResponse.model_fields.keys()),
    },
    "remove_ai_tags_files_bulk": {
        "type": BulkRemoveAITagsResponse,
        "keys": set(BulkRemoveAITagsResponse.model_fields.keys()),
    },
    "remove_tags_files_bulk": {
        "type": BulkRemoveTagsResponse,
        "keys": set(BulkRemoveTagsResponse.model_fields.keys()),
    },
    "get_files_metadata": {
        "type": Metadata,
        "keys": set(Metadata.model_fields.keys()),
    },
    "get_from_url_files_metadata": {
        "type": Metadata,
        "keys": set(Metadata.model_fields.keys()),
    },
    "delete_files_versions": {
        "type": None,
        "keys": None,
    },
    "get_files_versions": {
        "type": File,
        "keys": set(File.model_fields.keys()),
    },
    "list_files_versions": {
        "type": List[File],
        "keys": set(File.model_fields.keys()),
    },
    "restore_files_versions": {
        "type": File,
        "keys": set(File.model_fields.keys()),
    },
    "get_folders_job": {
        "type": JobGetResponse,
        "keys": set(JobGetResponse.model_fields.keys()),
    },
    "copy_folders": {
        "type": FolderCopyResponse,
        "keys": set(FolderCopyResponse.model_fields.keys()),
    },
    "create_folders": {
        "type": None,
        "keys": None,
    },
    "delete_folders": {
        "type": None,
        "keys": None,
    },
    "move_folders": {
        "type": None,
        "keys": None,
    },
    "rename_folders": {
        "type": FolderRenameResponse,
        "keys": set(FolderRenameResponse.model_fields.keys()),
    },
    "get_dates": {
        "type": dict,
        "keys": set(
            [
                "local_date",
                "local_time",
                "local_datetime",
                "utc_date",
                "utc_time",
                "utc_datetime",
            ]
        ),
    },
    "search_docs": {"type": dict, "keys": None},
    "transformation_builder": {
        "type": str,
        "keys": None,
    },
}


def filter_response(
    response: Any,
    key_names: Optional[List[str]] = None,
    tool_name: Optional[str] = None,
) -> Any:
    if key_names is None:
        return response

    key_names = set(key_names)

    if tool_name and tool_name in TOOL_RESPONSE_MAP:
        expected_keys = TOOL_RESPONSE_MAP[tool_name]["keys"]

    keys_to_filter = key_names.union(expected_keys)
    if not keys_to_filter:
        return keys_to_filter

    if isinstance(response, list):
        filtered_list = []
        for item in response:
            if isinstance(item, dict):
                filtered_item = {k: v for k, v in item.items() if k in keys_to_filter}
                filtered_list.append(filtered_item)
            else:
                filtered_list.append(item)
        return filtered_list
    elif isinstance(response, dict):
        return {k: v for k, v in response.items() if k in keys_to_filter}
    else:
        return response
