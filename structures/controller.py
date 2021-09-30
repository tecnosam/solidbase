from .utils.array import array
from .controller_block import ControllerBlock

from .controller_types import *

import os

import json

SIZE_METRIC = [ 'BB', 'KB', 'MB', 'GB', 'TB' ]

def translate_capacity(capacity:str):
    # converts from supported storage capacity to capacity in bytes
    return int(float(capacity[:-2]) * ( 1024 ** (SIZE_METRIC.index( capacity[-2:] )) ))


class Drive( array ):

    """
        This Structure allows users to:
            1) Instantiate new drives
            2) Store bytes in drives in storage
            3) Determine the size of drive
            4) Write changes to drive in storage
    """

    def __init__( self, fn:str, size:int ):
        # TODO: think of how to solve the array of large bytes issue
        self.fn = ".".join((fn, "sbdrive"))

        super(  ).__init__( size, bytes )

        self.clear( b'\x00' )

        with open( self.fn, "wb" ) as f:
            for byte in self:
                f.write( byte )

        f.close()

    def insert( self, c_block:ControllerBlock ):
        # writes files in file with fn c_block.name to virtual drive on disk
        with open( self.fn, "rb+" ) as o_stream:

            print( c_block.start )

            with open( c_block.name, "rb" ) as i_stream:

                for _ in range( c_block.start, c_block.end + 1 ):


                    byte = i_stream.read(1)

                    self[ _ ] = byte

                    o_stream.seek( _, 0 )
                    o_stream.write( byte )
                    o_stream.seek(0)

        i_stream.close()
        o_stream.close()

        return 


class Controller:

    def __init__( self, fn:str, capacity: str ):

        self.size = translate_capacity( capacity )

        self.drive = Drive( fn, self.size )

        self.fn = fn

        self._base = [ ControllerBlock( "drive", FOLDER_CONTROLLER, None ) ]

    # TESTED & WORKING
    def push_control( self, c_block:ControllerBlock ):

        # the function automatically corrects span
        print()
        c_block.span = os.path.getsize( c_block.name )

        self._base.append( c_block )

        if c_block.c_type == FILE_CONTROLLER:

            self.drive.insert( c_block )

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
        
        with open( self.fn, "w" ) as f:

            json.dump( blocks, f )
        
        return


    # TESTED & WORKING
    def __getitem__( self, i ):
        assert abs( i ) < len( self._base ), "Index out of range"

        return self._base[i]

    # TESTED & WORKING
    def __len__( self ):
        return len( self._base )
