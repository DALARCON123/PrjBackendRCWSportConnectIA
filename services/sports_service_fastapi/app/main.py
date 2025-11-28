from fastapi import FastAPI, Query
import requests

app = FastAPI()


# ------------------------------- YOUTUBE SEARCH -------------------------------
def rechercher_videos_youtube(requete: str):
    url = f"https://yt-api.p.rapidapi.com/search?query={requete}&type=video"
    headers = {
        "x-rapidapi-key": "TA_CLE_RAPIDAPI_ICI",
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }

    rep = requests.get(url, headers=headers)
    data = rep.json()

    videos = []

    for item in data.get("data", [])[:6]:
        videos.append({
            "title": item["title"],
            "image": item["thumbnail"]["url"],
            "videoId": item["videoId"],
            "link": f"https://www.youtube.com/watch?v={item['videoId']}"
        })

    return videos


# -------------------------- RECOMMANDATIONS GLOBALES --------------------------
@app.get("/sports/recommendations")
def recommandations_sportives(
    age: int = Query(...),
    poids: int = Query(...),
    objectif: str = Query(...)
):

    if age < 30:
        categorie = "HIIT pour débutants"
    elif 30 <= age < 55:
        categorie = "Cardio à faible impact"
    else:
        categorie = "Exercices doux pour seniors"

    if objectif == "Perte de poids":
        requete = "cardio pour perdre du poids"
    elif objectif == "Gain de muscle":
        requete = "musculation à la maison"
    else:
        requete = "exercices de bien-être"

    videos = rechercher_videos_youtube(requete)

    return {
        "categorie_recommandee": categorie,
        "videos": videos
    }


# ---------------------- VIDEOS PAR CATÉGORIE CLIQUÉE -------------------------
@app.get("/sports/category")
def videos_par_categorie(name: str):

    mapping = {
        "Yoga": "yoga débutants",
        "Cardio": "cardio maison",
        "HIIT": "séance HIIT",
        "Musculation": "musculation maison",
        "Étirements": "étirements complets",
        "Pilates": "pilates débutants",
        "Danse Fitness": "danse fitness exercices",
        "Marche Active": "walking workout indoor",
    }

    requete = mapping.get(name, name)
    videos = rechercher_videos_youtube(requete)

    return {
        "categorie": name,
        "videos": videos
    }
