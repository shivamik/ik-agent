from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders.job",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/bulkJobs/{job_id}",
    "operation_id": "bulk-job-status",
}


def _serialize_job_status(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_folders_job(
    *,
    job_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve status of a bulk job (copy/move/rename folder).

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.job.get(job_id)
    response = _serialize_job_status(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_folders_job",
    description=(
        "Retrieve the status of an ImageKit bulk folder job such as copy, "
        "move, or rename."
    ),
)
async def get_folders_job_tool(
    job_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Retrieve the status of a bulk folder operation.

    This tool returns the current status and metadata for an asynchronous
    bulk job initiated by folder copy, move, or rename operations.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        job_id: Unique identifier of the bulk job to query.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.status`

    Returns:
        A dictionary containing bulk job details, typically:
            - jobId: Unique identifier of the bulk job.
            - status: Current status of the job (`Pending` or `Completed`).
            - type: Type of bulk job (e.g. `COPY_FOLDER`, `MOVE_FOLDER`,
              `RENAME_FOLDER`).
            - purgeRequestId: Identifier of the purge request, present only
              for rename operations with cache purging enabled.
    """
    return await get_folders_job(
        job_id=job_id,
        filter_spec=filter_spec,
    )
