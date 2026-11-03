from beanie import PydanticObjectId

from app.modules.post.models import Post


def interest_group_pipeline(
    interests: list[str] | None, skip: int, limit: int, users_per_group: int
) -> list[dict]:
    pipeline: list[dict] = []

    if interests:
        pipeline.append({"$match": {"interests": {"$in": interests}}})

    pipeline += [
        {"$project": {"name": 1, "interests": 1}},
        {"$unwind": "$interests"},
    ]

    if interests:
        pipeline.append({"$match": {"interests": {"$in": interests}}})

    pipeline += [
        {
            "$group": {
                "_id": "$interests",
                "users": {"$push": {"id": "$_id", "name": "$name"}},
                "user_count": {"$sum": 1},
            }
        },
        {"$sort": {"user_count": -1, "_id": 1}},
        {
            "$facet": {
                "metadata": [{"$count": "total"}],
                "data": [
                    {"$skip": skip},
                    {"$limit": limit},
                    {
                        "$project": {
                            "_id": 0,
                            "interest": "$_id",
                            "user_count": 1,
                            "users": {"$slice": ["$users", users_per_group]},
                        }
                    },
                ],
            }
        },
    ]
    return pipeline


def user_post_pipeline(user_id: PydanticObjectId, skip: int, limit: int) -> list[dict]:
    posts = Post.get_collection_name()

    return [
        {"$match": {"_id": user_id}},
        {"$project": {"name": 1}},
        {
            "$lookup": {
                "from": posts,
                "localField": "_id",
                "foreignField": "author_id",
                "pipeline": [
                    {"$sort": {"_id": -1}},
                    {"$skip": skip},
                    {"$limit": limit},
                    {
                        "$project": {
                            "_id": 0,
                            "id": "$_id",
                            "title": 1,
                            "content": 1,
                            "author_id": 1,
                            "created_at": 1,
                        }
                    },
                ],
                "as": "posts",
            }
        },
        {
            "$lookup": {
                "from": posts,
                "localField": "_id",
                "foreignField": "author_id",
                "pipeline": [{"$count": "total"}],
                "as": "post_count",
            }
        },
        {
            "$project": {
                "_id": 0,
                "user": {"id": "$_id", "name": "$name"},
                "posts": 1,
                "total": {"$ifNull": [{"$first": "$post_count.total"}, 0]},
            }
        },
    ]
