"""
Dataset endpoints.

Generic endpoint handler that works with any dataset type.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from peskas_api.api.deps import AuthenticatedUser, GCS, Query
from peskas_api.core.exceptions import DataNotFoundError
from peskas_api.models.params import DatasetQueryParams
from peskas_api.models.enums import ResponseFormat
from peskas_api.schema.dataset_config import get_dataset_type, get_all_dataset_types

router = APIRouter(tags=["Datasets"])


def create_dataset_endpoint(dataset_type_name: str):
    """
    Factory function to create dataset endpoints.

    This enables dynamic endpoint creation based on dataset config.
    """
    dataset_config = get_dataset_type(dataset_type_name)
    if dataset_config is None:
        raise ValueError(f"Unknown dataset type: {dataset_type_name}")

    async def get_dataset(
        _auth: AuthenticatedUser,
        gcs: GCS,
        query_svc: Query,
        params: DatasetQueryParams = Depends(),
    ):
        """
        Retrieve dataset records.

        Downloads the relevant Parquet file from GCS, applies filters,
        and streams the result as CSV or JSON.
        """
        # Download parquet file
        try:
            parquet_path = gcs.download_parquet(
                country=params.country,
                status=params.status,
            )
        except DataNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Resolve columns
        try:
            columns = params.get_columns(dataset_type_name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Query and respond
        try:
            if params.format == ResponseFormat.JSON:
                records = query_svc.get_as_records(
                    parquet_path,
                    date_column=dataset_config.date_column,
                    date_from=params.date_from,
                    date_to=params.date_to,
                    gaul_1=params.gaul_1,
                    catch_taxon=params.catch_taxon,
                    columns=columns,
                    limit=params.limit,
                )
                return JSONResponse(content={"data": records})
            else:
                # Stream CSV
                def generate():
                    yield from query_svc.stream_csv(
                        parquet_path,
                        date_column=dataset_config.date_column,
                        date_from=params.date_from,
                        date_to=params.date_to,
                        gaul_1=params.gaul_1,
                        catch_taxon=params.catch_taxon,
                        columns=columns,
                        limit=params.limit,
                    )

                filename = f"{dataset_type_name}_{params.country}_{params.status.value}.csv"
                return StreamingResponse(
                    generate(),
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"},
                )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return get_dataset


# Dynamically create endpoints for each dataset type
for ds_type in get_all_dataset_types():
    endpoint_func = create_dataset_endpoint(ds_type.name)
    endpoint_func.__doc__ = f"""
    Retrieve {ds_type.description}.

    **Dataset type**: `{ds_type.name}`

    **GCS path pattern**: `{{country}}/{{status}}/` (latest versioned file)
    """

    router.add_api_route(
        f"/{ds_type.endpoint}",
        endpoint_func,
        methods=["GET"],
        name=f"get_{ds_type.name}",
        summary=f"Get {ds_type.name} data",
    )
