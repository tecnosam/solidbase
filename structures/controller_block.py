from .utils.graph import Node
from .utils.array import array, Iterator


class ControllerBlock:

    def __init__( self, name, c_type, parent = 0, start = 0, end = 0 ):

        self._name = name
        self.c_type = c_type
        self.parent = parent
        self.start = start
        self.end = end

        self.is_root = parent is None

    @staticmethod
    def load_dict( data:dict ):
        return ControllerBlock( **data )

    def to_dict(self):
        return {
            "name": self._name,
            "c_type": self.c_type,
            "parent": self.parent,
            "start": self.start,
            "end": self.end
        }

    def rename ( self, new_name ):
        self._name = new_name
    
    def get_name( self ) -> str:
        return self._name
    
    def refix_span( self, new_span:int ):
        self.end = self.start + ( new_span - 1 )

    def __len__( self ):

        return (self.end - self.start) + 1

    name = property( get_name, rename )
    span = property( __len__, refix_span )