from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from datetime import datetime, timezone
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
datetime.now(timezone.utc)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class DroneModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    distanceCm = db.Column(db.Float, nullable=False)
    minDistance = db.Column(db.Float, nullable=False)
    maxDistance = db.Column(db.Float, nullable=False)
    lot = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    z = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return (f"Drone(time={self.time}, distanceCm={self.distanceCm}, "
                f"minDistance={self.minDistance}, maxDistance={self.maxDistance}, "
                f"lot={self.lot}, lat={self.lat}), x={self.x}, y={self.y}, y={self.y}")

def parse_datetime(value):
    try:
        return datetime.strptime(value, "%Y.%d.%m.%H:%M")
    except ValueError:
        raise ValueError("time must be in format YYYY.DD.MM.HH:MM")        

drone_args = reqparse.RequestParser()
drone_args.add_argument('time', type=parse_datetime, required=False)
drone_args.add_argument('distanceCm', type=float, required=True)
drone_args.add_argument('minDistance', type=float, required=True)
drone_args.add_argument('maxDistance', type=float, required=True)
drone_args.add_argument('lot', type=float, required=True)
drone_args.add_argument('lat', type=float, required=True)
drone_args.add_argument('x', type=float, required=True)
drone_args.add_argument('y', type=float, required=True)
drone_args.add_argument('z', type=float, required=True)

droneFields = {
    'id': fields.Integer,
    'time': fields.DateTime,
    'distanceCm': fields.Float,
    'minDistance': fields.Float,
    'maxDistance': fields.Float,
    'lot': fields.Float,
    'lat': fields.Float,
    'x': fields.Float,
    'y': fields.Float,
    'z': fields.Float
}


class Drone(Resource):
    @marshal_with(droneFields)
    def get(self):
        drone_data = DroneModel.query.all()
        return drone_data
    
    @marshal_with(droneFields)
    def post(self):
        args = drone_args.parse_args()
        drone = DroneModel(time=args["time"] if args["time"] else datetime.now(timezone.utc), distanceCm=args["distanceCm"], minDistance=args["minDistance"], maxDistance=args["maxDistance"], lot=args["lot"], lat=args["lat"], x=args["x"], y=args["y"], z=args["z"])
        db.session.add(drone)
        db.session.commit()
        drone_data = DroneModel.query.all()
        return drone_data, 201
    
class Drone_id(Resource):
    @marshal_with(droneFields)
    def get(self, id):
        drone = DroneModel.query.filter_by(id=id).first()
        if not drone:
            abort(404, "Drone id not found")
        return drone
    
    @marshal_with(droneFields)
    def delete(self, id):
        drone = DroneModel.query.filter_by(id=id).first()
        if not drone:
            abort(404, "Drone id not found")
        db.session.delete(drone)
        db.session.commit()
        drone_data = DroneModel.query.all()
        return drone_data, 204
    
class DroneHeightDiff(Resource):
    def get(self, id):
        drone = DroneModel.query.filter_by(id=id).first()
        if not drone:
            abort(404, message="Drone data not found")
        
        height_diff = drone.maxDistance - drone.minDistance
        return {"id": id, "height_difference": height_diff}, 200


    
api.add_resource(Drone, '/api/drone_data/')
api.add_resource(Drone_id, '/api/drone_data/<int:id>')
api.add_resource(DroneHeightDiff, '/api/drone_data/<int:id>/height_diff')


@app.route('/')
def home():
    return '<h1>Flask REST API<h1>'

if __name__ == '__main__':
    app.run(debug=True)