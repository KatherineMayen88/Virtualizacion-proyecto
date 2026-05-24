from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

import requests


app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

songs_collection = db["songs"]
genres_collection = db["genres"]
users_collection = db["users"]
ratings_collection = db["ratings"]


def serialize_id(item):
    item["id"] = str(item["_id"])
    del item["_id"]
    return item


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Music Discovery API funcionando"})


# SONGS - public panel can create and view songs

@app.route("/api/songs", methods=["GET"])
def get_songs():
    songs = [serialize_id(song) for song in songs_collection.find()]
    return jsonify(songs)


@app.route("/api/songs", methods=["POST"])
def create_song():
    data = request.json

    result = songs_collection.insert_one({
        "title": data.get("title"),
        "artist": data.get("artist"),
        "genre": data.get("genre")
    })

    return jsonify({"message": "Song created", "id": str(result.inserted_id)}), 201


# GENRES - public panel can create and view genres

@app.route("/api/genres", methods=["GET"])
def get_genres():
    genres = [serialize_id(genre) for genre in genres_collection.find()]
    return jsonify(genres)


@app.route("/api/genres", methods=["POST"])
def create_genre():
    data = request.json

    result = genres_collection.insert_one({
        "name": data.get("name"),
        "description": data.get("description")
    })

    return jsonify({"message": "Genre created", "id": str(result.inserted_id)}), 201


# USERS - simple profile system

@app.route("/api/users", methods=["GET"])
def get_users():
    users = [serialize_id(user) for user in users_collection.find()]
    return jsonify(users)


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json

    result = users_collection.insert_one({
        "username": data.get("username"),
        "password": data.get("password"),
        "fullName": data.get("fullName"),
        "favoriteGenres": data.get("favoriteGenres", [])
    })

    return jsonify({"message": "User created", "id": str(result.inserted_id)}), 201



@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({
        "username": username,
        "password": password
    })

    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": serialize_id(user)
    })



@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json

    update_data = {
        "username": data.get("username"),
        "fullName": data.get("fullName"),
        "favoriteGenres": data.get("favoriteGenres", [])
    }

    if data.get("password"):
        update_data["password"] = data.get("password")

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    return jsonify({"message": "User updated"})



@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    ratings_collection.delete_many({"userId": user_id})

    return jsonify({"message": "User deleted"})


# PUBLIC RATINGS - no update/delete from public panel

@app.route("/api/ratings/public", methods=["POST"])
def create_public_rating():
    data = request.json

    result = ratings_collection.insert_one({
        "songId": data.get("songId"),
        "score": int(data.get("score", 0)),
        "source": "public"
    })

    return jsonify({"message": "Public rating created", "id": str(result.inserted_id)}), 201


# USER RATINGS - update/delete allowed inside user portal

@app.route("/api/ratings/user", methods=["POST"])
def create_or_update_user_rating():
    data = request.json

    user_id = data.get("userId")
    song_id = data.get("songId")
    score = int(data.get("score", 0))

    existing_rating = ratings_collection.find_one({
        "userId": user_id,
        "songId": song_id,
        "source": "user"
    })

    if existing_rating:
        ratings_collection.update_one(
            {"_id": existing_rating["_id"]},
            {"$set": {"score": score}}
        )

        return jsonify({"message": "User rating updated"})

    result = ratings_collection.insert_one({
        "userId": user_id,
        "songId": song_id,
        "score": score,
        "source": "user"
    })

    return jsonify({"message": "User rating created", "id": str(result.inserted_id)}), 201


@app.route("/api/ratings/<rating_id>", methods=["PUT"])
def update_rating(rating_id):
    data = request.json

    ratings_collection.update_one(
        {"_id": ObjectId(rating_id), "source": "user"},
        {"$set": {"score": int(data.get("score", 0))}}
    )

    return jsonify({"message": "Rating updated"})


@app.route("/api/ratings/<rating_id>", methods=["DELETE"])
def delete_rating(rating_id):
    ratings_collection.delete_one({
        "_id": ObjectId(rating_id),
        "source": "user"
    })

    return jsonify({"message": "Rating deleted"})


# TOP SONGS - public + user ratings

@app.route("/api/songs/top", methods=["GET"])
def get_top_songs():
    pipeline = [
        {
            "$group": {
                "_id": "$songId",
                "rankingCount": {"$sum": 1},
                "averageScore": {"$avg": "$score"}
            }
        },
        {
            "$addFields": {
                "songObjectId": {"$toObjectId": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "songs",
                "localField": "songObjectId",
                "foreignField": "_id",
                "as": "song"
            }
        },
        {"$unwind": "$song"},
        {
            "$project": {
                "_id": 0,
                "songId": "$_id",
                "title": "$song.title",
                "artist": "$song.artist",
                "genre": "$song.genre",
                "rankingCount": 1,
                "averageScore": {"$round": ["$averageScore", 2]}
            }
        },
        {
            "$sort": {
                "averageScore": -1,
                "rankingCount": -1
            }
        }
    ]

    return jsonify(list(ratings_collection.aggregate(pipeline)))


# USER PROFILE

@app.route("/api/users/<user_id>/profile", methods=["GET"])
def get_user_profile(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"message": "User not found"}), 404

    ratings = list(ratings_collection.find({
        "userId": user_id,
        "source": "user"
    }))

    ranked_songs = []
    total_score = 0

    for rating in ratings:
        song = songs_collection.find_one({"_id": ObjectId(rating["songId"])})

        if song:
            ranked_songs.append({
                "ratingId": str(rating["_id"]),
                "songId": str(song["_id"]),
                "title": song.get("title"),
                "artist": song.get("artist"),
                "genre": song.get("genre"),
                "score": rating.get("score")
            })

            total_score += rating.get("score", 0)

    average_score = round(total_score / len(ranked_songs), 2) if ranked_songs else 0

    return jsonify({
        "user": serialize_id(user),
        "rankedSongs": ranked_songs,
        "averageScore": average_score,
        "totalRankings": len(ranked_songs)
    })



@app.route("/api/users/<user_id>/recommendations", methods=["GET"])
def get_user_recommendations(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"message": "User not found"}), 404

    favorite_genres = user.get("favoriteGenres", [])

    if not favorite_genres:
        favorite_genres = ["Pop", "Rock", "Alternative"]

    excluded_titles = request.args.get("exclude", "")
    excluded_titles = [
        title.strip().lower()
        for title in excluded_titles.split(",")
        if title.strip()
    ]

    ranked_titles = []

    for rating in ratings_collection.find({
        "userId": user_id,
        "source": "user"
    }):
        song = songs_collection.find_one({
            "_id": ObjectId(rating["songId"])
        })

        if song:
            ranked_titles.append(song.get("title", "").lower())

    blocked_titles = ranked_titles + excluded_titles

    search_terms = {
        "Pop": ["pop hits", "top pop songs", "pop music"],
        "Rock": ["rock hits", "classic rock", "alternative rock"],
        "Alternative": ["alternative rock", "indie alternative", "alternative music"],
        "Indie": ["indie music", "indie pop", "indie rock"],
        "Country": ["country music", "country hits", "modern country"],
        "Hip-Hop": ["hip hop hits", "rap music", "hip-hop"],
        "R&B": ["r&b music", "soul r&b", "rnb hits"],
        "Electronic": ["electronic music", "edm hits", "dance music"],
        "Latin": ["latin music", "reggaeton", "latin pop"]
    }

    recommendations = []

    for genre in favorite_genres:
        terms = search_terms.get(genre, [genre])

        for term in terms:
            response = requests.get(
                "https://itunes.apple.com/search",
                params={
                    "term": term,
                    "media": "music",
                    "entity": "song",
                    "limit": 50
                },
                timeout=8
            )

            data = response.json()

            for item in data.get("results", []):
                track_name = item.get("trackName", "")
                artist_name = item.get("artistName", "")

                if not track_name or not artist_name:
                    continue

                if track_name.lower() in blocked_titles:
                    continue

                already_added = any(
                    rec["title"].lower() == track_name.lower()
                    and rec["artist"].lower() == artist_name.lower()
                    for rec in recommendations
                )

                if already_added:
                    continue

                recommendations.append({
                    "title": track_name,
                    "artist": artist_name,
                    "genre": item.get("primaryGenreName"),
                    "previewUrl": item.get("previewUrl"),
                    "artworkUrl": item.get("artworkUrl100")
                })

                if len(recommendations) >= 30:
                    break

    if len(recommendations) >= 12:
        return jsonify(recommendations[:12])

    # Fallback final: si el filtro por géneros no alcanza,
    # busca música popular general para que nunca quede vacío.
    fallback_terms = [
        "top songs",
        "new music",
        "popular music",
        "billboard hits",
        "trending songs"
    ]

    for term in fallback_terms:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": term,
                "media": "music",
                "entity": "song",
                "limit": 50
            },
            timeout=8
        )

        data = response.json()

        for item in data.get("results", []):
            track_name = item.get("trackName", "")
            artist_name = item.get("artistName", "")

            if not track_name or not artist_name:
                continue

            if track_name.lower() in blocked_titles:
                continue

            already_added = any(
                rec["title"].lower() == track_name.lower()
                and rec["artist"].lower() == artist_name.lower()
                for rec in recommendations
            )

            if already_added:
                continue

            recommendations.append({
                "title": track_name,
                "artist": artist_name,
                "genre": item.get("primaryGenreName"),
                "previewUrl": item.get("previewUrl"),
                "artworkUrl": item.get("artworkUrl100")
            })

            if len(recommendations) >= 12:
                return jsonify(recommendations)

    return jsonify(recommendations)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)