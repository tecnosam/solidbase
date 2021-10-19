from ..controller_block import ControllerBlock

from ..configs import FILE_CONTROLLER

SIZE_METRIC = [ 'BB', 'KB', 'MB', 'GB', 'TB' ]

def translate_capacity(capacity:str):
    # converts from supported storage capacity to capacity in bytes
    return int(float(capacity[:-2]) * ( 1024 ** (SIZE_METRIC.index( capacity[-2:] )) ))


def interference( b: ControllerBlock, s:int) -> bool:
    # TODO: test this
    return b.c_type == FILE_CONTROLLER and (( b.start < s and b.end < s ) or b.start > s)

def overlap( b1:ControllerBlock, b2:ControllerBlock ) ->bool:
    return  b1.start <= b2.start <= b1.end or b2.start <= b1.start <= b2.end