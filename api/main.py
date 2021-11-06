from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field

from SPARQLWrapper import SPARQLWrapper, TURTLE, XML, JSON

PREFIXES = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX bl: <http://w3id.org/biolink/vocab/>
PREFIX dctypes: <http://purl.org/dc/dcmitype/>
PREFIX idot: <http://identifiers.org/idot/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX void-ext: <http://ldf.fi/void-ext#>"""

METADATA_ENDPOINT = 'https://graphdb.dumontierlab.com/repositories/shapes-registry'

app = FastAPI(
    title='Ranking datasets',
    description="""API to rank datasets for the [BioHackathon 2021](https://github.com/elixir-europe/biohackathon-projects-2021/tree/main/projects/26).

[Source code](https://github.com/vemonet/biohackathon2021)    
""",
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
    tags=["Ranked Search"],
    response_model=List[RankedDataset],
)            
def ranked_search(search: str = "novel coronavirus") -> List[RankedDataset]:

    mock_results = [
        {"url": "https://bio2rdf.org/sparql", "score": 42}
    ]

    return JSONResponse(mock_results)



@app.get("/datasets", name="List datasets available for Ranked Search",
    description="List the datasets available for Ranked Search",
    tags=["Ranked Search"],
    response_model=List[dict],
)            
def list_datasets() -> List[dict]:

    list_endpoints_query = PREFIXES + """SELECT DISTINCT ?endpoint (count(distinct ?graph) AS ?datasets_graph_count)
    WHERE {
        GRAPH ?endpoint {
            # ?graph a void:Dataset .
            ?graph void:propertyPartition ?propertyPartition . 
            # ?propertyPartition void:property ?predicate ;
        }
    } GROUP BY ?endpoint ORDER BY DESC(?datasets_graph_count)
    """

    sparql = SPARQLWrapper(METADATA_ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(list_endpoints_query)
    sparqlwrapper_results = sparql.query().convert()
    sparql_results = sparqlwrapper_results["results"]["bindings"]

    dataset_list = []
    for result in sparql_results:
        dataset_list.append({
            'url': result['endpoint']['value'],
            'graph_count': result['datasets_graph_count']['value'],
        })

    return JSONResponse(dataset_list)



@app.get("/get-dataset-classes", name="Get dataset classes",
    description="Retrieve the list of classes in a SPARQL endpoint indexed in Shapes of You",
    tags=["Ranked Search"],
    response_model=dict,
)            
def get_dataset_classes(dataset: str = "https://bio2rdf.org/sparql") -> dict:
    results = {'classes': [], 'predicates': []}
    sparql = SPARQLWrapper(METADATA_ENDPOINT)
    sparql.setReturnFormat(JSON)

    get_properties_query = PREFIXES + """
    SELECT DISTINCT ?predicate (SUM(?partitionTriples) AS ?triplesCount)
    WHERE {
    GRAPH <""" + dataset + """> {
        ?graph void:propertyPartition ?propertyPartition . 
        ?propertyPartition void:property ?predicate .
        ?propertyPartition void:triples ?partitionTriples .
    } } GROUP BY ?predicate ORDER BY DESC(?triplesCount)"""

    sparql.setQuery(get_properties_query)
    sparqlwrapper_results = sparql.query().convert()
    sparql_results = sparqlwrapper_results["results"]["bindings"]

    for result in sparql_results:
        results['predicates'].append({
            'uri': result['predicate']['value'],
            'triples_count': result['triplesCount']['value'],
        })


    get_classes_query = PREFIXES + """
    SELECT DISTINCT ?class (SUM(?partitionCount) AS ?triplesCount)
    WHERE {
    GRAPH <""" + dataset + """> {
        ?graph void:propertyPartition ?propertyPartition . 
        ?propertyPartition void:property ?predicate .
        {
            ?propertyPartition void:classPartition [
            void:class ?class ;
            void:distinctSubjects ?partitionCount ;
            ] .
        } UNION {
            ?propertyPartition void-ext:objectClassPartition [
                void:class ?class ;
                void:distinctObjects ?partitionCount ;
            ] .
        }
    }
    } GROUP BY ?class ORDER BY DESC(?triplesCount)
    """

    sparql.setQuery(get_classes_query)
    sparqlwrapper_results = sparql.query().convert()
    sparql_results = sparqlwrapper_results["results"]["bindings"]

    for result in sparql_results:
        results['classes'].append({
            'uri': result['class']['value'],
            'triples_count': result['triplesCount']['value'],
        })

    return JSONResponse(results)



# detailed_metadata_query = PREFIXES + """
# SELECT DISTINCT ?endpoint ?graph ?subjectCount ?subject ?predicate ?objectCount ?object
# WHERE {
# GRAPH ?endpoint {
#     # ?graph a void:Dataset .
#     ?graph void:propertyPartition ?propertyPartition . 
#     ?propertyPartition void:property ?predicate ;
#     void:classPartition [
#         void:class ?subject ;
#         void:distinctSubjects ?subjectCount ;
#     ] .
    
#     OPTIONAL {
#     ?propertyPartition void-ext:objectClassPartition [
#     void:class ?object ;
#     void:distinctObjects ?objectCount ;
#     ]
#     }
# }
# # FILTER (?sparql_endpoint = ?_sparqlendpoint_iri)
# } ORDER BY DESC(?subjectCount)
# """
