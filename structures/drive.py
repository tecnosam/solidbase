from .controller import ControllerBlock

class Drive:

    """
        This Structure allows users to:
            1) Instantiate new drives
            2) Store bytes in drives in storage
            3) Determine the size of drive
            4) Write changes to drive in storage
    """

    def __init__( self, fn:str, size:int ):

        self.fn = ".".join((fn, "sbdrive"))
        self.size = size

        self.clear( b'\x00' )

    def clear( self, byte:bytes ):

        with open( self.fn, "wb" ) as f:

            for i in range( self.size ):
                f.write( byte )

        f.close()

    def insert( self, i_fn, c_block:ControllerBlock ):
        # writes files in file with fn c_block.name to virtual drive on disk
        with open( self.fn, "rb+" ) as o_stream:

            print( c_block.start )

            with open( i_fn, "rb" ) as i_stream:

                for _ in range( c_block.start, c_block.end + 1 ):

                    byte = i_stream.read(1)

                    o_stream.seek( _, 0 )
                    o_stream.write( byte )
                    o_stream.seek(0)

        i_stream.close()
        o_stream.close()

        return 

