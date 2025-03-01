from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import (
    NodeSerializer,
    NodeCreateSingleSerializer,
    NodeCreateMultipleLabelsSerializer,
    NodeSearchSerializer,
    AggregatedDataSerializer,
    MultipleNodesUpdateSerializer,
    MultipleNodesPropertiesRemoveSerializer,
    RelationshipCreationSerializer,
    RelationshipUpdateSerializer,
    MultipleRelationshipUpdateSerializer,
    RelationshipRemoveSerializer,
    MultipleRelationshipRemoveSerializer,
    NodeDeleteSerializer,
    MultipleNodesDeleteSerializer,
)
from .neo4j_connection import neo4j_conn
import datetime
from neo4j.exceptions import Neo4jError

"""
Crear un nodo con un solo label
"""


@api_view(["POST"])
def create_node_single_label(request):
    """
    Ejemplo de JSON esperado:
    {
        "label": "Persona"
    }
    """

    serializer = NodeCreateSingleSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        query = f"CREATE (n:{label}) RETURN id(n) AS node_id, labels(n) AS labels"

        with neo4j_conn._driver.session() as session:
            result = session.run(query)
            nodo_creado = result.single()  # Obtiene el nodo creado

            if nodo_creado:
                return Response(
                    {
                        "message": "Nodo creado",
                        "node": {
                            "id": nodo_creado["node_id"],
                            "labels": nodo_creado["labels"],
                        },
                    }
                )
            else:
                return Response({"error": "No se pudo crear el nodo"}, status=500)

    return Response(serializer.errors, status=400)


"""
Crear un nodo con múltiples labels
"""


# 2️⃣ Crear un nodo con múltiples labels
@api_view(["POST"])
def create_node_multiple_labels(request):
    """
    Ejemplo de JSON esperado:
    {
        "labels": ["Persona", "Cliente"]
    }
    """

    serializer = NodeCreateMultipleLabelsSerializer(data=request.data)
    if serializer.is_valid():
        labels = serializer.validated_data.get("labels", [])  # Obtener etiquetas

        if not labels or len(labels) < 2:  # Validar que haya al menos 2 etiquetas
            return Response(
                {"error": "Debes proporcionar al menos dos labels."}, status=400
            )

        labels_str = ":".join(labels)  # Formatear para Neo4j (Ej: "Persona:Cliente")

        query = f"CREATE (n:{labels_str}) RETURN id(n) AS node_id, labels(n) AS labels"

        with neo4j_conn._driver.session() as session:
            result = session.run(query)
            nodo_creado = result.single()  # Obtener el nodo creado

            if nodo_creado:
                return Response(
                    {
                        "message": "Nodo con múltiples labels creado",
                        "labels_str": labels_str,  # <-- Para ver en la respuesta
                        "node": {
                            "id": nodo_creado["node_id"],
                            "labels": nodo_creado["labels"],
                        },
                    }
                )
            else:
                return Response({"error": "No se pudo crear el nodo"}, status=500)

    return Response(serializer.errors, status=400)


"""
Crear un nodo con propiedades y validar que al menos 5 propiedades sean proporcionadas
"""


@api_view(["POST"])
def create_node_with_properties(request):
    """
    Ejemplo de JSON esperado:
    {
        "label": "Usuario",
        "properties": {
            "nombre": "Juan Pérez",
            "email": ""
            "edad": 30,
            "fecha_registro": "2024-01-01",
            "activo": true
        }
    }
    """

    serializer = NodeSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data.get("label")
        properties = serializer.validated_data.get("properties", {})

        # Validar que al menos 5 propiedades sean proporcionadas
        if len(properties) < 5:
            return Response(
                {"error": "Debes proporcionar al menos 5 propiedades."}, status=400
            )

        # Construir la cadena de propiedades para Cypher
        properties_string = ", ".join(f"n.{key} = ${key}" for key in properties.keys())
        query = f"CREATE (n:{label}) SET {properties_string} RETURN id(n) AS node_id, labels(n) AS labels, properties(n) AS properties"

        with neo4j_conn._driver.session() as session:
            result = session.run(query, properties)
            nodo_creado = result.single()

            if nodo_creado:
                return Response(
                    {
                        "message": "Nodo con propiedades creado",
                        "node": {
                            "id": nodo_creado["node_id"],
                            "labels": nodo_creado["labels"],
                            "properties": nodo_creado["properties"],
                        },
                    }
                )
            else:
                return Response({"error": "No se pudo crear el nodo"}, status=500)

    return Response(serializer.errors, status=400)


@api_view(["POST"])
def search_nodes(request):
    """
    Endpoint para buscar nodos de forma dinámica en Neo4j.
    Parámetros en el payload JSON:
      - labels: Lista de etiquetas (ej: ["Usuario", "Cliente"])
      - filters: Diccionario de filtros, donde cada clave es el nombre de la propiedad y el valor es un objeto con:
            - operator: "=", "<", "<=", ">", ">=", "IN"
            - value: Valor a comparar (puede ser simple o una lista)
      - limit: Número máximo de nodos a retornar (por defecto 100)
    """
    serializer = NodeSearchSerializer(data=request.data)
    if serializer.is_valid():
        labels = serializer.validated_data.get("labels", [])
        filters = serializer.validated_data.get("filters", {})
        limit = serializer.validated_data.get("limit", 100)

        query = "MATCH (n"
        if labels:
            query += ":" + ":".join(labels)
        query += ")"

        params = {}
        where_clauses = []

        if filters:
            for key, filter_item in filters.items():
                operator = filter_item["operator"].upper()
                value = filter_item["value"]

                if operator == "IN":
                    # Si el valor no es una lista, lo convertimos a lista
                    if not isinstance(value, list):
                        value = [value]
                    where_clauses.append(f"ANY(x IN n.{key} WHERE x IN ${key})")
                    params[key] = [str(v).strip() for v in value]
                elif operator == "CONTAINS":
                    if isinstance(value, list):
                        where_clauses.append(
                            f"ANY(y IN n.{key} WHERE ANY(x IN ${key} WHERE y CONTAINS x))"
                        )
                        params[key] = [str(v).strip() for v in value]
                    else:
                        where_clauses.append(
                            f"ANY(y IN n.{key} WHERE y CONTAINS ${key})"
                        )
                        params[key] = str(value).strip()
                else:
                    where_clauses.append(f"n.{key} {operator} ${key}")
                    # Si la propiedad es de fecha (por ejemplo, empieza con "fecha_"), convertir el valor a fecha.
                    if key.lower().startswith("fecha_"):
                        try:
                            params[key] = datetime.date.fromisoformat(value)
                        except ValueError:
                            params[key] = value
                    else:
                        try:
                            params[key] = int(value)
                        except ValueError:
                            try:
                                params[key] = float(value)
                            except ValueError:
                                params[key] = value

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " RETURN elementId(n) AS node_id, labels(n) AS labels, properties(n) AS properties"
        query += f" LIMIT {limit}"

        nodes = []
        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            for record in result:
                props = record["properties"]
                for k, v in props.items():
                    if hasattr(v, "isoformat"):
                        try:
                            props[k] = v.isoformat()
                        except Exception:
                            props[k] = str(v)
                nodes.append(
                    {
                        "id": record["node_id"],
                        "labels": record["labels"],
                        "properties": props,
                    }
                )

        return Response(
            {"message": f"Se encontraron {len(nodes)} nodos", "nodes": nodes}
        )
    return Response(serializer.errors, status=400)


"""
Consultas agregadas
"""


@api_view(["POST"])
def get_aggregated_data(request):
    """
    Endpoint para realizar consultas agregadas sobre los nodos.
    Se espera recibir un JSON con:
      - label: Etiqueta de los nodos a consultar (por ejemplo, "Persona").
      - property: Nombre de la propiedad numérica a agregar (por ejemplo, "edad").

    La consulta se construye de forma dinámica:
    MATCH (n:Persona)
    RETURN COUNT(n) AS count, AVG(n.edad) AS avg, MAX(n.edad) AS max, MIN(n.edad) AS min, SUM(n.edad) AS sum
    """
    serializer = AggregatedDataSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        prop = serializer.validated_data["property"]

        query = f"""
        MATCH (n:{label})
        RETURN COUNT(n) AS count, 
               AVG(n.{prop}) AS avg, 
               MAX(n.{prop}) AS max, 
               MIN(n.{prop}) AS min, 
               SUM(n.{prop}) AS sum
        """

        with neo4j_conn._driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": f"Datos agregados para nodos con label '{label}' y propiedad '{prop}'",
                        "count": record["count"],
                        "avg": record["avg"],
                        "max": record["max"],
                        "min": record["min"],
                        "sum": record["sum"],
                    }
                )
            else:
                return Response(
                    {"error": "No se encontraron datos agregados."}, status=404
                )
    return Response(serializer.errors, status=400)


"""
Agregar y actualizar propiedades de uno o varios nodos
"""


@api_view(["PUT"])
def update_multiple_nodes_properties(request):
    """
    Endpoint para actualizar (agregar o modificar) propiedades en múltiples nodos,
    usando el label y una lista de valores de la propiedad 'id'.

    Se espera un JSON como:
    {
        "node_ids": ["1", "2", "3"],
        "label": "Usuario",
        "properties": {
            "edad": 35,
            "activo": true
        }
    }

    La consulta ejecutada es:

    MATCH (n:Usuario)
    WHERE n.id IN $node_ids
    SET n += $props
    RETURN count(n) AS updatedCount
    """
    serializer = MultipleNodesUpdateSerializer(data=request.data)
    if serializer.is_valid():
        node_ids = serializer.validated_data["node_ids"]
        label = serializer.validated_data["label"]
        new_properties = serializer.validated_data["properties"]

        # Convertir todos los node_ids a enteros (si la propiedad se almacena como número)
        try:
            node_ids_int = [int(node_id) for node_id in node_ids]
        except ValueError:
            node_ids_int = node_ids  # Si falla la conversión, se mantienen como strings

        query = f"""
        MATCH (n:{label})
        WHERE n.id IN $node_ids
        SET n += $props
        RETURN count(n) AS updatedCount
        """
        params = {"node_ids": node_ids_int, "props": new_properties}

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": "Nodos actualizados correctamente",
                        "updatedCount": record["updatedCount"],
                    }
                )
            else:
                return Response({"error": "Error al actualizar nodos"}, status=500)
    return Response(serializer.errors, status=400)


"""
Eliminar 1 o mas propiedades de uno o de varios nodos.
"""


@api_view(["PUT"])
def remove_multiple_nodes_properties(request):
    """
    Endpoint para eliminar (remover) una o más propiedades de múltiples nodos.
    Se espera recibir un JSON con:
      - node_ids: Lista de valores de la propiedad 'id' de los nodos (ej: ["1", "2", "3"]).
      - label: Label de los nodos (ej: "Persona").
      - properties: Lista de nombres de propiedades a eliminar (ej: ["edad", "ocupacion"]).

    La consulta Cypher que se ejecuta es similar a:
    MATCH (n:Persona)
    WHERE n.id IN $node_ids
    REMOVE n.edad, n.ocupacion
    RETURN count(n) AS updatedCount
    """
    serializer = MultipleNodesPropertiesRemoveSerializer(data=request.data)
    if serializer.is_valid():
        node_ids = serializer.validated_data["node_ids"]
        label = serializer.validated_data["label"]
        props_to_remove = serializer.validated_data["properties"]

        # Convertir los node_ids a enteros, si corresponde
        try:
            node_ids_int = [int(nid) for nid in node_ids]
        except ValueError:
            node_ids_int = node_ids  # En caso de que se almacenen como strings

        # Construir la cláusula REMOVE a partir de la lista de propiedades
        remove_clause = ", ".join(f"n.{prop}" for prop in props_to_remove)

        query = f"""
        MATCH (n:{label})
        WHERE n.id IN $node_ids
        REMOVE {remove_clause}
        RETURN count(n) AS updatedCount
        """
        params = {"node_ids": node_ids_int}

        try:
            with neo4j_conn._driver.session() as session:
                result = session.run(query, params)
                record = result.single()
                if record is not None:
                    return Response(
                        {
                            "message": "Propiedades eliminadas de los nodos",
                            "updatedCount": record["updatedCount"],
                        }
                    )
                else:
                    return Response({"error": "Error al actualizar nodos"}, status=500)
        except Neo4jError as e:
            return Response({"error": str(e)}, status=500)
    return Response(serializer.errors, status=400)


"""
Crear una relación entre dos nodos existentes
"""


@api_view(["POST"])
def create_relationship(request):
    """
    Endpoint para crear una relación entre dos nodos ya existentes.

    Se espera recibir un JSON con:
      - label1: Label del primer nodo (ej: "Persona")
      - node1_id: Valor de la propiedad "id" del primer nodo
      - label2: Label del segundo nodo (ej: "Empresa")
      - node2_id: Valor de la propiedad "id" del segundo nodo
      - rel_type: Tipo de la relación (ej: "TRABAJA_EN")
      - properties: Un diccionario con al menos 3 propiedades (ej: { "cargo": "Desarrollador", "desde": 2018, "salario": 60000 })
    La consulta se ejecuta de forma global, verificando que ambos nodos existan.
    """
    serializer = RelationshipCreationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        # Validar que se envíe al menos 3 propiedades para la relación
        if len(data["properties"]) < 3:
            return Response(
                {"error": "Debe proveer al menos 3 propiedades para la relación."},
                status=400,
            )

        # Convertir node ids a entero, si la propiedad "id" es numérica
        try:
            node1_id = int(data["node1_id"])
            node2_id = int(data["node2_id"])
        except ValueError:
            # Si falla, usarlos como string
            node1_id = data["node1_id"]
            node2_id = data["node2_id"]

        label1 = data["label1"]
        label2 = data["label2"]
        rel_type = data["rel_type"]
        props = data["properties"]

        # Construir la consulta Cypher. Utilizamos f-string para inyectar los labels y el tipo de relación.
        query = f"""
        MATCH (n1:{label1} {{ id: $node1_id }}), (n2:{label2} {{ id: $node2_id }})
        CREATE (n1)-[r:{rel_type} $props]->(n2)
        RETURN elementId(r) AS rel_id, properties(r) AS rel_properties
        """
        params = {"node1_id": node1_id, "node2_id": node2_id, "props": props}

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": "Relación creada correctamente",
                        "relationship": {
                            "id": record["rel_id"],
                            "properties": record["rel_properties"],
                        },
                    }
                )
            else:
                return Response(
                    {
                        "error": "No se pudo crear la relación. Verifique que ambos nodos existan."
                    },
                    status=404,
                )
    return Response(serializer.errors, status=400)


"""

Actualizar propiedades de una relación entre dos nodos y validar que al menos 3 propiedades sean proporcionadas.
"""


@api_view(["PUT"])
def update_single_relationship_properties(request):
    """
    Actualiza (agrega) propiedades en una relación específica entre dos nodos.
    Se espera recibir un JSON similar a:
    {
        "label1": "Persona",
        "node1_id": "1",
        "label2": "Empresa",
        "node2_id": "100",
        "rel_type": "TRABAJA_EN",
        "properties": {
            "fechaInicio": "2025-01-01",
            "cargo": "Ingeniero",
            "salario": 60000
        }
    }
    La consulta ejecutada será:
    MATCH (n1:Persona {id: $node1_id})-[r:TRABAJA_EN]->(n2:Empresa {id: $node2_id})
    SET r += $props
    RETURN elementId(r) AS rel_id, properties(r) AS rel_properties
    """
    serializer = RelationshipUpdateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        label1 = data["label1"]
        label2 = data["label2"]
        rel_type = data["rel_type"]
        # Convertir node ids a entero si es numérico (o usarlos como string si así se guardó)
        try:
            node1_id = int(data["node1_id"])
            node2_id = int(data["node2_id"])
        except ValueError:
            node1_id = data["node1_id"]
            node2_id = data["node2_id"]
        props = data["properties"]

        query = f"""
        MATCH (n1:{label1} {{id: $node1_id}})-[r:{rel_type}]->(n2:{label2} {{id: $node2_id}})
        SET r += $props
        RETURN elementId(r) AS rel_id, properties(r) AS rel_properties
        """
        params = {"node1_id": node1_id, "node2_id": node2_id, "props": props}

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": "Relación actualizada correctamente",
                        "relationship": {
                            "id": record["rel_id"],
                            "properties": record["rel_properties"],
                        },
                    }
                )
            else:
                return Response({"error": "Relación no encontrada"}, status=404)
    return Response(serializer.errors, status=400)


"""
Actualizar propiedades de múltiples relaciones y validar que al menos 3 propiedades sean proporcionadas.
"""


@api_view(["PUT"])
def update_multiple_relationships_properties(request):
    """
    Actualiza (agrega) propiedades a todas las relaciones de un tipo específico.
    Se espera recibir un JSON similar a:
    {
        "rel_type": "TRABAJA_EN",
        "properties": {
            "fechaInicio": "2025-01-01",
            "cargo": "Empleado"
        }
    }
    La consulta ejecutada será:
    MATCH ()-[r:TRABAJA_EN]->()
    SET r += $props
    RETURN count(r) AS updatedCount
    """
    serializer = MultipleRelationshipUpdateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        rel_type = data["rel_type"]
        props = data["properties"]

        query = f"""
        MATCH ()-[r:{rel_type}]->()
        SET r += $props
        RETURN count(r) AS updatedCount
        """
        params = {"props": props}

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": "Propiedades agregadas a múltiples relaciones",
                        "updatedCount": record["updatedCount"],
                    }
                )
            else:
                return Response(
                    {"error": "Error al actualizar las relaciones"}, status=500
                )
    return Response(serializer.errors, status=400)


"""
Eliminar propiedades de una relación entre dos nodos y validar que al menos una propiedad sea proporcionada.
"""


@api_view(["PUT"])
def remove_single_relationship_properties(request):
    """
    Elimina (REMOVE) una o más propiedades de una relación específica entre dos nodos.

    Se espera recibir un JSON:
    {
        "label1": "Persona",
        "node1_id": "1",
        "label2": "Empresa",
        "node2_id": "100",
        "rel_type": "TRABAJA_EN",
        "properties": ["cargo", "fechaInicio"]
    }

    La consulta Cypher se ejecuta como:
    MATCH (n1:Persona { id: $node1_id })-[r:TRABAJA_EN]->(n2:Empresa { id: $node2_id })
    REMOVE r.cargo, r.fechaInicio
    RETURN elementId(r) AS rel_id, properties(r) AS rel_properties
    """
    serializer = RelationshipRemoveSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        label1 = data["label1"]
        label2 = data["label2"]
        rel_type = data["rel_type"]

        # Convertir node ids a entero si se almacenan como números
        try:
            node1_id = int(data["node1_id"])
            node2_id = int(data["node2_id"])
        except ValueError:
            node1_id = data["node1_id"]
            node2_id = data["node2_id"]

        props_to_remove = data["properties"]
        remove_clause = ", ".join(f"r.{prop}" for prop in props_to_remove)

        query = f"""
        MATCH (n1:{label1} {{ id: $node1_id }})-[r:{rel_type}]->(n2:{label2} {{ id: $node2_id }})
        REMOVE {remove_clause}
        RETURN elementId(r) AS rel_id, properties(r) AS rel_properties
        """
        params = {
            "node1_id": node1_id,
            "node2_id": node2_id,
        }

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return Response(
                    {
                        "message": "Propiedades eliminadas de la relación",
                        "relationship": {
                            "id": record["rel_id"],
                            "properties": record["rel_properties"],
                        },
                    }
                )
            else:
                return Response({"error": "Relación no encontrada"}, status=404)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
def remove_multiple_relationships_properties(request):
    """
    Elimina (REMOVE) una o más propiedades de todas las relaciones de un tipo específico.

    Se espera recibir un JSON:
    {
        "rel_type": "TRABAJA_EN",
        "properties": ["cargo", "fechaInicio"]
    }

    La consulta Cypher se ejecuta como:
    MATCH ()-[r:TRABAJA_EN]->()
    REMOVE r.cargo, r.fechaInicio
    RETURN count(r) AS updatedCount
    """
    serializer = MultipleRelationshipRemoveSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        rel_type = data["rel_type"]
        props_to_remove = data["properties"]
        remove_clause = ", ".join(f"r.{prop}" for prop in props_to_remove)

        query = f"""
        MATCH ()-[r:{rel_type}]->()
        REMOVE {remove_clause}
        RETURN count(r) AS updatedCount
        """
        params = {}
        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record is not None:
                return Response(
                    {
                        "message": "Propiedades eliminadas de múltiples relaciones",
                        "updatedCount": record["updatedCount"],
                    }
                )
            else:
                return Response(
                    {"error": "Error al actualizar las relaciones"}, status=500
                )
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
def delete_single_node(request):
    """
    Endpoint para eliminar un nodo individual,
    verificando primero si el nodo tiene relaciones.
    Se espera recibir un JSON:
    {
        "node_id": "1",
        "label": "Persona"
    }
    """
    serializer = NodeDeleteSerializer(data=request.data)
    if serializer.is_valid():
        node_id = serializer.validated_data["node_id"]
        label = serializer.validated_data["label"]
        try:
            node_id_int = int(node_id)
        except ValueError:
            node_id_int = node_id

        # Primero, verificar si el nodo tiene relaciones
        query_check = f"""
        MATCH (n:{label} {{ id: $node_id }})
        OPTIONAL MATCH (n)-[r]-()
        RETURN n, count(r) AS relCount
        """
        params = {"node_id": node_id_int}

        with neo4j_conn._driver.session() as session:
            result = session.run(query_check, params)
            record = result.single()
            if record is None or record["n"] is None:
                return Response({"error": "Nodo no encontrado"}, status=404)
            if record["relCount"] > 0:
                return Response(
                    {"error": "El nodo cuenta con relaciones y no puede ser eliminado"},
                    status=400,
                )

            # Si no tiene relaciones, se procede a eliminarlo
            query_delete = f"""
            MATCH (n:{label} {{ id: $node_id }})
            DELETE n
            """
            session.run(query_delete, params)
            return Response({"message": "Nodo eliminado correctamente"})
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
def delete_multiple_nodes(request):
    """
    Endpoint para eliminar múltiples nodos de un label específico.
    Se usa DETACH DELETE para eliminar también las relaciones.
    Se espera recibir un JSON:
    {
        "label": "Persona"
    }
    La consulta se ejecutará como:
    MATCH (n:Persona)
    DETACH DELETE n
    RETURN count(n) AS deletedCount
    """

    serializer = MultipleNodesDeleteSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        query = f"""
        MATCH (n:{label})
        WITH n, count(n) AS total
        DETACH DELETE n
        RETURN total AS deletedCount
        """
        with neo4j_conn._driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record is not None:
                return Response(
                    {
                        "message": f"Se eliminaron {record['deletedCount']} nodos con label '{label}'"
                    }
                )
            else:
                return Response(
                    {"error": "No se pudieron eliminar los nodos"}, status=500
                )
    return Response(serializer.errors, status=400)
