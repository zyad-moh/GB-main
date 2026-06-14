from fastapi import APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import traceback

from pydantic import BaseModel
job_router=APIRouter( # prefix for end point
   prefix="/api/v1",
   tags=["api_v1","job"],
)


# Adzuna
APP_ID = "e58471d6"
APP_KEY = "a610ceeedde21bbf7f86e4b1e33dd1c3"

# JSearch
JSEARCH_API_KEY = "ak_sgvu8n42inp74j2sccbmzmr6mljvbkffg78abn5isftswet"

JSEARCH_COUNTRIES = [
    "eg",  # Egypt
    "sa",  # Saudi Arabia
    "ae",  # UAE
    "qa",  # Qatar
    "kw",  # Kuwait
    "bh",  # Bahrain
    "om",  # Oman
]


def remove_null_fields(obj: dict):
    return {
        key: value
        for key, value in obj.items()
        if value is not None
    }
class job_search(BaseModel):
    what: str = "developer"
    where : str = "london"
    country : str =  "gb"
    page: int = 1

@job_router.post("/jobs")
async def get_jobs(payload: job_search):
    what = payload.what
    where = payload.where
    country = payload.country
    page = payload.page
    try:

        if not what and not where:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "fail",
                    "message": "Missing search params"
                }
            )

        final_country = country.lower()
        final_page = page

        # ==========================
        # JSearch Countries
        # ==========================
        if final_country in JSEARCH_COUNTRIES:

            query = f"{what or 'developer'} {where or ''}".strip()

            async with httpx.AsyncClient(timeout=30.0) as client:
                print("Before request")
                response = await client.get(
                    "https://api.openwebninja.com/jsearch/search-v2",
                    params={
                        "query": query,
                        "country": final_country,
                        "num_pages": 1,
                    },
                    headers={
                        "x-api-key": JSEARCH_API_KEY
                    }
                )
            print("after request")

            response.raise_for_status()

            data = response.json()

            jobs = [
                remove_null_fields(job)
                for job in data.get("data", {}).get("jobs", [])
            ]

            return {
                "status": "success",
                "provider": "jsearch",
                "search": {
                    "what": what,
                    "where": where,
                    "country": final_country,
                },
                "results": len(jobs),
                "data": jobs,
            }

        # ==========================
        # Adzuna Countries
        # ==========================
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 10,
            "what": what or "developer",
        }

        if where:
            params["where"] = where

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.adzuna.com/v1/api/jobs/{final_country}/search/{final_page}",
                params=params
            )

        response.raise_for_status()

        data = response.json()

        return {
            "status": "success",
            "provider": "adzuna",
            "search": {
                "what": what,
                "where": where,
                "country": final_country,
            },
            "page": final_page,
            "results": len(data.get("results", [])),
            "data": data.get("results", []),
        }

    except httpx.HTTPStatusError as e:

        print("==========================")
        print("ERROR STATUS:")
        print(e.response.status_code)

        print("ERROR DATA:")
        try:
            print(e.response.json())
        except Exception:
            print(e.response.text)

        print("ERROR MESSAGE:")
        print(str(e))
        print("==========================")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )

    except Exception as e:
        print(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        print("==========================")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )


