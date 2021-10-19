from flask_restful import Resource, marshal_with, reqparse, abort

from werkzeug.wrappers.response import Response

from genericpath import isdir

from app.structures.utils.extras import translate_capacity

from ..structures.configs import BASE_DIRECTORY

from ..structures.controller import Controller

from .all_fields import drive_fields

import os, shutil

class DriveResource(Resource):
    args = reqparse.RequestParser()
    args.add_argument( "name", type = str, required = True )
    args.add_argument( "capacity", type = str, required = True )


    @marshal_with( drive_fields )
    def get( self, drivename:str = None ):
        if drivename is not None:

            if os.path.exists( os.path.join( BASE_DIRECTORY, f"{drivename}-solidbase" ) ):
                return Controller.load_file( drivename )
        
        fullpath = lambda d: os.path.join( BASE_DIRECTORY, d )
        cond = lambda d: d[-10:] == "-solidbase" and isdir( fullpath(d) )

        return [ Controller.load_file( d[:-10] ) for d in os.listdir( BASE_DIRECTORY ) if cond(d) ]

    @marshal_with( drive_fields )
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

    @marshal_with( drive_fields )
    def delete( self, drivename:str = None ):
        if drivename is None:
            abort( Response( "Drive name is requiired" ), 400 )

        fn = os.path.join( BASE_DIRECTORY, drivename )

        try:
            controller = Controller.load_file( fn )
            shutil.rmtree( fn )
        except Exception as e:
            abort( Response( str(e), 500 ) )

        return controller