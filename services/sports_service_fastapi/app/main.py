from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEOS_FALLBACK = {
    "Yoga": [
        {"title": "Yoga pour débutants complet", "videoId": "Yzm3fA2HhkQ"},
        {"title": "Yoga matinal énergisant", "videoId": "4C-gxOE0j7s"},
        {"title": "Yoga relaxation du soir", "videoId": "Ji5y90va_X8"},
        {"title": "Yoga flow doux 20 min", "videoId": "X655B4ISakg"},
        {"title": "Yoga étirements complets", "videoId": "j7rKKpwdXNE"},
        {"title": "Hatha Yoga débutant", "videoId": "v7AYKMP6rOE"},
    ],
    "Cardio": [
        {"title": "30 MIN CARDIO WORKOUT", "videoId": "8CtBqczAjbs"},
        {"title": "Cardio Training intensif", "videoId": "hbV16grOT5Y"},
        {"title": "Cardio sans équipement", "videoId": "gOqJ7V1X2RI"},
        {"title": "Fat Burning Cardio Workout", "videoId": "YBnSUIVXfXk"},
        {"title": "20 Min Cardio maison", "videoId": "6buOGGOwmXI"},
        {"title": "HIIT Cardio rapide", "videoId": "ml6cT4AZdqI"},
    ],
    "HIIT": [
        {"title": "20 MIN HIIT WORKOUT", "videoId": "M0uO8X3_tEA"},
        {"title": "HIIT Full Body No Equipment", "videoId": "ml6cT4AZdqI"},
        {"title": "15 MIN HIIT Workout", "videoId": "cZnsLVArIt8"},
        {"title": "HIIT Cardio and Abs", "videoId": "q1g_gLrj2E0"},
        {"title": "HIIT débutant sans sauts", "videoId": "aUb0q7MYh5o"},
        {"title": "Tabata HIIT intense", "videoId": "RBMmgRUudJk"},
    ],
    "Musculation": [
        {"title": "FULL BODY WORKOUT 30 Min", "videoId": "R27HBJEwR_w"},
        {"title": "Musculation sans matériel", "videoId": "IODxDxX7oi4"},
        {"title": "Renforcement musculaire", "videoId": "YYOnTr4ASTY"},
        {"title": "Upper Body Workout", "videoId": "TvOhJgVAmWc"},
        {"title": "Musculation jambes fessiers", "videoId": "lCg_gh98PhQ"},
        {"title": "Abs and Core Workout", "videoId": "DHD1-2P94DI"},
    ],
    "Étirements": [
        {"title": "Full Body Stretch 15 MIN", "videoId": "qULTwquOuT4"},
        {"title": "Morning Yoga Stretch", "videoId": "g_tea8ZNk5A"},
        {"title": "Étirements dos et jambes", "videoId": "4pKly2JojMw"},
        {"title": "Flexibility Routine", "videoId": "L_xrDAtykMI"},
        {"title": "Stretching relaxation", "videoId": "Ji5y90va_X8"},
        {"title": "Deep Stretch Yoga", "videoId": "j7rKKpwdXNE"},
    ],
    "Pilates": [
        {"title": "Pilates débutant 20 min", "videoId": "0EFZ5hTHxw4"},
        {"title": "Pilates Abs and Core", "videoId": "Bw4M0aGplLQ"},
        {"title": "Full Body Pilates Workout", "videoId": "nks00R7oQq0"},
        {"title": "Pilates Mat Flow", "videoId": "4wkTgDUSMPM"},
        {"title": "Pilates pour tonifier", "videoId": "FmF3xlCF7kw"},
        {"title": "Beginner Pilates", "videoId": "K56Z12XsB8s"},
    ],
    "Danse Fitness": [
        {"title": "ZUMBA FITNESS PARTY", "videoId": "VY1eFxgRR-k"},
        {"title": "Dance Workout Fun", "videoId": "O-mr11DEoZI"},
        {"title": "Cardio Dance 30 Minutes", "videoId": "t1JghzZCWYw"},
        {"title": "Zumba pour débutants", "videoId": "S_fYKoXohT4"},
        {"title": "Dance Fitness Party", "videoId": "1JoVbWm-BYc"},
        {"title": "Fun Dance Cardio", "videoId": "r_4a4O7kXQo"},
    ],
    "Marche Active": [
        {"title": "30 MIN WALKING WORKOUT", "videoId": "vvkT5P3IiIo"},
        {"title": "Walk at Home Cardio", "videoId": "R1W2rVy4I8M"},
        {"title": "Indoor Walking Exercise", "videoId": "Cuf3PIMXpCg"},
        {"title": "Walking Workout 20 Min", "videoId": "Pk6T_M6R_ok"},
        {"title": "Marche sportive", "videoId": "yPq9m_Ud91U"},
        {"title": "Power Walking Indoor", "videoId": "9K0lC1zpgTE"},
    ],
}

def obtener_videos_fallback(categoria: str):
    videos_bruts = VIDEOS_FALLBACK.get(categoria, VIDEOS_FALLBACK["Cardio"])
    videos = []
    for v in videos_bruts:
        vid = v["videoId"]
        videos.append({
            "title": v["title"],
            "image": f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
            "videoId": vid,
            "link": f"https://www.youtube.com/watch?v={vid}",
            "category": categoria
        })
    return videos

def rechercher_videos_youtube(requete: str, categoria: str, max_results: int = 6):
    url = f"https://yt-api.p.rapidapi.com/search?query={requete}&type=video"
    headers = {
        "x-rapidapi-key": "5bcfd3c0e4msh7db006c0824dd53ple3438jsn86c3ad93bfe8",
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }
    try:
        rep = requests.get(url, headers=headers, timeout=10)
        rep.raise_for_status()
        data = rep.json()
        videos = []
        for item in data.get("data", [])[:max_results]:
            thumbnail = item.get("thumbnail", [{}])
            if isinstance(thumbnail, list) and len(thumbnail) > 0:
                image_url = thumbnail[0].get("url", "")
            else:
                image_url = ""
            videos.append({
                "title": item.get("title", "Video"),
                "image": image_url,
                "videoId": item.get("videoId", ""),
                "link": f"https://www.youtube.com/watch?v={item.get('videoId', '')}",
                "category": categoria
            })
        if len(videos) > 0:
            print(f" {len(videos)} videos de API")
            return videos
        else:
            print(f" Usando fallback")
            return obtener_videos_fallback(categoria)
    except Exception as e:
        print(f" Error: {e}, usando fallback")
        return obtener_videos_fallback(categoria)

@app.get("/sports/recommendations")
def recommandations_sportives(age: int = Query(...), poids: int = Query(...), objectif: str = Query(...)):
    if age < 30:
        categorie = "HIIT"
    elif 30 <= age < 55:
        categorie = "Cardio"
    else:
        categorie = "Étirements"
    if objectif == "Perte de poids":
        categorie = "Cardio"
    elif objectif == "Gain de muscle":
        categorie = "Musculation"
    elif objectif == "Flexibilité":
        categorie = "Yoga"
    videos = obtener_videos_fallback(categorie)
    return {"categorie_recommandee": categorie, "videos": videos}

@app.get("/sports/category")
def videos_par_categorie(name: str = Query(...), age: int = Query(30), objectif: str = Query("Bien-être")):
    videos = obtener_videos_fallback(name)
    return {"categorie": name, "videos": videos}

@app.get("/sports/health")
def health_check():
    return {"status": "ok", "service": "sports"}
