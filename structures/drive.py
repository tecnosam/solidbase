from .controller import ControllerBlock

from .controller_types import CAPACITY_HEADER_SIZE

from .utils.buffers import FileInputBuffer, FileOutputBuffer

import os


class Drive:

    """
        This Structure allows users to:
            1) Instantiate new drives
            2) Store bytes in drives in storage
            3) Determine the size of drive
            4) Write changes to drive in storage
    """

    def __init__( self, drive_dir:str, size:int, clear:bool = True ):

        self.fn = os.path.join( drive_dir, "sbdrive" )

        self._size = size

        self._header_size = 0

        if clear:
            self.clear( b'\x00' )

    def clear( self, byte:bytes ):

        with open( self.fn, "wb" ) as f:

            # f.write( self._size.to_bytes( CAPACITY_HEADER_SIZE, "big" ) )

            for i in range( self.size ):
                f.write( byte )

        f.close()

    def insert( self, c_block:ControllerBlock, i_stream:FileInputBuffer ):
        # writes files in file with fn c_block.name to virtual drive on disk
        with open( self.fn, "rb+" ) as o_stream:
            _ = c_block.start + self.header_size

            # for _ in range( c_block.start + self.header_size, c_block.end + self.header_size + 1 ):
            try:
                while byte := i_stream.read():
                    # byte = i_stream.read()

                    o_stream.seek( _, 0 )
                    o_stream.write( byte )
                    o_stream.seek(0)

                    _ += len( byte )
            except StopIteration:
                pass

        o_stream.close()

        return 

    def __getitem__(self, c_block: ControllerBlock):

        stream = open( self.fn, "rb" )
        stream.seek( c_block.start + self.header_size, 0 )

        return FileOutputBuffer(stream, c_block)

    # properties
    def set_size( self, new_size ):
        self._size = new_size
        # change file header in file

    def get_size( self ) -> int:
        return self._size

    def set_header_size( self, val:int ):
        self._header_size = val

    def get_header_size( self ) -> int:
        return self._header_size

    size = property( get_size, set_size )
    header_size = property( get_header_size, set_header_size )
