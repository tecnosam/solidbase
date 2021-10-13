from structures.utils.buffers import FileInputBuffer
from .controller_block import ControllerBlock
from .controller_types import *
from .drive import Drive
import os, json

from magic import Magic

SIZE_METRIC = [ 'BB', 'KB', 'MB', 'GB', 'TB' ]

def translate_capacity(capacity:str):
    # converts from supported storage capacity to capacity in bytes
    return int(float(capacity[:-2]) * ( 1024 ** (SIZE_METRIC.index( capacity[-2:] )) ))

class Controller:

    def __init__( self, name:str, capacity: str, drive_dir = None, afresh = True, clear:bool = True ):

        self.size = translate_capacity( capacity )


        self.drive_dir = drive_dir if drive_dir is not None else os.path.join( BASE_DIRECTORY, f"{name}-solidbase" )

        if afresh:
            try:
                os.mkdir( self.drive_dir )
            except FileExistsError:
                raise Exception( "This drive has already been created" )

        self.drive = Drive( self.drive_dir, self.size, clear = clear )

        self.name = name

        self._base = [ ControllerBlock( "drive", FOLDER_CONTROLLER, None ) ]

    # TESTED & WORKING
    def push_control( self, c_block:ControllerBlock, i_fn:str = None ):

        print()

        i_fn = i_fn if i_fn is not None else input( "Name or URL of file: " )

        if c_block.c_type == FILE_CONTROLLER:

            i_buffer = FileInputBuffer( i_fn ) # our input buffer to handle all sort of files

            # the function automatically corrects span
            c_block.span = i_buffer.full_size

            c_block.mime = i_buffer.mime

            # check if its too large
            if (
                sum(
                    [ block.span for block in self if block.c_type == FILE_CONTROLLER ],
                    c_block.span
                ) > self.drive.size
            ):
                raise Exception("File too large")

            self.drive.insert( c_block, i_buffer ) # insert file in drive

        print( "Correct size is now ", c_block.span, "ending at ", c_block.end )

        self._base.append( c_block )

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

        with open( os.path.join(f"{self.drive_dir}", ".controller.json"), "w" ) as f:

            json.dump( {
                "name": self.name,
                "capacity": f"{self.size}BB",
                "drive_dir": self.drive_dir,
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
    
    @staticmethod
    def load_file( fn ):

        with open ( fn, "r" ) as f:
            data = json.load( f )
        f.close()

        _controller = Controller( data['name'], data['capacity'], drive_dir = data['drive_dir'], afresh = False, clear = False )

        _controller._base = [] # reset base cus the root c_block is also dumped

        for block in data['blocks']:
            # we use append becuase insert will start the writing process all over
            _controller._base.append( ControllerBlock( **block ) )

        return _controller
