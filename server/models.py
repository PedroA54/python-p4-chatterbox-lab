from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, func
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Message(db.Model, SerializerMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    username = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route("/messages", methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = [
            message.to_dict() for message in Message.query.order_by("created_at")
        ]
        return make_response(jsonify(messages), 200)

    elif request.method == "POST":
        data = request.get_json()
        new_message = Message(body=data.get("body"), username=data.get("username"))
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201)


@app.route("/messages/<int:id>", methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        abort(404, description="Message not found")

    if request.method == "PATCH":
        data = request.get_json()
        message.body = data.get("body", message.body)
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return make_response(
            jsonify({"delete_successful": True, "message": "Message deleted."}), 200
        )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
