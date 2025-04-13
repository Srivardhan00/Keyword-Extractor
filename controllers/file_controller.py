from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

file_routes = Blueprint("file_routes", __name__)

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["keyword_extractor"]  # Replace with your database name
file_collection = db["files"]  # Collection for storing file data

# Create a new file
@file_routes.route("/files", methods=["POST"])
def create_file():
    data = request.json
    if not data.get("file_name") or not data.get("file_type"):
        return jsonify({"error": "file_name and file_type are required"}), 400
    try:
        file_data = {
            "file_name": data["file_name"],
            "keywords": data.get("keywords", []),
            "file_type": data["file_type"],
            "description": data.get("description", ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = file_collection.insert_one(file_data)
        file_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return jsonify(file_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Get all files
@file_routes.route("/files", methods=["GET"])
def get_files():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit
        files = list(file_collection.find().skip(skip).limit(limit))
        for file in files:
            file["_id"] = str(file["_id"])
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Get a single file by ID
@file_routes.route("/files/<file_id>", methods=["GET"])
def get_file(file_id):
    try:
        file = file_collection.find_one({"_id": ObjectId(file_id)})
        if not file:
            return jsonify({"error": "File not found"}), 404
        file["_id"] = str(file["_id"])  # Convert ObjectId to string
        return jsonify(file), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Update a file by ID
@file_routes.route("/files/<file_id>", methods=["PUT"])
def update_file(file_id):
    data = request.json
    try:
        update_data = {
            "file_name": data.get("file_name"),
            "keywords": data.get("keywords"),
            "file_type": data.get("file_type"),
            "description": data.get("description"),
            "updated_at": datetime.utcnow(),
        }
        # Remove None values from update_data
        update_data = {k: v for k, v in update_data.items() if v is not None}

        result = file_collection.update_one(
            {"_id": ObjectId(file_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "File not found"}), 404

        file = file_collection.find_one({"_id": ObjectId(file_id)})
        file["_id"] = str(file["_id"])  # Convert ObjectId to string
        return jsonify(file), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Delete a file by ID
@file_routes.route("/files/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    try:
        result = file_collection.delete_one({"_id": ObjectId(file_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "File not found"}), 404
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400