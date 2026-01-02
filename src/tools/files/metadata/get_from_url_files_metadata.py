from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.metadata",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/metadata",
    "operation_id": "get-metadata-from-url",
}


def _serialize_metadata(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_from_url_files_metadata(
    *,
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve metadata (EXIF, pHash, etc.) for an accessible URL.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.metadata.get_from_url(
        url=url,
    )
    response = _serialize_metadata(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_from_url_files_metadata",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nGet image EXIF, pHash, and other metadata from ImageKit.io powered remote URL using this API.\n\n\n# Response Schema\n```json\n{\n  $ref: '#/$defs/metadata',\n  $defs: {\n    metadata: {\n      type: 'object',\n      description: 'JSON object containing metadata.',\n      properties: {\n        audioCodec: {\n          type: 'string',\n          description: 'The audio codec used in the video (only for video).'\n        },\n        bitRate: {\n          type: 'integer',\n          description: 'The bit rate of the video in kbps (only for video).'\n        },\n        density: {\n          type: 'integer',\n          description: 'The density of the image in DPI.'\n        },\n        duration: {\n          type: 'integer',\n          description: 'The duration of the video in seconds (only for video).'\n        },\n        exif: {\n          type: 'object',\n          properties: {\n            exif: {\n              type: 'object',\n              description: 'Object containing Exif details.',\n              properties: {\n                ApertureValue: {\n                  type: 'number'\n                },\n                ColorSpace: {\n                  type: 'integer'\n                },\n                CreateDate: {\n                  type: 'string'\n                },\n                CustomRendered: {\n                  type: 'integer'\n                },\n                DateTimeOriginal: {\n                  type: 'string'\n                },\n                ExifImageHeight: {\n                  type: 'integer'\n                },\n                ExifImageWidth: {\n                  type: 'integer'\n                },\n                ExifVersion: {\n                  type: 'string'\n                },\n                ExposureCompensation: {\n                  type: 'number'\n                },\n                ExposureMode: {\n                  type: 'integer'\n                },\n                ExposureProgram: {\n                  type: 'integer'\n                },\n                ExposureTime: {\n                  type: 'number'\n                },\n                Flash: {\n                  type: 'integer'\n                },\n                FlashpixVersion: {\n                  type: 'string'\n                },\n                FNumber: {\n                  type: 'number'\n                },\n                FocalLength: {\n                  type: 'integer'\n                },\n                FocalPlaneResolutionUnit: {\n                  type: 'integer'\n                },\n                FocalPlaneXResolution: {\n                  type: 'number'\n                },\n                FocalPlaneYResolution: {\n                  type: 'number'\n                },\n                InteropOffset: {\n                  type: 'integer'\n                },\n                ISO: {\n                  type: 'integer'\n                },\n                MeteringMode: {\n                  type: 'integer'\n                },\n                SceneCaptureType: {\n                  type: 'integer'\n                },\n                ShutterSpeedValue: {\n                  type: 'number'\n                },\n                SubSecTime: {\n                  type: 'string'\n                },\n                WhiteBalance: {\n                  type: 'integer'\n                }\n              }\n            },\n            gps: {\n              type: 'object',\n              description: 'Object containing GPS information.',\n              properties: {\n                GPSVersionID: {\n                  type: 'array',\n                  items: {\n                    type: 'integer'\n                  }\n                }\n              }\n            },\n            image: {\n              type: 'object',\n              description: 'Object containing EXIF image information.',\n              properties: {\n                ExifOffset: {\n                  type: 'integer'\n                },\n                GPSInfo: {\n                  type: 'integer'\n                },\n                Make: {\n                  type: 'string'\n                },\n                Model: {\n                  type: 'string'\n                },\n                ModifyDate: {\n                  type: 'string'\n                },\n                Orientation: {\n                  type: 'integer'\n                },\n                ResolutionUnit: {\n                  type: 'integer'\n                },\n                Software: {\n                  type: 'string'\n                },\n                XResolution: {\n                  type: 'integer'\n                },\n                YCbCrPositioning: {\n                  type: 'integer'\n                },\n                YResolution: {\n                  type: 'integer'\n                }\n              }\n            },\n            interoperability: {\n              type: 'object',\n              description: 'JSON object.',\n              properties: {\n                InteropIndex: {\n                  type: 'string'\n                },\n                InteropVersion: {\n                  type: 'string'\n                }\n              }\n            },\n            makernote: {\n              type: 'object',\n              additionalProperties: true\n            },\n            thumbnail: {\n              type: 'object',\n              description: 'Object containing Thumbnail information.',\n              properties: {\n                Compression: {\n                  type: 'integer'\n                },\n                ResolutionUnit: {\n                  type: 'integer'\n                },\n                ThumbnailLength: {\n                  type: 'integer'\n                },\n                ThumbnailOffset: {\n                  type: 'integer'\n                },\n                XResolution: {\n                  type: 'integer'\n                },\n                YResolution: {\n                  type: 'integer'\n                }\n              }\n            }\n          }\n        },\n        format: {\n          type: 'string',\n          description: 'The format of the file (e.g., \\'jpg\\', \\'mp4\\').'\n        },\n        hasColorProfile: {\n          type: 'boolean',\n          description: 'Indicates if the image has a color profile.'\n        },\n        hasTransparency: {\n          type: 'boolean',\n          description: 'Indicates if the image contains transparent areas.'\n        },\n        height: {\n          type: 'integer',\n          description: 'The height of the image or video in pixels.'\n        },\n        pHash: {\n          type: 'string',\n          description: 'Perceptual hash of the image.'\n        },\n        quality: {\n          type: 'integer',\n          description: 'The quality indicator of the image.'\n        },\n        size: {\n          type: 'integer',\n          description: 'The file size in bytes.'\n        },\n        videoCodec: {\n          type: 'string',\n          description: 'The video codec used in the video (only for video).'\n        },\n        width: {\n          type: 'integer',\n          description: 'The width of the image or video in pixels.'\n        }\n      }\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Should be a valid file URL. It should be accessible using your ImageKit.io account.\n",
                },
                "filter_spec": {
                    "type": "string",
                    "title": "filter_spec",
                    "description": 'A filter_spec to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [glomdocumentation](http://glom.readthedocs.io/).',
                },
            },
            "required": ["url"],
        }
    },
)
async def get_from_url_files_metadata_tool(
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve metadata (EXIF, pHash, etc.) for an accessible URL.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await get_from_url_files_metadata(
        url=url,
        filter_spec=filter_spec,
    )
