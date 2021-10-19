from ctypes import pointer, py_object

class array:

    def __init__( self, size, dtype ):
        self._size = size

        self._dtype = dtype

        self._base = (py_object * size)()

    def clear( self, val = 0 ):

        assert self.val_type(val), f"{type(val)} is not {self._dtype}"

        for i in range( self._size ):

            self._base[ i ] = val

        return

    def val_type( self, val ):
        return type( val ) == self._dtype
    
    def get_size( self ):
        return self._size
    
    def resize( self, new_size:int ):

        if new_size < self._size:

            print("WARNING: New size lower than initial size, Data positioned at index greater will be thrown away!!!")

        new_arr = array( new_size, dtype = self._dtype )

        N = self._size if self._size < new_size else new_size

        for i in range( N ):

            new_arr[ i ] = self[ i ]

        self._base = new_arr._base
        self._size = new_arr._size
        self._dtype = new_arr._dtype

        del new_arr

        return self._size

    def __setitem__(self, i, val) -> None:

        assert self.val_type(val), f"{type(val)} is not {self._dtype}"

        self._base[ i ] = val

    def __getitem__(self, i) -> int:
        try:
            return self._base[ i ]
        except ValueError:
            return None

    def __len__(self):
        return self._size

    def __iter__( self ):
        return Iterator( self )
    
    size = property( get_size, resize )

class Iterator:
    def __init__( self, iteratable ):
        self.cur = 0
        self._iteratable = iteratable

    def __next__( self ):

        self.cur += 1

        if self.cur == len( self._iteratable )+1:
            raise StopIteration()

        return self._iteratable[ self.cur - 1 ]
