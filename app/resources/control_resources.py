
import os, sys

from flask_restful import Resource, marshal_with, reqparse
from flask import request, stream_with_context, abort, Response
from werkzeug.utils import secure_filename

from ..structures.configs import FILE_CONTROLLER, TEMP_DIRECTORY
from ..structures.controller import Controller
from ..structures.controller_block import ControllerBlock

from .all_fields import control_fields

from .some_functions import load_controller

class ControlResource(Resource):

    arg_parser = reqparse.RequestParser()

    arg_parser.add_argument( "name", type = str, required = True )
    arg_parser.add_argument( "c_type", type = int, required = True, default = FILE_CONTROLLER )
    arg_parser.add_argument( "parent", type = int, required = False, default = 0 )

    @marshal_with( control_fields )
    def get( self, drivename, id:int = None ):
        _controller = load_controller( drivename )

        if id is None:
            return _controller._base

        index = _controller.find( id )

        if index == -1:
            abort ( Response( "Controller not found", 404 ) )

        return _controller[ index ]

    @marshal_with( control_fields )    
    def post( self, drivename, id:int = None ):

        _controller = load_controller( drivename )

        args = self.arg_parser.parse_args( strict = True )

        _block = ControllerBlock( **args )

        if _block.c_type == FILE_CONTROLLER:
            # look for file
            url = request.args.get( 'url' )
            if url is not None:
                source = url
            else:
                upload = request.files[ 'source' ]
                source = os.path.join( TEMP_DIRECTORY, secure_filename( upload.filename ) )
                upload.save( source )
        else:
            source = None

        _id = _controller.push_control( _block, source )

        return _controller[ _controller.find( _id ) ]
    
    @marshal_with(control_fields)
    def delete( self, drivename, id:int = None ):
        if id is None:
            abort( Response( "ID of block is required", 400 ) )

        _controller = load_controller( drivename )

        _block = _controller.pop_control( id )

        if _block is None:
            abort( Response( "Block with ID {} not found".format( id ), 404 ) )

        _controller.dump()

        return _block

        # try:
        #     return _controller.pop_control( id )
        # except IndexError as e:
        #     abort( Response( str(e), 404 ) )