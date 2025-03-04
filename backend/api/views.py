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
    RelationshipBulkUpdateSerializer,
    RelationshipBulkRemoveSerializer,
    MultipleNodesDeleteWithChecksSerializer,
    RelationshipBulkDeleteSerializer,
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
            - operator: "=", "<", "<=", ">", ">=", "IN", "CONTAINS"
            - value: Valor a comparar (puede ser simple o una lista)
      - limit: Número máximo de nodos a retornar (por defecto 100)

      JSON de ejemplo:
        {
            "labels": ["Usuario"],
            "filters": {
                "edad": { "operator": ">=", "value": 18 },
                "fecha_registro": { "operator": ">=", "value": "2022-01-01" }
            },
            "limit": 50
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
Actualizar propiedades de múltiples relaciones y validar que al menos 3 propiedades sean proporcionadas.
"""


@api_view(["PUT"])
def update_bulk_relationships(request):
    """
    Endpoint para crear/actualizar múltiples relaciones a nivel masivo.
    Cada objeto en 'relationships' debe incluir:
      - label1: Label del primer nodo (ej: "Persona")
      - node1_id: Valor de la propiedad 'id' del primer nodo
      - label2: Label del segundo nodo (ej: "Persona")
      - node2_id: Valor de la propiedad 'id' del segundo nodo
      - rel_type: Tipo de la relación (ej: "AMIGOS")
      - Propiedades adicionales a agregar/actualizar en la relación (ej: sueldo, tipo_amistad, etc.)

    Se procesa cada relación de forma individual y se acumulan errores si no se encuentra alguno de los nodos o la relación.
    """
    serializer = RelationshipBulkUpdateSerializer(data=request.data)
    if serializer.is_valid():
        rels = serializer.validated_data["relationships"]
        total_updated = 0
        errors = []

        with neo4j_conn._driver.session() as session:
            for rel in rels:
                # Extraer datos obligatorios
                label1 = rel.get("label1")
                label2 = rel.get("label2")
                node1_id = rel.get("node1_id")
                node2_id = rel.get("node2_id")
                rel_type = rel.get("rel_type")

                # Extraer las propiedades adicionales (remover las claves de control)
                props = {
                    k: v
                    for k, v in rel.items()
                    if k not in ["label1", "label2", "rel_type", "node1_id", "node2_id"]
                }

                # Construir la consulta dinámicamente (sin usar APOC, para evitar problemas de procedimiento)
                query = f"""
                MATCH (a:{label1} {{id: $node1_id}}), (b:{label2} {{id: $node2_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                ON CREATE SET r += $props
                ON MATCH SET r += $props
                RETURN count(r) AS updatedCount
                """
                params = {"node1_id": node1_id, "node2_id": node2_id, "props": props}

                result = session.run(query, params)
                record = result.single()
                if record:
                    count = record["updatedCount"]
                    if count == 0:
                        errors.append(
                            f"No se encontró la relación entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                        )
                    else:
                        total_updated += count
                else:
                    errors.append(
                        f"Error al actualizar la relación entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                    )

        # Retornar respuesta final: si hay errores, se informan junto con el total actualizado.
        response_data = {
            "message": "Proceso completado.",
            "updatedCount": total_updated,
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
def remove_bulk_relationships(request):
    """
    Endpoint para eliminar (remover) propiedades de múltiples relaciones de forma masiva.

    Se espera recibir un JSON con la siguiente estructura:
    {
      "relationships": [
        {
          "label1": "Persona",
          "node1_id": 1,
          "label2": "Empresa",
          "node2_id": 100,
          "rel_type": "TRABAJA_EN",
          "properties": ["cargo", "fechaInicio"]
        },
        {
          "label1": "Persona",
          "node1_id": 2,
          "label2": "Empresa",
          "node2_id": 101,
          "rel_type": "TRABAJA_EN",
          "properties": ["cargo"]
        }
      ]
    }

    Para cada objeto, se ejecuta la siguiente consulta:

    MATCH (a:<label1> {id: $node1_id}), (b:<label2> {id: $node2_id})
    MATCH (a)-[r:<rel_type>]->(b)
    REMOVE r.<prop1>, r.<prop2>, ...
    RETURN count(r) AS updatedCount

    Se acumulan errores en caso de que no se encuentren los nodos o la relación.
    """
    serializer = RelationshipBulkRemoveSerializer(data=request.data)
    if serializer.is_valid():
        rels = serializer.validated_data["relationships"]
        total_updated = 0
        errors = []

        with neo4j_conn._driver.session() as session:
            for rel in rels:
                label1 = rel.get("label1")
                label2 = rel.get("label2")
                node1_id = rel.get("node1_id")
                node2_id = rel.get("node2_id")
                rel_type = rel.get("rel_type")
                props_to_remove = rel.get("properties", [])

                # Construir la cláusula REMOVE a partir de la lista de propiedades
                remove_clause = ", ".join(f"r.{prop}" for prop in props_to_remove)

                query = f"""
                MATCH (a:{label1} {{id: $node1_id}}), (b:{label2} {{id: $node2_id}})
                MATCH (a)-[r:{rel_type}]->(b)
                REMOVE {remove_clause}
                RETURN count(r) AS updatedCount
                """
                params = {"node1_id": node1_id, "node2_id": node2_id}

                result = session.run(query, params)
                record = result.single()
                if record:
                    count = record["updatedCount"]
                    if count == 0:
                        errors.append(
                            f"No se encontró la relación entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                        )
                    else:
                        total_updated += count
                else:
                    errors.append(
                        f"Error al procesar la relación entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                    )

        response_data = {
            "message": "Proceso completado.",
            "updatedCount": total_updated,
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data)
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
def delete_multiple_nodes_with_checks(request):
    """
    Endpoint para eliminar uno o más nodos verificando que:
      - El nodo exista.
      - El nodo NO tenga relaciones (de lo contrario, no se elimina).

    Se espera recibir un JSON:
    {
        "label": "Persona",
        "node_ids": ["1", "2", "3"]
    }

    Para cada nodo:
      - Si no se encuentra, se reporta error.
      - Si tiene relaciones, se reporta error indicando que no se puede eliminar.
      - Si no tiene relaciones, se elimina.

    Se retorna la cantidad de nodos eliminados y una lista de errores (si los hay).
    """
    serializer = MultipleNodesDeleteWithChecksSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        node_ids = serializer.validated_data["node_ids"]
        deleted_count = 0
        errors = []

        # Convertir los node_ids a enteros, si la propiedad "id" es numérica
        try:
            node_ids_int = [int(nid) for nid in node_ids]
        except ValueError:
            node_ids_int = node_ids  # Si falla la conversión, se usan como string

        with neo4j_conn._driver.session() as session:
            for nid in node_ids_int:
                params = {"node_id": nid}
                # Verificar si el nodo existe y cuántas relaciones tiene
                query_check = f"""
                MATCH (n:{label} {{ id: $node_id }})
                OPTIONAL MATCH (n)-[r]-()
                RETURN n, count(r) AS relCount
                """
                result = session.run(query_check, params)
                record = result.single()
                if record is None or record["n"] is None:
                    errors.append(f"Nodo con id {nid} no encontrado.")
                    continue
                if record["relCount"] > 0:
                    errors.append(
                        f"Nodo con id {nid} no puede ser eliminado porque tiene relaciones."
                    )
                    continue

                # Si no tiene relaciones, eliminar el nodo
                query_delete = f"""
                MATCH (n:{label} {{ id: $node_id }})
                DELETE n
                """
                session.run(query_delete, params)
                deleted_count += 1

        response_data = {
            "message": "Proceso de eliminación completado.",
            "deletedCount": deleted_count,
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data)
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
def delete_bulk_relationships(request):
    """
    Endpoint para eliminar (borrar) de forma masiva una o más relaciones.

    Se espera recibir un JSON de la siguiente forma:
    {
      "relationships": [
        {
          "label1": "Persona",
          "node1_id": 1,
          "label2": "Persona",
          "node2_id": 2,
          "rel_type": "AMIGOS"
        },
        {
          "label1": "Persona",
          "node1_id": 2,
          "label2": "Empresa",
          "node2_id": 100,
          "rel_type": "TRABAJA_EN"
        }
      ]
    }

    Para cada objeto se ejecuta la siguiente consulta:

    MATCH (a:<label1> {id: $node1_id}), (b:<label2> {id: $node2_id})
    MATCH (a)-[r:<rel_type>]->(b)
    DELETE r
    RETURN count(r) AS deletedCount

    Se acumulan errores si no se encuentra la relación o alguno de los nodos.
    """
    serializer = RelationshipBulkDeleteSerializer(data=request.data)
    if serializer.is_valid():
        rels = serializer.validated_data["relationships"]
        total_deleted = 0
        errors = []

        with neo4j_conn._driver.session() as session:
            for rel in rels:
                label1 = rel.get("label1")
                label2 = rel.get("label2")
                node1_id = rel.get("node1_id")
                node2_id = rel.get("node2_id")
                rel_type = rel.get("rel_type")

                query = f"""
                MATCH (a:{label1} {{id: $node1_id}}), (b:{label2} {{id: $node2_id}})
                MATCH (a)-[r:{rel_type}]->(b)
                DELETE r
                RETURN count(r) AS deletedCount
                """
                params = {"node1_id": node1_id, "node2_id": node2_id}

                result = session.run(query, params)
                record = result.single()
                if record is not None:
                    count = record["deletedCount"]
                    if count == 0:
                        errors.append(
                            f"No se encontró la relación {rel_type} entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                        )
                    else:
                        total_deleted += count
                else:
                    errors.append(
                        f"Error al procesar la relación {rel_type} entre {label1} con id {node1_id} y {label2} con id {node2_id}."
                    )

        response_data = {
            "message": "Proceso de eliminación completado.",
            "deletedCount": total_deleted,
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data)
    return Response(serializer.errors, status=400)
