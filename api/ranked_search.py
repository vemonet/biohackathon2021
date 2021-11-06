from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.responses import JSONResponse
from typing import List, Optional

router = APIRouter()


@router.get("/search", name="Ranked search",
    description="Ranked search of SPARQL endpoints",
    response_model=List[dict],
)            
def ranked_search(search: str = "novel coronavirus") -> List[dict]:

    mock_results = [
        {"example": "TO BE IMPLEMENTED"},
        {"url": "https://bio2rdf.org/sparql", "score": 42}
    ]

    return JSONResponse(mock_results)

