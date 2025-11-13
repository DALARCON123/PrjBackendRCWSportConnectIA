from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

SPORTS = [
    {"id":"run","name":"Running","level":"beginner"},
    {"id":"yoga","name":"Yoga","level":"all"},
    {"id":"swim","name":"Natación","level":"all"},
    {"id":"strength","name":"Fuerza","level":"intermediate"},
]

@app.get("/sports")
def list_sports():
    return SPORTS

@app.get("/sports/search")
def search(q: str = Query('')):
    ql = q.lower()
    return [s for s in SPORTS if ql in s["name"].lower()]
