import os, re, asyncio
import aiofiles
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Dict,
    List,
    Tuple,
    TypedDict,
    Type,
    TypeAlias
)
from codecs import decode
from utils import helpers
#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

READ_SIZE= 512 * 1024

READ_SIZE = 320 * 1024

async def read_file(filename) -> Dict[str, bytes]:
    size = os.path.getsize(filename)

    res = dict( filename=filename )
    async with aiofiles.open(filename, mode='rb') as f:
        res['header'] = await f.read(READ_SIZE)
        await f.seek(size - READ_SIZE)
        res['footer'] = await f.read(READ_SIZE)

        return res

async def read_header(filename: str, read_size: int=READ_SIZE) -> str:
    async with aiofiles.open(filename, mode='rb') as f:
        data = await f.read(READ_SIZE)

        return data.decode("utf-8")

async def read_footer(filename: str, read_size: int=READ_SIZE) -> str:
    """
    Read a specific amount of data from the end of the file

    Parameter
    ---------
    filename: str
        Filename to retrieve raw footer data from

    read_size: int
        Amount of data in bytes to retrieve from the file

    Returns
    -------
    (str): 
        The requested data from the footer
    """

    size = os.path.getsize(filename)

    async with aiofiles.open(filename, mode='rb') as f:
        await f.seek(size - read_size)
        data = await f.read(read_size)

        return data.decode("utf-8")

def read_files_async(filenames: list) -> list:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        asyncio.gather(
            #*[read_header(filename) for filename in filenames],

            *(read_file(filename) for filename in filenames),

            #[{'data': read_header(filename)} for filename in filenames],
        ))
        #asyncio.gather(*[{ 'file': filename, 'data': read_file(filename)} for filename in filenames]))

def diff_data(left:Dict, right:Dict) -> Dict:
    """
    Diff two dictionary data objects

    Parameter
    ---------
    left: Dict[str, str]
        Dictionary with the key/values for the settings in the gcode data

    right: Dict[str, str]
        Same thing as left, but for a different file

    Returns: Dict
        left: Dict[str, str]: Values in the left dict that differ from the right

    Returns
    -------
    left (Dict[str, str]):
        Settings that are different than the value on the right side

    right (Dict[str, str]):
        Settings that are different than the value on the left side

    keys (list[str]):
        Unique list of setting names that were found in the diff results


    Dict[left|right, Dict[setting: str, value: str]]
    """

    result = {}

    left_set = set(left.items())
    right_set = set(right.items())

    result['left'] = left_set - right_set
    result['right'] = right_set - left_set

    updated_keys = list(result['left'])

    updated_keys.extend(list(result['right']))

    result['left'] = sort_dict(dict(result['left']))
    result['right'] = sort_dict(dict(result['right']))
    result['keys'] = sorted(list(dict(updated_keys)))

    return result

def sort_dict(data: Dict ) -> Dict:
    return dict(sorted(data.items()))

def parse_line(line: str, delimiter: str='=', cast: bool = False) -> List:
    """
    Parse a single line to try to retrieve a key and value

    Parameter
    ---------
    line: str
        Single line from the gcode file

    delimiter: str
        Delimiter separating the key and value in the gcode comments.

    Returns:
        (List) [str, str]: Returns a list with the key and value 
    """

    if not line:
        return

    #m = re.match(r"([a-zA-Z0-9_-]+) = (.+)$", line)

    m = re.match(f"^[\s;]*([a-zA-Z0-9_\s-]+) {delimiter} (.+)$", line)

    # If no matches are found, then  abort
    if not m: return None

    # If there was a key and value found, return them
    if m[1] and m[2]: 
        return [m[1], helpers.cast(m[2]) if cast is True else m[2]]
 
def is_comment(line: str) -> bool:
    m = re.match('^\s*;\s*', line)
    return m is not None

def parse_header(data: str, cast: bool = False) -> Dict:
    """
    Parse raw footer data into a dictionary

    Parameter
    ---------
    data (str):
        Footer data (from read_footer)

    Returns (Dict[str, str]):
    --------
        Dictionary with the key and values from the footer that was parsed
    """

    # print([s for s in s_hyphen.split('-') if s])

    # Split into lines.. 
    data_split = data.split('\n')

    config_rows=data_split

    # Filter out non-comment lines..
    data_rows = filter(lambda line: is_comment(line), config_rows)

    # Strip out the comment chars..
    data_rows = [re.sub(r"^;\s?", '', line) for line in data_rows]

    # Parse each line, and cast the values if requested
    data_list = [parse_line(d, cast=cast) for d in data_rows]

    # Get rid of rows without a val

    res = []

    for d in data_list:
        if not d:  continue
        if len(d) != 2: continue

        res.append(d)

    data_list = res

    return dict(data_list)   

def parse_footer(data: str, cast: bool = False) -> Dict:
    """
    Parse raw footer data into a dictionary

    Parameter
    ---------
    data (str):
        Footer data (from read_footer)

    Returns (Dict[str, str]):
    --------
        Dictionary with the key and values from the footer that was parsed
    """

    # print([s for s in s_hyphen.split('-') if s])

    # Split into lines.. 
    data_rows = data.split('\n')

    config_rows=[]

    in_config = False

    for row in data_rows:
        if in_config is False:
            if 'prusaslicer_config = begin' in row:
                in_config = True;
            continue

        if in_config is True:
            if 'prusaslicer_config = end' in row:
                in_config = False;
                break

            config_rows.append(row)
            continue

    # Filter out non-comment lines..
    data_rows = filter(lambda line: re.match('^;', line), config_rows)

    # Strip out the comment chars..
    data_rows = [re.sub(r"^;\s?", '', line) for line in data_rows]

    # Parse each line, and cast the values if requested
    data_list = [parse_line(d, cast=cast) for d in data_rows]

    # Get rid of rows without a val

    res = []

    for d in data_list:
        if not d:  continue
        if len(d) != 2: continue

        res.append(d)

    data_list = res

    return dict(data_list)

async def diff_slicer_data(left: str, right: str, cast: bool = False) -> Dict:
    left_footer = await read_footer(left)
    right_footer = await read_footer(right)

    left_data = parse_footer(data=left_footer, cast=cast)
    right_data = parse_footer(data=right_footer, cast=cast)
   

    return diff_data(dict(left_data), dict(right_data))


