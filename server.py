
from fastapi import FastAPI, Query, status, Response, Depends, Request
from fastapi.responses import PlainTextResponse, JSONResponse, ORJSONResponse, UJSONResponse, FileResponse
from enum import Enum
import json
import os



from api.routers import utils, gcode

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    Set,
    Optional,
    Union,
    Dict,
    List,
    Annotated,
    Type,
)





app = FastAPI()

app.include_router(gcode)
app.include_router(utils)


# Using FastAPI instance
@app.get("/")
def get_all_urls():

    return [{
        "path": route.path, 
        "name": route.name, 
        "methods": route.methods if route.methods else None
    } for route in app.routes]