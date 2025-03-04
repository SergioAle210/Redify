# Redify - Proyecto Neo4j y Django

Este proyecto implementa una red social utilizando Neo4j como base de datos gráfica y Django como backend. Se ha generado un conjunto de nodos y relaciones a través de un script de generación de CSV, y se han implementado diversos endpoints en el backend para crear, consultar, actualizar y eliminar nodos y relaciones.

## Integrantes

- Sergio Orellana - 221122
- Andre Marroquin - 22266
- Joaquin Campos - 22155

## 1. Generación de Datos (generate.CSV)

Se creó un script en Python que genera archivos CSV para poblar la base de datos con los siguientes elementos:

### Nodos

- **User (Usuario)**  
  **Label:** `Usuario`  
  **Propiedades:**

  - **id:** Integer
  - **nombre:** String
  - **email:** String
  - **fecha_registro:** Fecha
  - **intereses:** Lista de Strings

- **User:Influencer:Verified (Usuario:Influencers:Verificados)**  
  **Labels:** `Usuario`, `Influencers`, `Verificados`  
  **Propiedades:** (mismas que User)
- **User:Influencer (Usuario:Influencers)**  
  **Labels:** `Usuario`, `Influencers`  
  **Propiedades:** (mismas que User)
- **Post**  
  **Label:** `Post`  
  **Propiedades:**

  - **id:** Integer
  - **contenido:** String
  - **fecha_publicacion:** Fecha
  - **likes:** Integer
  - **privado:** Boolean

- **Comment (Comentario)**  
  **Label:** `Comment`  
  **Propiedades:**

  - **id:** Integer
  - **contenido:** String
  - **fecha_comentario:** Fecha
  - **likes:** Integer
  - **privado:** Boolean

- **Reel**  
  **Label:** `Reel`  
  **Propiedades:**

  - **id:** Integer
  - **duracion:** Float
  - **fecha_publicacion:** Fecha
  - **likes:** Integer
  - **hashtags:** Lista de Strings

- **Group (Grupo)**  
  **Label:** `Group`  
  **Propiedades:**

  - **id:** Integer
  - **nombre:** String
  - **descripcion:** String
  - **privado:** Boolean
  - **miembros:** Integer

### Relaciones

- **Mentions (Menciona)**  
  **Entre:** User → User  
  **Propiedades:**

  - **fecha_mencion:** Fecha
  - **tipo_mencion:** String
  - **notificado:** Boolean

- **Friends_with (Amistad)**  
  **Entre:** User → User  
  **Propiedades:**

  - **desde:** Fecha
  - **nivel_confianza:** Integer
  - **tipo_amistad:** String

- **Follows (Sigue)**  
  **Entre:**

  - Usuarios normales siguen a Usuarios Verificados o Influencers (verificados o no)
  - Influencers no verificados pueden seguir entre sí y a verificados  
    **Propiedades:**
  - **desde:** Fecha
  - **interaccion_frecuencia:** String
  - **razon:** String

- **Posted (Publicó)**  
  **Entre:** User → Post  
  **Propiedades:**

  - **fecha_posteo:** Fecha
  - **visibilidad:** String
  - **ubicacion:** String

- **Likes (Me gusta)**  
  **Entre:** User → (Post, Comment, Reel)  
  **Propiedades:**

  - **fecha_like:** Fecha
  - **tipo:** String
  - **desde_movil:** Boolean
  - _(Para Comment y Reel se puede incluir la propiedad "editado": Boolean)_

- **Commented_on (Comentó)**  
  **Entre:**

  - User → Post
  - User → Reel  
    **Propiedades:**
  - **fecha_comentario:** Fecha
  - **tipo:** String
  - **editado:** Boolean
  - _(En el caso de Post, también se puede incluir "categoría": String)_

- **Watched (Vio)**  
  **Entre:** User → Reel  
  **Propiedades:**

  - **fecha_vista:** Fecha
  - **duracion_vista:** Float
  - **completo:** Boolean

- **Created (Creó)**  
  **Entre:** User → Reel  
  **Propiedades:**

  - **fecha_creacion:** Fecha
  - **visibilidad:** String
  - **ubicacion:** String

- **Member_of (Miembro de)**  
  **Entre:** User → Group  
  **Propiedades:**

  - **desde:** Fecha
  - **rol:** String
  - **activo:** Boolean

- **Belongs_to (Pertenece a)**  
  **Entre:**

  - Post → User
  - Comment → User  
    **Propiedades:**
  - **fecha_creacion:** Fecha
  - **privado:** Boolean
  - **categoria:** String

_Nota:_ Algunos nodos (como Reel y Group) solo participan en relaciones, por lo que no tienen una relación **Belongs_to**.

El script `generateCSV.py` genera todos estos nodos y relaciones con sus propiedades, y además especifica el tipo de cada propiedad (por ejemplo, "Integer", "String", "Fecha", "Boolean", "Lista de Strings") y el nombre del nodo (etiqueta) para posteriormente hacer la inserción en AuraDB.

---

## 2. Endpoints del Backend

El proyecto cuenta con un backend en Django que expone múltiples endpoints para interactuar con la base de datos Neo4j. A continuación, se describen los principales endpoints y lo que hacen:

### a. Creación de Nodos

- **Crear Nodo con Una Sola Label**  
  **Método:** POST  
  **Endpoint:** `/api/create-node-single-label/`  
  **Descripción:** Crea un nodo asignándole únicamente una etiqueta.  
  **Entrada:** Un JSON con el campo `label`.
- **Crear Nodo con Múltiples Labels**  
  **Método:** POST  
  **Endpoint:** `/api/create-node-multiple-labels/`  
  **Descripción:** Crea un nodo asignándole dos o más etiquetas.  
  **Entrada:** Un JSON con el campo `labels` (lista de etiquetas).
- **Crear Nodo con Propiedades**  
  **Método:** POST  
  **Endpoint:** `/api/create-node-with-properties/`  
  **Descripción:** Crea un nodo asignándole propiedades; se valida que se provean al menos 5 propiedades.  
  **Entrada:** Un JSON que incluye `label` y `properties` (por ejemplo, `nombre`, `email`, `edad`, `fecha_registro`, `intereses`, etc.).  
  **Nota:** Se convierte la cadena de fecha a un valor de tipo Date en Neo4j (usando la función `date()`).

### b. Consultas de Nodos

- **Buscar Nodos Dinámicamente**  
  **Método:** POST  
  **Endpoint:** `/api/search-nodes/`  
  **Descripción:** Permite realizar consultas dinámicas de nodos basadas en etiquetas y filtros. Los filtros pueden especificar operadores como `=`, `<`, `<=`, `>`, `>=`, `IN` y `CONTAINS`. Además, se pueden filtrar por fechas y valores en listas.  
  **Entrada:** Un JSON que incluye `labels`, `filters` y `limit`.
- **Consultas Agregadas de Datos**  
  **Método:** POST  
  **Endpoint:** `/api/get-aggregated-data/`  
  **Descripción:** Realiza consultas agregadas (COUNT, AVG, MAX, MIN, SUM) sobre una propiedad numérica de los nodos de un determinado label.  
  **Entrada:** Un JSON que incluye `label` y `property`.

### c. Actualización de Nodos

- **Actualizar Propiedades de Múltiples Nodos**  
  **Método:** PUT  
  **Endpoint:** `/api/update-multiple-nodes-properties/`  
  **Descripción:** Permite agregar o actualizar propiedades en múltiples nodos. El usuario indica una lista de IDs (valor de la propiedad `id`) y el label, junto con las propiedades a actualizar.  
  **Entrada:** Un JSON con `node_ids`, `label` y `properties`.
- **Eliminar Propiedades de Múltiples Nodos**  
  **Método:** PUT  
  **Endpoint:** `/api/remove-multiple-nodes-properties/`  
  **Descripción:** Permite eliminar (remover) una o más propiedades de múltiples nodos, especificando el label y una lista de IDs de los nodos.  
  **Entrada:** Un JSON con `node_ids`, `label` y `properties` (lista de nombres de propiedades a eliminar).
- **Eliminar Nodos (Con Verificación)**  
  **Método:** DELETE  
  **Endpoint:** `/api/delete-multiple-nodes/`  
  **Descripción:** Permite eliminar uno o más nodos, pero primero verifica que cada nodo no tenga relaciones. Si un nodo tiene relaciones, se informa que no puede eliminarse.  
  **Entrada:** Un JSON con `label` y `node_ids`.

### d. Gestión de Relaciones

- **Crear Relación con Propiedades**  
  **Método:** POST  
  **Endpoint:** `/api/create-relationship/`  
  **Descripción:** Crea una relación entre dos nodos ya existentes (identificados por su label y valor de la propiedad `id`), asignando propiedades a la relación.  
  **Entrada:** Un JSON que incluye `label1`, `node1_id`, `label2`, `node2_id`, `rel_type` y `properties`.
- **Actualizar Propiedades de Múltiples Relaciones**  
  **Método:** PUT  
  **Endpoint:** `/api/update-bulk-relationships/`  
  **Descripción:** Permite actualizar (o crear) propiedades en múltiples relaciones a la vez, mediante un arreglo de objetos que especifican los nodos involucrados, el tipo de relación y las propiedades a asignar.  
  **Entrada:** Un JSON con un arreglo en el campo `relationships`.
- **Eliminar Propiedades de Múltiples Relaciones**  
  **Método:** PUT  
  **Endpoint:** `/api/remove-bulk-relationships/`  
  **Descripción:** Permite eliminar una o más propiedades de múltiples relaciones a la vez.  
  **Entrada:** Un JSON con un arreglo en el campo `relationships` donde cada objeto incluye `label1`, `node1_id`, `label2`, `node2_id`, `rel_type` y `properties` (lista de propiedades a eliminar).
- **Eliminar Relaciones (Global)**  
  **Método:** DELETE  
  **Endpoint:** `/api/delete-bulk-relationships/`  
  **Descripción:** Permite eliminar múltiples relaciones a la vez, identificándolas mediante los labels y los valores de la propiedad `id` de los nodos involucrados.  
  **Entrada:** Un JSON con un arreglo en el campo `relationships`.

---

## 3. Resumen del Proyecto

El proyecto se compone de dos grandes partes:

- **Generación de Datos:**  
  Se han generado nodos (usuarios, posts, comentarios, reels, grupos) con propiedades y relaciones (por ejemplo, follows, likes, comentarios, etc.). Cada nodo y relación se crea con su respectivo conjunto de propiedades, donde se definen los tipos (Integer, String, Fecha, Boolean, Lista, Floats) y se asignan etiquetas que determinan el rol en la red social.
- **Backend en Django:**  
  Se implementaron múltiples endpoints REST para:

  - Crear nodos (con una o múltiples etiquetas) y relaciones.
  - Consultar nodos de forma dinámica, con filtros, búsquedas por fecha y agregaciones.
  - Actualizar propiedades en nodos y relaciones.
  - Eliminar propiedades y nodos, con validaciones de integridad.
  - Gestionar la eliminación de relaciones de forma masiva.

Estos endpoints están diseñados para trabajar a gran escala, permitiendo la manipulación y consulta de datos en una red social compleja, y se pueden utilizar para diversos casos de uso, como análisis de influencia, detección de comunidades, recomendaciones, entre otros.

## 4. Ejemplos de Endpoints y sus Payloads

Crear Nodo con Una Sola Label:

```css
@POST http://127.0.0.1:8000/api/create-node-single-label/
Payload:
{
    "label": "Persona"
}
```

Crear Nodo con Múltiples Labels:

```css
@post http://127.0.0.1:8000/api/create-node-multiple-labels/
Payload: {
  "labels":["Persona","cliente","empresa"] ;
}
```

Crear Nodo con Propiedades:

```css

@POST http://127.0.0.1:8000/api/create-node-with-properties/
Payload:
{
    "label": "Persona",
    "properties": {
        "id": 1,
        "nombre": "Sergio",
        "email": "juanperez@gmail.com",
        "edad": 20,
        "fecha_registro": "2024-01-02",
        "intereses": ["hola", "prueba"],
        "activo": true
    }
}

```

Buscar Nodos Dinámicamente:

```css
@post http://127.0.0.1:8000/api/search-nodes/
Payload: {
  "labels":["Reel"],"filters":  {
    'duracion': {
      "operator":">=","value": '30.5';
    }
    ,
        'likes': {
      "operator":"<","value": '4000';
    }
  }
  ,"limit": 10;
}
```

Consultas Agregadas:

```css
@post http://127.0.0.1:8000/api/get-aggregated-data/
Payload: {
  "label":"Reel","property": 'duracion';
}
```

Actualizar Propiedades de Múltiples Nodos:

```css
@put http://127.0.0.1:8000/api/update-multiple-nodes-properties/
Payload: {
  'node_ids': [1, 2, 3],
    'label': 'persona',
    'properties': {
    "edad":22,"intereses": [ 'Baloncesto'];
  }
}
```

Eliminar Propiedades de Múltiples Nodos:

```css
@PUT http://127.0.0.1:8000/api/remove-multiple-nodes-properties/
Payload:
{
    "node_ids": [1, 2],
    "label": "Persona",
    "properties": ["email"]
}
```

Crear Relación con Propiedades:

```css
@POST http://127.0.0.1:8000/api/create-relationship/
Payload:
{
    "label1": "Persona",
    "node1_id": 2,
    "label2": "Persona",
    "node2_id": 1,
    "rel_type": "Profesora",
    "properties": {
        "tipo_amistad": "Compañeros de trabajo",
        "desde": "2021-10-23",
        "nivel_confianza": 10
    }
}
```

Actualizar Propiedades en Múltiples Relaciones:

```css
@PUT http://127.0.0.1:8000/api/update-bulk-relationships/
Payload:
{
  "relationships": [
    {
      "label1": "Persona",
      "node1_id": 1,
      "label2": "Persona",
      "node2_id": 2,
      "rel_type": "ALUMNO_DE",
      "sueldo": 10000,
      "tipo_amistad": "Mejores Amigos",
      "desde": "2025-04-03"
    },
    {
      "label1": "Persona",
      "node1_id": 2,
      "label2": "Persona",
      "node2_id": 1,
      "rel_type": "Profesora",
      "sueldo": 6000,
      "tipo_amistad": "Mejores Amigos",
      "desde": "2020-10-10"
    }
  ]
}

```

Eliminar Propiedades en Múltiples Relaciones:

```css
@PUT http://127.0.0.1:8000/api/remove-bulk-relationships/
Payload:
{
  "relationships": [
    {
      "label1": "Persona",
      "node1_id": 1,
      "label2": "Persona",
      "node2_id": 2,
      "rel_type": "ALUMNO_DE",
      "properties": ["sueldo"]
    },
    {
      "label1": "Persona",
      "node1_id": 2,
      "label2": "Persona",
      "node2_id": 1,
      "rel_type": "Profesora",
      "properties": ["sueldo"]
    }
  ]
}

```

Eliminar Múltiples Nodos:

```css
@delete http://127.0.0.1:8000/api/delete-multiple-nodes/
Payload: {
  "label":"Persona","node_ids": [1, 2];
}
```

Eliminar Múltiples Relaciones:

```css
@DELETE http://127.0.0.1:8000/api/delete-bulk-relationships/
Payload:
{
  "relationships": [
    {
      "label1": "Persona",
      "node1_id": 1,
      "label2": "Persona",
      "node2_id": 2,
      "rel_type": "ALUMNO_DE"
    },
    {
      "label1": "Persona",
      "node1_id": 2,
      "label2": "Persona",
      "node2_id": 1,
      "rel_type": "Profesora"
    }
  ]
}

```

## 5. Conclusión

Este proyecto integra:

- **Generación de datos** a través de un script Python que crea CSV para nodos y relaciones.
- **Estructura de nodos y relaciones** definidas en base a una red social (con nodos de tipo Usuario, Post, Comment, Reel, Group, y relaciones como FOLLOWS, LIKES, COMMENTED_ON, etc.) y sus respectivas propiedades (con tipos: Integer, String, Fecha, Boolean, Lista).
- **Backend en Django** con endpoints REST para:
  - Crear nodos (con una o múltiples etiquetas) y relaciones con propiedades.
  - Consultar nodos de forma dinámica y realizar agregaciones.
  - Actualizar y eliminar propiedades de nodos y relaciones.
  - Eliminar nodos y relaciones, validando integridad (por ejemplo, no eliminar nodos que tienen relaciones).

Cada endpoint está diseñado para operar a gran escala, aceptando datos dinámicos y permitiendo operaciones CRUD complejas en la base de datos Neo4j.
