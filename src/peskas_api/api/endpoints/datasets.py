"""
Dataset endpoints.

`/data/landings` serves one row per catch with the full filter set;
`/data/district-months` serves one row per district and month, filtered by
place and month only. Both read the newest parquet file of their dataset.
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query as QueryParam
from fastapi.responses import StreamingResponse, JSONResponse

from peskas_api.api.deps import AuthenticatedUser, GCS, Query
from peskas_api.core.exceptions import DataNotFoundError
from peskas_api.models.params import DatasetQueryParams, DistrictMonthsQueryParams
from peskas_api.models.enums import ResponseFormat
from peskas_api.schema.dataset_config import get_dataset_type
from peskas_api.services.query import QueryService

router = APIRouter(tags=["Datasets"])


def _query_response(
    query_svc: QueryService,
    parquet_path: Path,
    params: DatasetQueryParams | DistrictMonthsQueryParams,
    date_column: str,
    filename: str,
    **filters,
):
    """Filter the parquet file and return it as JSON or as a CSV download."""
    query_args = dict(
        date_column=date_column,
        date_from=params.date_from,
        date_to=params.date_to,
        gaul_1=params.gaul_1,
        gaul_2=params.gaul_2,
        limit=params.limit,
        **filters,
    )
    try:
        if params.format == ResponseFormat.JSON:
            records = query_svc.get_as_records(parquet_path, **query_args)
            return JSONResponse(content={"data": records})

        # Stream CSV
        def generate():
            yield from query_svc.stream_csv(parquet_path, **query_args)

        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
        params: Annotated[DatasetQueryParams, QueryParam()],
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

        return _query_response(
            query_svc,
            parquet_path,
            params,
            date_column=dataset_config.date_column,
            filename=f"{dataset_type_name}_{params.country}_{params.status.value}.csv",
            catch_taxon=params.get_catch_taxa(),
            survey_id=params.survey_id,
            columns=columns,
        )

    return get_dataset


# Landings take the full filter set (status, species, survey, scope).
ds_type = get_dataset_type("landings")
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


@router.get(
    "/district-months",
    name="get_district-months",
    summary="Get district-months data",
)
async def get_district_months(
    _auth: AuthenticatedUser,
    gcs: GCS,
    query_svc: Query,
    params: Annotated[DistrictMonthsQueryParams, QueryParam()],
):
    """
    Retrieve monthly figures per district.

    One row per district (by GAUL code) and month: averages over the landings
    recorded, and the whole fleet's estimated trips, catch and revenue by the
    GPS tracker and FAO ARTFISH methods, as the country dashboards show them.
    Validated data only. `/metadata/district-months` describes every column.

    **Dataset type**: `district-months`

    **GCS path pattern**: `{country}/aggregated/` (latest versioned file)
    """
    dataset_config = get_dataset_type("district-months")
    try:
        parquet_path = gcs.download_parquet(
            country=params.country,
            dataset=dataset_config.name,
        )
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return _query_response(
        query_svc,
        parquet_path,
        params,
        date_column=dataset_config.date_column,
        filename=f"district-months_{params.country}.csv",
    )
