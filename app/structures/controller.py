from .utils.buffers import FileInputBuffer
from .utils.extras import interference, translate_capacity
from .controller_block import ControllerBlock
from .configs import *
from .drive import Drive
import os, json, collections

class Controller:

    def __init__( self, name:str, capacity: str, drive_dir = None, afresh = True, clear:bool = True, base_length:int = 1 ):

        self.size = translate_capacity( capacity ) # fetch the size
        self.name = name
        self.base_length = base_length

        # configure drive directory
        self.drive_dir = drive_dir if drive_dir is not None else os.path.join( BASE_DIRECTORY, f"{name}-solidbase" )

        if afresh:

            try:
                os.mkdir( self.drive_dir )
            except FileExistsError:
                raise FileExistsError( "This drive has already been created" )

            self._base = [ ControllerBlock( "drive", FOLDER_CONTROLLER, None ) ]
            self._base[0].id = 0

        else:
            self._base = list()

        self.drive = Drive( self.drive_dir, self.size, clear = clear ) # instantiate drive

    # TESTED & WORKING
    # CRUD post control
    def push_control( self, c_block:ControllerBlock, i_fn:str = None ):
        if self.find( c_block.parent ) == -1:
            raise Exception( "Cannot find parent" )

        if c_block.c_type == FILE_CONTROLLER:

            i_fn = i_fn if i_fn is not None else input( "Name or URL of file: " )

            i_buffer = FileInputBuffer( i_fn ) # our input buffer to handle all sort of files

            try:
                block : ControllerBlock = next(self._free_space( i_buffer.full_size ))

                # the function automatically corrects span
                block.name = c_block.name
                block.parent = c_block.parent

                block.mime = i_buffer.mime

                c_block = block
            except StopIteration:
                raise Exception( "No space to place your data. You can try upgrading storage" )

            self.drive.insert( c_block, i_buffer ) # insert file in drive

        c_block.id = self.base_length

        self._base.append( c_block )

        self.base_length += 1

        self.dump()

        return c_block.id

    # CRUD PUT control
    def rename_control( self, id:int, name:str ):
        i = self.find(id)
        if i == -1:
            raise IndexError( "Cannot find ControllerBlock with id %s" % id )
        self[ i ].name = name

    # CRUD delete control
    def pop_control( self, id) -> ControllerBlock:
        i = self.find(id)
        if i == -1:
            # raise IndexError( "Cannot find ControllerBlock with id %s" % id )
            return None
        c_block = self._base.pop( i )

        # delete all children recursively
        if c_block.c_type == FOLDER_CONTROLLER:

            for block in self:
                if block.parent == c_block.id:
                    self.pop_control( block.id )

        return c_block

    def delete_control( self, id ):
        i = self.find(id)
        if i == -1:
            raise IndexError( "Cannot find ControllerBlock with id %s" % id )

        # delete all children recursively
        if self[i].c_type == FOLDER_CONTROLLER:
            for block in self:
                if block.parent == id:
                    self.delete_control( block.id )

        self[ i ].deleted = True

        self.dump()

    def restore_control( self, id ):
        # raise NotImplementedError("Coming soon as soon as I figure out the journaling stuff")
        i = self.find( id )
        self[ i ].deleted = False

        # restore all children recursively
        if self[i].c_type == FOLDER_CONTROLLER:
            for block in self:
                if block.parent == id:
                    self.restore_control( block.id )

        self.dump()

    # CRUD get control /:solidbase
    def get_folders( self, deleted = False ):
        # This functions iteratively fetches all folders and sorts them out
        # This works and i dont know why

        # the deleted parameter determines whether the deleted controllers will also be listed

        full = collections.defaultdict( dict )

        for block in self._base:

            if block.deleted and not deleted:
                continue

            ident = self.find( block.id )
            assert ident != -1
            parent = block.parent
            final = full[ ident ]
            if block.c_type == FILE_CONTROLLER:
                final = block

            if not block.is_root:
                full[ parent ][ ident ] = final
            else:
                root = final

        return root

    # TESTED & WORKING ( DO NOT TOUCH )
    def _free_space( self, req_size:int = 1 ) -> ControllerBlock:

        # free = [  ]

        occupied = [(self[i].start,self[i].end) for i in range(len(self)) if self[i].c_type==FILE_CONTROLLER and not self[i].deleted]

        if not occupied:
            yield ControllerBlock( None, FILE_CONTROLLER, 0, 0, self.drive.size - 1 )
            # return []

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
                c_block.span = req_size
                yield c_block

                # free.append( c_block )
            else:
                # implies theres no space between blocks i and i+1
                del c_block 

        # Print out free clusters in drive based on controller data
        # return free

    def resize( self, new_size:int ):
        if new_size < self.drive.size:
            for i in range( len(self._base) ):
                if interference( self[i], new_size ):
                    self._base.pop( i )
                # if self[i].c_type != FILE_CONTROLLER:
                #     continue
                # if ( self[i].start < new_size and self[i].end < new_size ) or ( self[i].start > new_size ):
                #     # indicates that the block is in the way
                #     self._base.pop( i )

        self.drive.size = new_size
        return new_size

    # TESTED & WORKING
    # get control /:solidbase/:id
    def __getitem__( self, i ):
        assert abs( i ) < len( self._base ), "Index out of range"

        return self._base[i]

    # TESTED & WORKING
    def __len__( self ):
        return len( self._base )

    def __iter__ ( self ):
        return self._base.__iter__()

    def find(self, id:int) -> int:
        # perform bin search
        low = 0
        high = len(self._base) - 1
        mid = 0

        while low <= high:
            mid = ( low + high ) // 2
            if self._base[ mid ].id == id:
                return mid
            elif self._base[mid].id > id:
                high = mid - 1
            elif self._base[ mid ].id < id:
                low = mid + 1
        return -1

    def dump( self ):
        blocks = []

        for block in self:
            blocks.append( block.to_dict() )

        with open( os.path.join(f"{self.drive_dir}", ".controller.json"), "w" ) as f:

            json.dump( {
                "name": self.name,
                "capacity": f"{self.size}BB",
                "drive_dir": self.drive_dir,
                "blocks": blocks,
                "base_length": self.base_length
            }, f )

        return

    @staticmethod
    def load_file( drivename ):
        fn = os.path.join( BASE_DIRECTORY, f"{drivename}-solidbase", ".controller.json" )
        try:
            with open ( fn, "r" ) as f:
                data = json.load( f )
            f.close()
        except FileNotFoundError:
            return None

        _controller = Controller( 
            data['name'], data['capacity'], drive_dir = data['drive_dir'],
            afresh = False, clear = False, base_length = data['base_length']
        )

        # _controller._base = [] # reset base cus the root c_block is also dumped

        for block in data['blocks']:
            # we use append becuase insert will start the writing process all over
            _controller._base.append( ControllerBlock( **block ) )

        return _controller
