from flask import Flask
from flask_restful import Api

app = Flask( "SolidBase" )

app.secret_key = b"Change dis bitch"

api = Api( app )

from .resources.drive_resources import DriveResource

api.add_resource( DriveResource, "/drives", "/drives/<drivename>" )

api.init_app( app )