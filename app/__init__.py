from flask import Flask
from flask_restful import Api

app = Flask( "SolidBase" )

app.secret_key = b"Change dis bitch"

api = Api( app )

from .resources.drive_resources import DriveResource
from .resources.control_resources import ControlResource

api.add_resource( 
    DriveResource, 
    "/drives", 
    "/drives/<drivename>"
)

api.add_resource( 
    ControlResource, 
    "/drives/<drivename>/controls", 
    "/drives/<drivename>/controls/<int:id>"
)

api.init_app( app )

# TODO: work on packaging and exporting drive files to merged file
# TODO: work on encrypting drive data and drive controller.json file
# TODO: work on importing merged file to app