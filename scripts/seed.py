"""Seed the database with realistic volume for explain() checks.

Run every command from the project root, so .env and the app imports are found.
It targets the database named by DATABASE_NAME in .env: check it before running.

Create the seed (refuses if the users collection already has data):
    python -m scripts.seed

Wipe everything, then seed again:
    python -m scripts.seed --reset

Remove the seed without re-seeding:
    python -m scripts.seed --clear

Change the volume (defaults: 5000 users, 50000 notes, 20000 posts):
    python -m scripts.seed --reset --users 1000 --notes 10000 --posts 5000

--reset and --clear delete ALL users, notes and posts, not only seeded ones.
Indexes are kept, because delete_all() removes documents, not the collection.
Seeded logins: admin@seed.dev (admin) and user<N>@seed.dev, all with Password123.
"""

import argparse
import asyncio
import random
from collections import Counter
from datetime import datetime, timedelta

from beanie import Document, PydanticObjectId

from app.common.enum import UserRole
from app.common.utils import utc_now
from app.core.database import mongodb
from app.core.security import hash_pass
from app.modules.note.models import Note
from app.modules.post.models import Post
from app.modules.user.models import User

SEED_PASSWORD = "Password123"
ADMIN_EMAIL = "admin@seed.dev"
BATCH_SIZE = 1_000

INTERESTS = [
    "music",
    "travel",
    "cooking",
    "fitness",
    "reading",
    "gaming",
    "photography",
    "movies",
    "hiking",
    "coding",
    "art",
    "football",
    "cricket",
    "gardening",
    "history",
    "science",
    "fashion",
    "chess",
    "cycling",
    "writing",
]
FIRST_NAMES = [
    "Ayesha",
    "Rahim",
    "Karim",
    "Nadia",
    "Sam",
    "Lina",
    "Omar",
    "Mina",
    "Alex",
    "Rina",
]
LAST_NAMES = ["Hossain", "Rahman", "Khan", "Ahmed", "Islam", "Chowdhury", "Das", "Roy"]
WORDS = [
    "idea",
    "plan",
    "meeting",
    "draft",
    "project",
    "review",
    "update",
    "list",
    "task",
    "summary",
    "note",
    "travel",
    "recipe",
    "book",
    "design",
    "server",
    "index",
    "query",
    "cursor",
    "schema",
    "pipeline",
]


def sentence(min_words: int, max_words: int) -> str:
    words = random.choices(WORDS, k=random.randint(min_words, max_words))
    return " ".join(words).capitalize()


def sorted_dates(count: int, days_back: int = 365) -> list[datetime]:
    # Sorted so ids created in this order line up with created_at.
    now = utc_now()
    span = days_back * 86_400
    return sorted(
        now - timedelta(seconds=random.randint(0, span)) for _ in range(count)
    )


def skewed_owners(
    user_ids: list[PydanticObjectId], count: int
) -> list[PydanticObjectId]:
    # Long tail: a few users own most documents, most users own a handful.
    weights = [1 / rank for rank in range(1, len(user_ids) + 1)]
    random.shuffle(weights)
    return random.choices(user_ids, weights=weights, k=count)


def build_users(count: int, pass_hash: str) -> list[User]:
    return [
        User(
            id=PydanticObjectId(),
            name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            email=ADMIN_EMAIL if i == 0 else f"user{i}@seed.dev",
            pass_hash=pass_hash,
            role=UserRole.ADMIN if i == 0 else UserRole.USER,
            interests=random.sample(INTERESTS, k=random.randint(0, 4)),
        )
        for i in range(count)
    ]


def build_notes(user_ids: list[PydanticObjectId], count: int) -> list[Note]:
    owners = skewed_owners(user_ids, count)
    return [
        Note(
            id=PydanticObjectId(),
            title=sentence(2, 6),
            content=sentence(10, 40),
            owner_id=owner,
            created_at=created,
            updated_at=created,
        )
        for owner, created in zip(owners, sorted_dates(count))
    ]


def build_posts(user_ids: list[PydanticObjectId], count: int) -> list[Post]:
    authors = skewed_owners(user_ids, count)
    return [
        Post(
            id=PydanticObjectId(),
            title=sentence(3, 8),
            content=sentence(20, 80),
            author_id=author,
            created_at=created,
        )
        for author, created in zip(authors, sorted_dates(count))
    ]


async def insert_in_batches(model: type[Document], docs: list[Document]) -> None:
    for start in range(0, len(docs), BATCH_SIZE):
        await model.insert_many(docs[start : start + BATCH_SIZE])
    print(f"  {model.Settings.name}: {len(docs)} inserted")


async def seed(args: argparse.Namespace) -> None:
    random.seed(args.random_seed)
    await mongodb.connect()  # init_beanie also creates the declared indexes
    try:
        if await User.count() and not (args.reset or args.clear):
            print("Database already has data. Re-run with --reset to wipe it.")
            return
        if args.reset or args.clear:
            # delete_all keeps the indexes; drop() would remove them.
            for model in (User, Note, Post):
                await model.delete_all()
        if args.clear:
            print("Removed all users, notes and posts. Indexes kept.")
            return

        pass_hash = await hash_pass(SEED_PASSWORD)  # hash once, not per user
        users = build_users(args.users, pass_hash)
        user_ids = [user.id for user in users]
        posts = build_posts(user_ids, args.posts)

        await insert_in_batches(User, users)
        await insert_in_batches(Note, build_notes(user_ids, args.notes))
        await insert_in_batches(Post, posts)

        heavy_author, post_count = Counter(p.author_id for p in posts).most_common(1)[0]
        print(f"\nLogin: {ADMIN_EMAIL} / {SEED_PASSWORD} (admin)")
        print(
            f"Heaviest author (use for $lookup explain): {heavy_author} with {post_count} posts"
        )

        # Compare against the declared indexes: nothing more, nothing less.
        for model in (User, Note, Post):
            indexes = await model.get_pymongo_collection().index_information()
            print(f"{model.Settings.name} indexes: {list(indexes)}")
    finally:
        await mongodb.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the note-taking database")
    parser.add_argument("--users", type=int, default=5_000)
    parser.add_argument("--notes", type=int, default=50_000)
    parser.add_argument("--posts", type=int, default=20_000)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--reset", action="store_true", help="wipe existing data first")
    parser.add_argument("--clear", action="store_true", help="wipe data and exit")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(seed(parse_args()))
