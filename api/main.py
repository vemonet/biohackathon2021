from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field


app = FastAPI(
    title='Ranking datasets',
    description="""API to rank datasets for the [BioHackathon 2021](https://github.com/elixir-europe/biohackathon-projects-2021/tree/main/projects/26)""",
    license_info = {
        "name": "MIT license",
        "url": "https://opensource.org/licenses/MIT"
    },
    contact = {
        "name": "Vincent Emonet",
        "email": "vincent.emonet@gmail.com",
        "url": "https://github.com/vemonet",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RankedDataset(BaseModel):
    url: str = Field(...)
    score: int = Field(...)
    # id: str = Field(..., alias="@id")
    # context: str = Field(..., alias="@context")


@app.get("/search", name="Ranked search",
    description="Ranked search of SPARQL endpoints",
    response_model=List[RankedDataset],
)            
async def ranked_search(search: str = "novel coronavirus") -> List[RankedDataset]:

    mock_results = [
        {"url": "https://bio2rdf.org/sparql", "score": 42}
    ]

    return JSONResponse(mock_results)