from django.shortcuts import render # type: ignore
from rest_framework.decorators import api_view # type: ignore
from rest_framework.response import Response # type: ignore
from .neo4j_driver import get_session

# Create your views here.

@api_view(['POST'])
def add_movie(request):
   
    return Response({"message": "Movie added"})

@api_view(['GET'])
def get_movie_short_by_id(request, movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return Response({"error": "Invalid id"}, status=400)

    query = """
    MATCH (m:Movie)
    WHERE toInteger(m.id) = $movie_id
    RETURN m.id AS id, m.original_title AS title
    """

    with get_session() as session:
        record = session.run(query, movie_id=movie_id).single()

    if record is None:
        return Response({"error": "Movie not found"}, status=404)

    return Response({
        "id": record["id"],
        "title": record["title"]
    })

@api_view(['GET'])
def get_movie_full_by_id(request, movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return Response({"error": "Invalid id"}, status=400)

    query = """
    MATCH (m:Movie)
    WHERE toInteger(m.id) = $movie_id
    RETURN m.id AS id, m.original_title AS title,m.adult AS adult,m.budget AS budget,m.genres AS genres,
    m.original_language AS original_language,m.overview AS overview,m.popularity AS popularity,toString(m.release_date) AS release_date,
    m.revenue AS revenue,m.runtime AS runtime,m.vote_average AS vote_average,m.vote_count AS vote_count,m.poster_path AS poster_path
    """

    with get_session() as session:
        record = session.run(query, movie_id=movie_id).single()

    if record is None:
        return Response({"error": "Movie not found"}, status=404)

    return Response({
        "id": record["id"],
        "title": record["title"],
        "adult": record["adult"],
        "budget": record["budget"],
        "genres": record["genres"],
        "original_language": record["original_language"],
        "overview": record["overview"],
        "popularity": record["popularity"],
        "release_date": record["release_date"],
        "revenue": record["revenue"],
        "runtime": record["runtime"],
        "vote_average": record["vote_average"],
        "vote_count": record["vote_count"],
        "poster_path": record["poster_path"],
    })

@api_view(['GET'])
def get_link_by_id(request, movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return Response({"error": "Invalid id"}, status=400)


    query = """
    MATCH (m:Link)
    WHERE toInteger(m.movieId) = $movie_id
    RETURN m.imdbId AS imdbId, m.tmdbId AS tmdbId
    """

    with get_session() as session:
        record = session.run(query, movie_id=movie_id).single()

    if record is None:
        return Response({"error": "Links not found"}, status=404)

    return Response({
        "imdbId": record["imdbId"],
        "tmdbId": record["tmdbId"],
    })

@api_view(['GET'])
def get_keyword_by_id(request, movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return Response({"error": "Invalid id"}, status=400)

    query = """
    MATCH (k:Keyword)
    WHERE toInteger(k.id) = $movie_id
    RETURN k.id AS id, k.keywords AS keywords
    """

    with get_session() as session:
        records = session.run(query, movie_id=movie_id).values()

    keywords = [{"id": record[0], "keywords": record[1]} for record in records]

    return Response({"keywords": keywords})

@api_view(['GET'])
def get_credit_by_id(request, movie_id):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return Response({"error": "Invalid id"}, status=400)

    query = """
    MATCH (c:Credit)
    WHERE toInteger(c.id) = $movie_id
    RETURN c.id AS id, c.cast AS cast, c.crew AS crew
    """

    with get_session() as session:
        records = session.run(query, movie_id=movie_id).values()

    credits = [{"id": record[0], "cast": record[1], "crew": record[2]} for record in records]

    return Response({"credits": credits})

@api_view(['GET'])
def get_rating_by_movieid_userid(request, movie_id, user_id):

    query = """
    MATCH (r:Rating)
    WHERE toInteger(r.userId) = $user_id
      AND toInteger(r.movieId) = $movie_id
    RETURN r.userId AS userId,
           r.movieId AS movieId,
           r.rating AS rating,
           r.timestamp AS timestamp
    """

    with get_session() as session:
        record = session.run(
            query,
            user_id=int(user_id),
            movie_id=int(movie_id)
        ).single()

    if record is None:
        return Response({"error": "Rating not found"}, status=404)

    return Response({
        "userId": record["userId"],
        "movieId": record["movieId"],
        "rating": record["rating"],
        "timestamp": record["timestamp"],
    })

@api_view(['POST'])
def add_movie_to_list(request):
    list_id = request.data.get("list_id")
    movie_id = request.data.get("movie_id")

    query = """
    MATCH (l:List {id: $list_id})
    MATCH (m:Movie)
    WHERE toInteger(m.id) = $movie_id
    MERGE (l)-[:CONTAINS]->(m)
    """

    with get_session() as session:
        session.run(query, list_id=list_id, movie_id=int(movie_id))

    return Response({"message": "Movie added to list"})

@api_view(['GET'])
def get_list_genres(request, list_id):
    query = """
    MATCH (l:List {id: $list_id})-[:CONTAINS]->(m:Movie)
    UNWIND m.genres AS genre
    RETURN genre.name AS genre, count(*) AS frequency
    ORDER BY frequency DESC
    """

    with get_session() as session:
        records = session.run(query, list_id=list_id).values()

    return Response([
        {"genre": r[0], "count": r[1]} for r in records
    ])

@api_view(['GET'])
def get_list_genres(request, list_id):
    query = """
    MATCH (l:List {id: $list_id})-[:CONTAINS]->(m:Movie)
    UNWIND m.genres AS genre
    RETURN genre.name AS genre, count(*) AS frequency
    ORDER BY frequency DESC
    """

    with get_session() as session:
        records = session.run(query, list_id=list_id).values()

    return Response([
        {"genre": r[0], "count": r[1]} for r in records
    ])

@api_view(['GET'])
def recommend_from_list(request, list_id):
    query = """
    MATCH (l:List {id: $list_id})-[:CONTAINS]->(m:Movie)
    UNWIND m.genres AS g
    WITH g.name AS genre, count(*) AS freq
    ORDER BY freq DESC
    LIMIT 1

    MATCH (rec:Movie)
    WHERE any(x IN rec.genres WHERE x.name = genre)
      AND NOT ( (l)-[:CONTAINS]->(rec) )
    RETURN rec.id AS id,
           rec.original_title AS title,
           rec.vote_average AS rating
    ORDER BY rec.vote_average DESC
    LIMIT 10
    """

    with get_session() as session:
        records = session.run(query, list_id=list_id).values()

    return Response([
        {"id": r[0], "title": r[1], "rating": r[2]} for r in records
    ])


@api_view(['GET'])
def recommend_weighted(request, list_id):
    query = """
    MATCH (l:List {id: $list_id})-[:CONTAINS]->(m:Movie)
    UNWIND m.genres AS g
    WITH g.name AS genre, count(*) AS weight

    MATCH (rec:Movie)
    WHERE any(x IN rec.genres WHERE x.name = genre)
      AND NOT ( (l)-[:CONTAINS]->(rec) )
    RETURN rec.id AS id,
           rec.original_title AS title,
           sum(weight) AS score,
           rec.vote_average AS rating
    ORDER BY score DESC, rating DESC
    LIMIT 10
    """

    with get_session() as session:
        records = session.run(query, list_id=list_id).values()

    return Response([
        {"id": r[0], "title": r[1], "score": r[2], "rating": r[3]} for r in records
    ])

@api_view(['GET'])
def recommend_similar_movie(request, movie_id):
    query = """
    MATCH (m:Movie)
    WHERE toInteger(m.id) = $movie_id
    UNWIND m.genres AS g

    MATCH (rec:Movie)
    WHERE rec <> m
      AND any(x IN rec.genres WHERE x.name = g.name)
    RETURN rec.id AS id, rec.original_title AS title
    ORDER BY rec.vote_average DESC
    LIMIT 10
    """

    with get_session() as session:
        records = session.run(query, movie_id=int(movie_id)).values()

    return Response([
        {"id": r[0], "title": r[1]} for r in records
    ])
