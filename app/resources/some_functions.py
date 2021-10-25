from ..structures.controller import Controller

from flask import abort, Response

def load_controller( drivename ) -> Controller:

    _controller = Controller.load_file( drivename )

    if _controller is None:

        abort( Response( "Controller not found", 404 ) )

    return _controller