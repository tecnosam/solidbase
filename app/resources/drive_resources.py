from flask_restful import Resource, marshal_with, reqparse, abort

from werkzeug.wrappers.response import Response

from genericpath import isdir

from app.structures.utils.extras import translate_capacity

from ..structures.configs import BASE_DIRECTORY

from ..structures.controller import Controller

from .all_fields import controller_fields
from .some_functions import load_controller

import os, shutil

class DriveResource(Resource):
    args = reqparse.RequestParser()
    args.add_argument( "name", type = str, required = True )
    args.add_argument( "capacity", type = str, required = True )


    @marshal_with( controller_fields )
    def get( self, drivename:str = None ):
        if drivename is not None:

            return load_controller( drivename )

        fullpath = lambda d: os.path.join( BASE_DIRECTORY, d )
        cond = lambda d: d[-10:] == "-solidbase" and isdir( fullpath(d) )

        return [ Controller.load_file( d[:-10] ) for d in os.listdir( BASE_DIRECTORY ) if cond(d) ]

    @marshal_with( controller_fields )
    def post( self, drivename = None ):
        pl = self.args.parse_args( strict = True )
        try:
            controller = Controller( **pl )
        except FileExistsError as e:
            abort( Response(str(e), 400) )
        except ValueError:
            abort( Response( f"Incorrect value for capacity\n{translate_capacity.__doc__}\n", 400 ) )

        controller.dump()

        return controller

    @marshal_with( controller_fields )
    def delete( self, drivename:str = None ):
        if drivename is None:
            abort( Response( "Drive name is requiired" ), 400 )

        fn = os.path.join( BASE_DIRECTORY, drivename )

        try:

            controller = Controller.load_file( fn )

            if controller is None:
                abort( Response("Drive not found", 404) )

            shutil.rmtree( fn )

        except Exception as e:

            abort( Response( str(e), 500 ) )

        return controller