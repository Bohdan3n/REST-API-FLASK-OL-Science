from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class DroneModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    height_min = db.Column(db.Float, nullable=False)
    height_max = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Drone(lat = {self.lat}, lon = {self.lon}, distance={self.distance}, height_min={self.height_min}, height_max={self.height_max})"
        

drone_args = reqparse.RequestParser()
drone_args.add_argument('lat', type=float, required=True)
drone_args.add_argument('lon', type=float, required=True)
drone_args.add_argument('distance', type=float, required=True)
drone_args.add_argument('height_min', type=float, required=True)
drone_args.add_argument('height_max', type=float, required=True)

droneFields = {
    'id':fields.Integer,
    'lat':fields.Float,
    'lon':fields.Float,
    'distance':fields.Float,
    'height_min':fields.Float,
    'height_max':fields.Float,
}

class Drone(Resource):
    @marshal_with(droneFields)
    def get(self):
        drone_data = DroneModel.query.all()
        return drone_data
    
    @marshal_with(droneFields)
    def post(self):
        args = drone_args.parse_args()
        drone = DroneModel(lat=args["lat"], lon=args["lon"], distance=args["distance"], height_min=args["height_min"], height_max=args["height_max"])
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
        
        height_diff = drone.height_max - drone.height_min
        return {"id": id, "height_difference": height_diff}, 200

    
api.add_resource(Drone, '/api/drone_data/')
api.add_resource(Drone_id, '/api/drone_data/<int:id>')
api.add_resource(DroneHeightDiff, '/api/drone_data/<int:id>/height_diff')


@app.route('/')
def home():
    return '<h1>Flask REST API<h1>'

if __name__ == '__main__':
    app.run(debug=True)