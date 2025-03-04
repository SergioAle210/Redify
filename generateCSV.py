import pandas as pd
import random
from faker import Faker
import os

# Inicializar Faker para generar datos aleatorios
fake = Faker()
Faker.seed(42)
random.seed(42)

# Crear carpeta de salida si no existe
output_dir = "./docs"
os.makedirs(output_dir, exist_ok=True)

# Definir la cantidad de nodos
users_count = 1500
posts_count = 1200
comments_count = 1000
groups_count = 600
reels_count = 700
influencers_no_verified_count = 100
influencers_verified_count = 100

# Generar Usuarios (User)
users = []
for i in range(users_count):
    users.append(
        {
            "id": i + 1,
            "nombre": fake.name(),
            "email": fake.email(),
            "fecha_registro": fake.date_between(start_date="-5y", end_date="today"),
            "intereses": ";".join(
                random.sample(
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
                )
            ),
        }
    )
df_users = pd.DataFrame(users)
df_users.to_csv(f"{output_dir}/users.csv", index=False)


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
            "usuario_id": random.randint(1, users_count),
        }
    )
df_posts = pd.DataFrame(posts)
df_posts.to_csv(f"{output_dir}/posts.csv", index=False)

# Generar Comentarios (Comment)
comments = []
for i in range(comments_count):
    comments.append(
        {
            "id": i + 1,
            "contenido": fake.sentence(nb_words=15),
            "fecha_comentario": fake.date_between(start_date="-5y", end_date="today"),
            "likes": random.randint(0, 500),
            "reacciones": ";".join(
                random.sample(
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
                )
            ),
            "usuario_id": random.randint(1, users_count),
            "post_id": random.randint(1, posts_count),
        }
    )
df_comments = pd.DataFrame(comments)
df_comments.to_csv(f"{output_dir}/comments.csv", index=False)

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
df_groups.to_csv(f"{output_dir}/groups.csv", index=False)

# Generar Reels (Reel)
reels = []
for i in range(reels_count):
    reels.append(
        {
            "id": i + 1,
            "duracion": round(random.uniform(5.0, 120.0), 2),
            "fecha_publicacion": fake.date_between(start_date="-5y", end_date="today"),
            "likes": random.randint(0, 5000),
            "hashtags": ";".join(
                random.sample(
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
                )
            ),
            "usuario_id": random.randint(1, users_count),
        }
    )
df_reels = pd.DataFrame(reels)
df_reels.to_csv(f"{output_dir}/reels.csv", index=False)

# Generar Relaciones (CSV)
relationships = {
    "friends": [],
    "follows": [],
    "likes": [],
    "commented_on": [],
    "belongs_to": [],
    "member_of": [],
    "created": [],
    "watched": [],
    "mentions": [],
    "posted": [],
}

# Generar Relaciones de Amistad (FRIENDS_WITH)
for _ in range(2000):
    u1, u2 = random.sample(range(1, users_count + 1), 2)
    relationships["friends"].append(
        {
            "usuario1_id": u1,
            "usuario2_id": u2,
            "desde": fake.date_between(start_date="-5y", end_date="today"),
            "nivel_confianza": random.randint(1, 10),
            "tipo_amistad": random.choice(
                ["Cercana", "Compañero de trabajo", "Conocido", "Mejor amigo"]
            ),
        }
    )

# Generar Relaciones de Seguimiento (FOLLOWS)
for _ in range(2500):
    u1, u2 = random.sample(range(1, users_count + 1), 2)
    relationships["follows"].append(
        {
            "usuario_id": u1,
            "seguido_id": u2,
            "desde": fake.date_between(start_date="-5y", end_date="today"),
            "interaccion_frecuencia": random.choice(
                ["Diaria", "Semanal", "Mensual", "Ocasional"]
            ),
            "razón": "Interés en su contenido",
        }
    )


# Generar Relaciones de Menciones (MENTIONS)
for _ in range(1500):
    u1, u2 = random.sample(range(1, users_count + 1), 2)
    relationships["mentions"].append(
        {
            "usuario_id": u1,
            "mencionado_id": u2,
            "fecha_mencion": fake.date_between(start_date="-5y", end_date="today"),
            "tipo_mencion": "Texto",
            "notificado": random.choice([True, False]),
        }
    )

# Generar Likes en Publicaciones
for _ in range(3000):
    u, p = random.randint(1, users_count), random.randint(1, posts_count)
    relationships["likes"].append(
        {
            "usuario_id": u,
            "contenido_id": p,
            "tipo_contenido": "Post",
            "fecha_like": fake.date_between(start_date="-5y", end_date="today"),
            "tipo": random.choice(["👍", "❤️", "😂", "😢", "😡", "🔥"]),
            "desde_movil": random.choice([True, False]),
        }
    )

# Generar Likes en Comentarios
for _ in range(2500):
    u, c = random.randint(1, users_count), random.randint(1, comments_count)
    relationships["likes"].append(
        {
            "usuario_id": u,
            "contenido_id": c,
            "tipo_contenido": "Comment",
            "fecha_like": fake.date_between(start_date="-5y", end_date="today"),
            "tipo": random.choice(["👍", "❤️", "😂", "😢", "😡", "🔥"]),
            "desde_movil": random.choice([True, False]),
        }
    )

# Generar Likes en Reels
for _ in range(2500):
    u, r = random.randint(1, users_count), random.randint(1, reels_count)
    relationships["likes"].append(
        {
            "usuario_id": u,
            "contenido_id": r,
            "tipo_contenido": "Reel",
            "fecha_like": fake.date_between(start_date="-5y", end_date="today"),
            "tipo": random.choice(["👍", "❤️", "😂", "😢", "😡", "🔥"]),
            "desde_movil": random.choice([True, False]),
        }
    )


# Generar Comentarios en Publicaciones
for _ in range(2000):
    u, p = random.randint(1, users_count), random.randint(1, posts_count)
    relationships["commented_on"].append(
        {
            "usuario_id": u,
            "contenido_id": p,
            "tipo_contenido": "Post",
            "fecha_comentario": fake.date_between(start_date="-5y", end_date="today"),
            "tipo": random.sample(
                ["Texto", "Sticker", "Emoji"], k=random.randint(1, 3)
            ),
            "editado": random.choice([True, False]),
        }
    )

# Generar Comentarios en Reels
for _ in range(1500):
    u, r = random.randint(1, users_count), random.randint(1, reels_count)
    relationships["commented_on"].append(
        {
            "usuario_id": u,
            "contenido_id": r,
            "tipo_contenido": "Reel",
            "fecha_comentario": fake.date_between(start_date="-5y", end_date="today"),
            "tipo": random.sample(
                ["Texto", "Sticker", "Emoji"], k=random.randint(1, 3)
            ),
            "editado": random.choice([True, False]),
        }
    )


# Generar Relaciones de Pertenencia a Publicaciones
for post in posts:
    relationships["belongs_to"].append(
        {
            "contenido_id": post["id"],
            "usuario_id": post["usuario_id"],
            "tipo_contenido": "Post",
            "fecha_creacion": post["fecha_publicacion"],
            "privado": post["privado"],
            "categoria": random.choice(
                ["Noticias", "Opinión", "Entretenimiento", "Deportes"]
            ),
        }
    )

# Generar Relaciones de Pertenencia a Comentarios
for comment in comments:
    relationships["belongs_to"].append(
        {
            "contenido_id": comment["id"],
            "usuario_id": comment["usuario_id"],
            "tipo_contenido": "Comment",
            "fecha_creacion": comment["fecha_comentario"],
            "privado": False,
            "categoria": random.choice(
                ["Noticias", "Opinión", "Entretenimiento", "Deportes"]
            ),
        }
    )

# Generar Relaciones de Membresía en Grupos (MEMBER_OF) asegurando que cada grupo tenga al menos un usuario
usuarios_disponibles = list(range(1, users_count + 1))
grupos_disponibles = list(range(1, groups_count + 1))

# Asignar al menos un usuario a cada grupo
for g in grupos_disponibles:
    u = random.choice(usuarios_disponibles)  # Seleccionar un usuario aleatorio
    relationships["member_of"].append(
        {
            "usuario_id": u,
            "grupo_id": g,
            "desde": fake.date_between(start_date="-5y", end_date="today"),
            "rol": random.choice(["Miembro", "Moderador", "Administrador"]),
            "activo": random.choice([True, False]),
        }
    )

# Generar relaciones adicionales hasta llegar a 2000
relaciones_faltantes = 2000 - len(relationships["member_of"])
for _ in range(relaciones_faltantes):
    u = random.choice(usuarios_disponibles)
    g = random.choice(grupos_disponibles)
    relationships["member_of"].append(
        {
            "usuario_id": u,
            "grupo_id": g,
            "desde": fake.date_between(start_date="-5y", end_date="today"),
            "rol": random.choice(["Miembro", "Moderador", "Administrador"]),
            "activo": random.choice([True, False]),
        }
    )


# Generar Relaciones de Creación de Reels (CREATED)
for reel in reels:
    relationships["created"].append(
        {
            "usuario_id": reel["usuario_id"],
            "reel_id": reel["id"],
            "fecha_creacion": reel["fecha_publicacion"],
            "visibilidad": random.choice(["Público", "Privado"]),
            "ubicacion": random.choice(["Guatemala", "México", "EE.UU", "España"]),
        }
    )

# Generar Relaciones de Visualización de Reels (WATCHED)
for _ in range(2500):
    u = random.randint(1, users_count)
    r = random.randint(1, reels_count)
    relationships["watched"].append(
        {
            "usuario_id": u,
            "reel_id": r,
            "fecha_vista": fake.date_between(start_date="-5y", end_date="today"),
            "duracion_vista": random.randint(1, 120),
            "completo": random.choice([True, False]),
        }
    )


# Generar Relaciones de Publicación de Posts (POSTED)
for post in posts:
    relationships["posted"].append(
        {
            "usuario_id": post["usuario_id"],
            "post_id": post["id"],
            "fecha_posteo": post["fecha_publicacion"],
            "visibilidad": random.choice(["Público", "Privado"]),
            "ubicacion": random.choice(["Guatemala", "México", "EE.UU", "España"]),
        }
    )

# Generar usuarios influencers NO verificados
influencers_no_verified = []
for i in range(influencers_no_verified_count):
    influencers_no_verified.append(
        {
            "id": i + 1 + users_count,  # IDs 1 a 150 para no verificados
            "nombre": fake.name(),
            "email": fake.email(),
            "fecha_registro": fake.date_between(start_date="-5y", end_date="today"),
            "intereses": ";".join(
                random.sample(
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
                )
            ),
        }
    )
df_influencers_no_verified = pd.DataFrame(influencers_no_verified)
df_influencers_no_verified.to_csv(f"{output_dir}/influencers_no.csv", index=False)

# Generar usuarios influencers VERIFICADOS
influencers_verified = []
# Para evitar conflicto de IDs, se asigna un offset (por ejemplo, a partir del 151)
for i in range(influencers_verified_count):
    influencers_verified.append(
        {
            "id": i + 1 + influencers_no_verified_count + users_count,  # IDs 151 a 300
            "nombre": fake.name(),
            "email": fake.email(),
            "fecha_registro": fake.date_between(start_date="-5y", end_date="today"),
            "intereses": ";".join(
                random.sample(
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
                )
            ),
        }
    )
df_influencers_verified = pd.DataFrame(influencers_verified)
df_influencers_verified.to_csv(f"{output_dir}/influencers_verified.csv", index=False)


# Guardar relaciones en CSV
for rel, data in relationships.items():
    df_rel = pd.DataFrame(data)
    df_rel.to_csv(f"{output_dir}/{rel}.csv", index=False)

print("Archivos CSV con relaciones generados correctamente ✅")


# Reinicializar la lista de follows para influencers
follows_influencers = []

# Obtener IDs de influencers de cada grupo
influencer_no_verified_ids = df_influencers_no_verified["id"].tolist()
influencer_verified_ids = df_influencers_verified["id"].tolist()
# Unir ambos conjuntos (total 200)
all_influencer_ids = influencer_no_verified_ids + influencer_verified_ids

for influencer_id in all_influencer_ids:
    # Seleccionar un número aleatorio de seguidores entre 5 y 15
    num_followers = random.randint(5, 15)
    # Candidatos: usuarios con IDs del 1 al 1500
    candidate_followers = list(range(1, users_count + 1))
    # Evitar que el influencer se siga a sí mismo (en caso de que su ID esté en ese rango)
    if influencer_id in candidate_followers:
        candidate_followers.remove(influencer_id)
    followers = random.sample(candidate_followers, num_followers)

    # Determinar el estado de verificación del influencer
    verified_status = (
        "Verified" if influencer_id in influencer_verified_ids else "No Verified"
    )

    for follower in followers:
        follows_influencers.append(
            {
                "usuario_id": follower,
                "seguido_id": influencer_id,
                "desde": fake.date_between(start_date="-5y", end_date="today"),
                "interaccion_frecuencia": random.choice(
                    ["Diaria", "Semanal", "Mensual", "Ocasional"]
                ),
                "razón": "Interés en su contenido",
                "estado": verified_status,  # Se asigna Verified o No Verified
            }
        )

df_follows = pd.DataFrame(follows_influencers)
df_follows.to_csv(f"{output_dir}/follows_influencers.csv", index=False)
print("Archivo follows_influencers.csv generado correctamente")


print(
    "Archivos CSV para influencers (verificados y no verificados) y relaciones follows generados correctamente ✅"
)
