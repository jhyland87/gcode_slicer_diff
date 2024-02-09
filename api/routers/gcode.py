from fastapi import FastAPI, Query, status, Response, Depends, Request, APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse, ORJSONResponse, UJSONResponse, FileResponse
from pathlib import Path
import os

import sys
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

sys.path.insert(1, '/Users/jhyland/Documents/scripts/python/gcode_slicer_diff')

import gcode_utils
from utils import helpers

router = APIRouter(
    prefix="/gcode",
    tags=["Gcode parser functions"]
)

# This should be the root of the gcode folder
gcode_base = os.path.join(helpers.get_project_root(), 'data/gcode-samples/')

dir_list = os.listdir(gcode_base)

# http://127.0.0.1:8000/compare/?file=foo&file=bar
@router.get("/")
def compare_index():
    # /compare-files?file=foo&file=bar
    return { "Hello": "World"}


@router.get("/list")
def list_gcode_files():
    return dir_list

@router.get("/{file}/parse-settings",  status_code=status.HTTP_200_OK)
async def parse_gcode_settings(file: str, response: Response):
    #print(f"q: {q}")
    # http://127.0.0.1:8000/gcode/prusa-sliced.gcode/parse-settings
    footer = await gcode_utils.read_footer(filename=gcode_base + file)
    return { 'file': file }

@router.get("/{file}/footer",  status_code=status.HTTP_200_OK)
async def get_gcode_footer(file: str, response: Response):
    '''
    Example: http://127.0.0.1:8000/gcode/prusa-sliced.gcode/footer
        Retrieves the raw footer data from prusa-sliced.gcode
    '''
    data_raw = await gcode_utils.read_footer(filename=gcode_base + file)
    return { 'result': data_raw }


@router.get("/{file}/footer/parse",  status_code=status.HTTP_200_OK)
async def parse_gcode_footer(file: str, response: Response, cast: bool = False):
    '''
    Example: http://127.0.0.1:8000/gcode/prusa-sliced.gcode/footer/parse
        Retrieves the footer data from prusa-sliced.gcode and parses it, returning
        a dictionary of the settings
    '''
    data_raw = await gcode_utils.read_footer(filename=gcode_base + file)
    footer_parsed = gcode_utils.parse_footer(data=data_raw, cast=cast)
    return { 'result': footer_parsed }


@router.get("/{file}/footer/size/{size}",  status_code=status.HTTP_200_OK)
async def get_gcode_footer_size(file: str, size: int, response: Response):
    '''
    Example: http://127.0.0.1:8000/gcode/prusa-sliced.gcode/footer/size/524288
        Retrieves the last 524 mb of raw footer data from prusa-sliced.gcode (524 * 1024 = 524288)
    '''
    data_raw = await gcode_utils.read_footer(filename=gcode_base + file, read_size=size)

    # http://127.0.0.1:8000/gcode/footer/prusa-sliced.gcode/327680
    return { 'result': data_raw }


@router.get("/{file}/header",  status_code=status.HTTP_200_OK)
async def get_gcode_header(file: str, response: Response):
    '''
    Example: http://127.0.0.1:8000/gcode/prusa-sliced.gcode/header
        Retrieves the raw header data from prusa-sliced.gcode
    '''
    data_raw = await gcode_utils.read_header(filename=gcode_base + file)
    return { 'result': data_raw }


@router.get("/{file}/header/parse",  status_code=status.HTTP_200_OK)
async def parse_gcode_header(file: str, response: Response, cast: bool = False):
    '''
    Example: http://127.0.0.1:8000/gcode/prusa-sliced.gcode/header/parse
        Retrieves the header data from prusa-sliced.gcode and parses it, returning
        a dictionary of the settings
    '''
    data_raw = await gcode_utils.read_header(filename=gcode_base + file)
    data_parsed = gcode_utils.parse_header(data=data_raw, cast=cast)
    return { 'result': data_parsed }



@router.get("/compare/{right}/{left}",  status_code=status.HTTP_200_OK)
async def compare_gcode_settings(right: str, left: str, response: Response, cast: bool = False ):
    # http://127.0.0.1:8000/gcode/compare/prusa-sliced.gcode/prusa-sliced-2.gcode
    # http://127.0.0.1:8000/gcode/compare/prusa-sliced.gcode/prusa-sliced-2.gcode?cast=true
    
    if right == left:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"error": f"File {right} was given for both the right and left filename. Files must be unique"})

    diff = await gcode_utils.diff_slicer_data(left=gcode_base + left, right=gcode_base + right, cast=cast)

    result = {
        'left': {
            'file': left,
            'diff': diff['left']
        },
        'right': {
            'file': right,
            'diff': diff['right']
        }
    }
    
    return result

