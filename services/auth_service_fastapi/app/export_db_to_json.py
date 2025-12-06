# -----------------------------------------------------------
# export_db_to_json.py
# Exporta toda la base de datos auth.db en formato JSON
# -----------------------------------------------------------

import json
from pathlib import Path

from .db import SessionLocal
from .models import User, Notification
from sqlalchemy.orm import class_mapper


def as_dict(model):
  """Convierte un modelo SQLAlchemy en diccionario JSON."""
  return {c.key: getattr(model, c.key) for c in class_mapper(model.__class__).columns}


def main():
  db = SessionLocal()

  data = {
      "users": [as_dict(u) for u in db.query(User).all()],
      "notifications": [as_dict(n) for n in db.query(Notification).all()],
  }

  output_path = Path(__file__).parent / "auth_export.json"

  with open(output_path, "w", encoding="utf-8") as f:
      # 🔥 default=str = convierte datetime (y otros tipos) a texto
      json.dump(data, f, indent=4, ensure_ascii=False, default=str)

  print(f"✅ Exportación completada → {output_path}")


if __name__ == "__main__":
  main()
