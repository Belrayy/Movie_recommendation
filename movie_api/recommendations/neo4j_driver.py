import os
from neo4j import GraphDatabase # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def get_session():
    return driver.session(database="movies")
