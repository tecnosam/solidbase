import io
from .controller import ControllerBlock

from .controller_types import CAPACITY_HEADER_SIZE

class Drive:

    """
        This Structure allows users to:
            1) Instantiate new drives
            2) Store bytes in drives in storage
            3) Determine the size of drive
            4) Write changes to drive in storage
    """

    def __init__( self, fn:str, size:int, clear:bool = True ):

        self.fn = fn

        self._size = size

        if clear:
            self.clear( b'\x00' )

    def clear( self, byte:bytes ):

        with open( self.fn, "wb" ) as f:

            f.write( self._size.to_bytes( CAPACITY_HEADER_SIZE, "big" ) )
            print(self._size.to_bytes( CAPACITY_HEADER_SIZE, "big" ))

            for i in range( self.size ):
                f.write( byte )

        f.close()

    def insert( self, c_block:ControllerBlock, i_stream ):
        # writes files in file with fn c_block.name to virtual drive on disk
        with open( self.fn, "rb+" ) as o_stream:

            print( c_block.start, CAPACITY_HEADER_SIZE, c_block.end )

            for _ in range( c_block.start + CAPACITY_HEADER_SIZE, c_block.end + CAPACITY_HEADER_SIZE + 1 ):

                byte = i_stream.read(1)
                print(byte, 'x')

                o_stream.seek( _, 0 )
                o_stream.write( byte )
                o_stream.seek(0)

        o_stream.close()

        return 

    def __getitem__(self, c_block: ControllerBlock):

        stream = open( self.fn, "rb" )
        stream.seek( c_block.start + CAPACITY_HEADER_SIZE, 0 )

        return FileOutputBuffer(stream, c_block)

    def set_size( self, new_size ):
        self._size = new_size
        # change file header in file
    
    def get_size( self ) -> int:
        return self._size

    size = property( get_size, set_size )


class FileOutputBuffer:

    def __init__(self, stream: io.BufferedReader, c_block:ControllerBlock, b_size:int = 1) -> None:

        self._stream = stream

        self._c_block = c_block

        self._cur = 0

        self._b_size = b_size

    def reset( self ):
        self._cur = 0
        self._stream.seek( self._c_block.start + CAPACITY_HEADER_SIZE, 0 )

    def __next__( self ):
        if ( self._cur >= self._c_block.span ):
            raise StopIteration

        self._cur += self.b_size

        if self._cur > self._c_block.span:
            byte = self._stream.read( self._cur - self._c_block.span )
        else:
            byte = self._stream.read( self.b_size )

        return byte

    def __iter__( self ):

        # reset the stream to point to beginning of file

        self.reset()

        return self
    
    def set_buffer_size( self, n:int ):
        self.reset()
        self._b_size = n

    def get_buffer_size( self ) -> int:
        return self._b_size

    b_size = property( get_buffer_size, set_buffer_size )

# TODO: work on FileInputBuffer