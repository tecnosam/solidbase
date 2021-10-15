import io, requests, os

from ..controller_block import ControllerBlock

from ..configs import *

import validators

from magic import Magic

class FileOutputBuffer:

    def __init__(self, stream: io.BufferedReader, c_block:ControllerBlock, b_size:int = 1) -> None:

        self._stream = stream

        self._c_block = c_block

        self._cur = 0

        self._b_size = b_size

    def reset( self ):
        self._cur = 0
        self._stream.seek( self._c_block.start, 0 )

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

class FileInputBuffer:

    def __init__( self, i_fn:str, b_size:int = 8192 ):

        self._b_size = b_size


        if validators.url( i_fn ):

            try:
                _stream = requests.get( i_fn, stream=True )

                if ( _stream.headers.get('content-length') is None ):
                    raise FutureWarning("Content length is not set")

                self.full_size = int(_stream.headers['content-length'])

                self._stream = _stream.iter_content( self._b_size )

                self.mime = _stream.headers['content-type'].split(";")[0]

            except Exception as e:

                raise e

            self.b_type = 'url'

        else:

            self.full_size = os.path.getsize( i_fn )

            self._stream = open( i_fn, "rb" )

            self.mime = Magic( mime = True, uncompress = True ).from_file( i_fn )

            self.b_type = 'file'


    def read( self):
        if self.b_type == 'file':
            return self._stream.read( self.b_size )

        return next( self._stream ) # potential bug here

    def meta_data(self):
        pass

    def get_b_size( self ):
        return self._b_size
    
    b_size = property( get_b_size )
