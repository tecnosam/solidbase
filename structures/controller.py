from .utils.array import array
from .controller_block import ControllerBlock

from .controller_types import *

from .drive import Drive

import os

import json

SIZE_METRIC = [ 'BB', 'KB', 'MB', 'GB', 'TB' ]

def translate_capacity(capacity:str):
    # converts from supported storage capacity to capacity in bytes
    return int(float(capacity[:-2]) * ( 1024 ** (SIZE_METRIC.index( capacity[-2:] )) ))

class Controller:

    def __init__( self, name:str, capacity: str ):

        self.size = translate_capacity( capacity )

        self.drive = Drive( name, self.size )

        self.name = name

        self._base = [ ControllerBlock( "drive", FOLDER_CONTROLLER, None ) ]

    # TESTED & WORKING
    def push_control( self, c_block:ControllerBlock, i_fn:str = None ):

        # the function automatically corrects span

        print()

        i_fn = i_fn if i_fn is not None else input( "Name of file: " )

        c_block.span = os.path.getsize( i_fn )

        self._base.append( c_block )

        if c_block.c_type == FILE_CONTROLLER:

            self.drive.insert( i_fn, c_block )

        return
    
    def get_folders( self ):
        # This functions iteratively fetches all folders and sorts them out
        folders = dict()

        for i in range( len ( self ) ):

            if self[ i ].c_type == FOLDER_CONTROLLER:
                folders[ i ] = []
            else:
                if i not in folders:
                    folders[ i ] = [ self[i] ]
                else:
                    folders[ i ].append( self[i] )

        return folders
    
    # TESTED & WORKING ( DO NOT TOUCH )
    def free_space( self, req_size:int = 1 ):

        free = [  ]

        occupied = [(self[i].start,self[i].end) for i in range(len(self)) if self[i].c_type==FILE_CONTROLLER]

        if not occupied:
            return [ControllerBlock( None, FILE_CONTROLLER, 0, 0, self.drive.size - 1 )]

        occupied.sort( key = lambda x: x[0] )

        N = len( occupied )

        for i in range( N ):

            if i == len( occupied ) -1:
                pass

            start = occupied[i][1] + 1 # the ending of the current plus 1

            # the ending of the next - 1. (pretty much the one in between)
            end = occupied[ i+1 ][ 0 ] - 1 if i != N-1 else self.drive.size - 1
            # if this is the last occupied, then the end would be the size of the drive

            c_type = FILE_CONTROLLER

            c_block = ControllerBlock( None, c_type, 0, start, end )

            if len( c_block ) >= req_size:

                free.append( c_block )
            else:
                # implies theres no space between blocks i and i+1
                del c_block 

        # Print out free clusters in drive based on controller data
        return free

    def dump( self ):
        blocks = []

        for block in self:
            blocks.append( block.to_dict() )
        
        with open( f"{self.name}.controller.json", "w" ) as f:

            json.dump( {
                "name": self.name,
                "capacity": f"{self.size}BB",
                "blocks": blocks
            }, f )
        
        return


    # TESTED & WORKING
    def __getitem__( self, i ):
        assert abs( i ) < len( self._base ), "Index out of range"

        return self._base[i]

    # TESTED & WORKING
    def __len__( self ):
        return len( self._base )

    def __iter__ ( self ):
        return self._base.__iter__()
