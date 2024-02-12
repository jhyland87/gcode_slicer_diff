import os, re, json, sys
from enum import Enum
from pathlib import Path
#from contextlib import contextmanager
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


project_root = str(Path(__file__).parent.parent)

sys.path.insert(1, project_root)

import gcode_utils
from utils import helpers


# class syntax
IterStatus = Enum('IterStatus', ['NONE', 'BEGIN', 'END', 'ERROR'])

def parse_line(line: str, delimiter: str='=', cast: bool = False) -> List:
    if not line:
        return

    #m = re.match(r"([a-zA-Z0-9_-]+) = (.+)$", line)

    m = re.match(f"^[\s;]*([a-zA-Z0-9_\s-]+) {delimiter} (.+)$", line)

    # If no matches are found, then  abort
    if not m: return None

    # If there was a key and value found, return them
    if m[1] and m[2]: 
        return { m[1]: helpers.cast(m[2]) }
 
def is_comment(line: str) -> bool:
    m = re.match('^\s*;\s*', line)
    return m is not None

def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, 'rb') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            # remove file's last "\n" if it exists, only for the first buffer
            if remaining_size == file_size and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]
            remaining_size -= buf_size
            lines = buffer.split('\n'.encode())
            # append last chunk's segment to this chunk's last line
            if segment is not None:
                lines[-1] += segment
            segment = lines[0]
            lines = lines[1:]
            # yield lines in this chunk except the segment
            for line in reversed(lines):
                # only decode on a parsed line, to avoid utf-8 decode error
                yield line.decode()
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment.decode()


def handle_line(line):
    parsed_line = parse_line(line=line.decode(), cast=True)
        
    if parsed_line is None:
        return IterStatus.NONE
    
    if type(parsed_line) is not dict:
        raise TypeError(f'Invalid data type returned from parser: {type(parsed_line)}, expected dict')

    #if len(parsed_line) != 2:
    #    raise ValueError(f'Invalid list returned from parser: {parsed_line}')

    if 'prusaslicer_config' in parsed_line:
        if parsed_line['prusaslicer_config'] == 'end':
            return IterStatus.BEGIN

        if parsed_line['prusaslicer_config'] == 'begin':
            return IterStatus.END

        raise ValueError(f'Encountered invalid value for prusaslicer_config = {parsed_line["prusaslicer_config"]}, expecting either "begin" or "end"')

    return parsed_line

def reverse_gcode_reader(filename, buf_size=8192):
    in_config = False
    is_completed = False
    settings_count = 0
    gcode_settings = {}


    try:
        """A generator that returns the lines of a file in reverse order"""
        #with closing(open(filename, 'rb')) as fh:
        with open(filename, 'rb') as fh:
            segment = None
            offset = 0
            fh.seek(0, os.SEEK_END)
            file_size = remaining_size = fh.tell()

            while remaining_size > 0:
                offset = min(file_size, offset + buf_size)
                fh.seek(file_size - offset)
                buffer = fh.read(min(remaining_size, buf_size))

                # remove file's last "\n" if it exists, only for the first buffer
                if remaining_size == file_size and buffer[-1] == ord('\n'):
                    buffer = buffer[:-1]
                remaining_size -= buf_size
                lines = buffer.split('\n'.encode())
                # append last chunk's segment to this chunk's last line
                if segment is not None:
                    lines[-1] += segment
                segment = lines[0]
                lines = lines[1:]
                # yield lines in this chunk except the segment
                for line in reversed(lines):
                    # only decode on a parsed line, to avoid utf-8 decode error
                    l = handle_line(line)

                    # If we've reached the ending line (which is the line that contains 
                    # prusaslicer_config = 'begin' since were reading it in reverse order), 
                    # then determine what exception to raise..
                    if l is IterStatus.END:
                        # if we've somehow come here without ever having hit the begin
                        # line, then raise an EOF.
                        if in_config is False:
                            raise EOFError('Encountered ending line without ever being in the footer')

                        # Otherwise, end the generator
                        raise GeneratorExit('Encountered ending')

                    # If we've come across the beginning line (or prusaslicer_config = 'end'), 
                    # then verify this was the first time.
                    if l is IterStatus.BEGIN:
                        if in_config is True:
                            raise ValueError('Encountered the beginning line while already in settings')

                        in_config = True
                        continue

                    if type(l) is dict:
                        settings_count = settings_count+1
                        yield l

            # Don't yield None if the file was empty
            if segment is not None:
                s = handle_line(segment)
                if s is IterStatus.END:
                    raise GeneratorExit('Encountered ending')

                if type(s) is dict:
                    settings_count = settings_count+1
                    yield s

    except GeneratorExit as ge:
        pass
    finally:
        if settings_count == 0:
            raise EOFError('No settings found')

parsed_settings = {}

for line in reverse_gcode_reader(project_root + '/data/gcode-samples/prusa-sliced.gcode'):
    #print(f"line: {line}")
    if type(line) is dict:
        parsed_settings.update(line)



print(json.dumps(gcode_utils.sort_dict(parsed_settings), indent=2))
