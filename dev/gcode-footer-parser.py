import asyncio, os, json, sys
from fastapi import FastAPI, Query, status, Response, Depends, Request, APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse, ORJSONResponse, UJSONResponse, FileResponse
from pathlib import Path

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


project_root = str(Path(__file__).parent.parent)

sys.path.insert(1, project_root)


import gcode_utils
from utils import helpers


async def parse_file(file, cast = True):
    data_raw = await gcode_utils.read_footer(filename=file)
    footer_parsed = gcode_utils.parse_footer(data=data_raw, cast=cast)
    return footer_parsed



parsed_settings = asyncio.run(parse_file(project_root + '/data/gcode-samples/prusa-sliced.gcode'))
print(json.dumps(gcode_utils.sort_dict(parsed_settings), indent=2))