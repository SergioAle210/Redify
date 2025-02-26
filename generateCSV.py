import pandas as pd
import random
from faker import Faker

# Inicializar Faker para generar datos aleatorios
fake = Faker()
Faker.seed(42)
random.seed(42)

# Definir el número total de nodos
TOTAL_NODES = 5000
users_count = 1500
posts_count = 1200
comments_count = 1000
groups_count = 600
reels_count = 700

# Generar Usuarios (User)
users = []
for i in range(users_count):
    users.append(
        {
            "id": i + 1,
            "nombre": fake.name(),
            "email": fake.email(),
            "fecha_registro": fake.date_between(start_date="-5y", end_date="today"),
            "intereses": random.sample(
                [
                    "fútbol",
                    "programación",
                    "cine",
                    "música",
                    "viajes",
                    "lectura",
                    "fotografía",
                    "baloncesto",
                    "videojuegos",
                    "historia",
                    "cocina",
                    "anime",
                    "automovilismo",
                    "ciencia ficción",
                    "arte digital",
                    "senderismo",
                    "astronomía",
                    "idiomas",
                    "tecnología",
                    "eSports",
                    "diseño gráfico",
                    "guitarra",
                    "baile",
                    "escalada",
                    "psicología",
                    "moda",
                ],
                k=random.randint(1, 4),
            ),
        }
    )
df_users = pd.DataFrame(users)
df_users.to_csv("./docs/users.csv", index=False)

# Generar Publicaciones (Post)
posts = []
for i in range(posts_count):
    posts.append(
        {
            "id": i + 1,
            "contenido": fake.sentence(nb_words=10),
            "fecha_publicacion": fake.date_between(start_date="-5y", end_date="today"),
            "likes": random.randint(0, 1000),
            "privado": random.choice([True, False]),
        }
    )
df_posts = pd.DataFrame(posts)
df_posts.to_csv("./docs/posts.csv", index=False)

# Generar Comentarios (Comment)
comments = []
for i in range(comments_count):
    comments.append(
        {
            "id": i + 1,
            "contenido": fake.sentence(nb_words=15),
            "fecha_comentario": fake.date_between(start_date="-5y", end_date="today"),
            "likes": random.randint(0, 500),
            "reacciones": random.sample(
                [
                    "👍",
                    "❤️",
                    "😂",
                    "😢",
                    "😡",
                    "🔥",
                    "😍",
                    "🤯",
                    "👏",
                    "🎉",
                    "💯",
                    "😎",
                    "🙌",
                    "🤔",
                ],
                k=random.randint(1, 3),
            ),
        }
    )
df_comments = pd.DataFrame(comments)
df_comments.to_csv("./docs/comments.csv", index=False)

# Generar Grupos (Group)
groups = []
for i in range(groups_count):
    groups.append(
        {
            "id": i + 1,
            "nombre": fake.company(),
            "descripcion": fake.sentence(nb_words=12),
            "privado": random.choice([True, False]),
            "miembros": random.randint(10, 1000),
        }
    )
df_groups = pd.DataFrame(groups)
df_groups.to_csv("./docs/groups.csv", index=False)

# Generar Reels (Reel)
reels = []
for i in range(reels_count):
    reels.append(
        {
            "id": i + 1,
            "duracion": round(random.uniform(5.0, 120.0), 2),
            "fecha_publicacion": fake.date_between(start_date="-5y", end_date="today"),
            "likes": random.randint(0, 5000),
            "hashtags": random.sample(
                [
                    "#divertido",
                    "#música",
                    "#viral",
                    "#fitness",
                    "#comedia",
                    "#tecnología",
                    "#viajes",
                    "#gaming",
                    "#arte",
                    "#programación",
                    "#cine",
                    "#libros",
                    "#deportes",
                    "#innovación",
                    "#desarrollo",
                    "#salud",
                    "#aprendizaje",
                    "#fotografía",
                    "#naturaleza",
                    "#aventura",
                    "#motivation",
                ],
                k=random.randint(1, 4),
            ),
        }
    )
df_reels = pd.DataFrame(reels)
df_reels.to_csv("./docs/reels.csv", index=False)

print("Archivos CSV generados correctamente ✅")
