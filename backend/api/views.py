from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import (
    NodeSerializer,
    NodeSearchSerializer,
    NodeUpdateSerializer,
    MultipleNodesUpdateSerializer,
    NodeSingleUpdateSerializer,
    NodePropertiesRemoveSerializer,
    MultipleNodesPropertiesRemoveSerializer,
    RelationshipCreationSerializer,
    RelationshipUpdateSerializer,
    MultipleRelationshipUpdateSerializer,
    RelationshipRemoveSerializer,
    MultipleRelationshipRemoveSerializer,
    NodeDeleteSerializer,
)
from .neo4j_connection import neo4j_conn
import datetime

"""
Crear un nodo con un solo label
"""


@api_view(["POST"])
def create_node_single_label(request):
    serializer = NodeSerializer(data=request.data)
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
    serializer = NodeSerializer(data=request.data)
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
        query = f"CREATE (n:{label}) SET {properties_string} RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties"

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

        # Construir la consulta MATCH
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
                    # Si el valor es una lista, la cláusula será:
                    # ANY(x IN $<key> WHERE x IN [y IN n.<key> | trim(y)])
                    if isinstance(value, list):
                        where_clauses.append(
                            f"ANY(x IN ${key} WHERE x IN [y IN n.{key} | trim(y)])"
                        )
                        params[key] = [str(v).strip() for v in value]
                    else:
                        where_clauses.append(f"${key} IN [y IN n.{key} | trim(y)]")
                        params[key] = str(value).strip()
                elif operator == "CONTAINS":
                    if isinstance(value, list):
                        # Verifica que para al menos un elemento y en la propiedad,
                        # exista algún x en la lista de parámetros tal que y CONTAINS x
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
                    # Intentar convertir a número (entero o float) si es posible, sino se queda como string.
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
                # Convertir valores de fecha a string
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


@api_view(["GET"])
def get_all_nodes(request):
    query = "MATCH (n) RETURN elementId(n) AS node_id, labels(n) AS labels, properties(n) AS properties"
    with neo4j_conn._driver.session() as session:
        result = session.run(query)
        nodes = [
            {
                "id": record["node_id"],
                "labels": record["labels"],
                "properties": record["properties"],
            }
            for record in result
        ]
    return Response({"message": f"Se encontraron {len(nodes)} nodos", "nodes": nodes})


"""
Consultas agregadas
"""


@api_view(["GET"])
def get_aggregated_data(request):
    """
    Endpoint para realizar consultas agregadas de datos.
    Parámetros opcionales:
      - label: Etiqueta de los nodos a consultar (por defecto "Usuario").
      - propiedad: Nombre de la propiedad numérica sobre la que se realizará la agregación (por defecto "edad").
    Ejemplo:
      GET /api/get-aggregated-data/?label=Usuario&propiedad=edad
    """
    label = request.GET.get("label", "Usuario")
    propiedad = request.GET.get("propiedad", "edad")

    # Construir la consulta Cypher de agregación.
    query = f"""
    MATCH (n:{label})
    RETURN 
      COUNT(n) AS total_nodos, 
      AVG(n.{propiedad}) AS promedio, 
      MAX(n.{propiedad}) AS max_valor, 
      MIN(n.{propiedad}) AS min_valor
    """

    with neo4j_conn._driver.session() as session:
        result = session.run(query)
        record = result.single()
        if record:
            # Record contiene los valores agregados.
            return Response(
                {
                    "message": f"Datos agregados para nodos con label '{label}' y propiedad '{propiedad}'",
                    "total_nodos": record["total_nodos"],
                    "promedio": record["promedio"],
                    "max": record["max_valor"],
                    "min": record["min_valor"],
                }
            )
        else:
            return Response({"error": "No se encontraron datos agregados."}, status=404)


"""
Agregar y actualizar propiedades de nodos
"""


@api_view(["PUT"])
def update_node_properties(request):
    """
    Endpoint para actualizar (agregar o modificar) propiedades de un nodo existente,
    buscando el nodo por su label y su propiedad 'id'.

    Se espera recibir un JSON con:
      - node_id: El valor de la propiedad 'id' del nodo (no el elementId).
      - properties: Un diccionario con las propiedades a agregar o actualizar.
      - label: El label del nodo (por ejemplo, "Usuario").
    """
    serializer = NodeUpdateSerializer(data=request.data)
    if serializer.is_valid():
        # Convertir node_id a entero
        try:
            node_id_int = int(serializer.validated_data["node_id"])
        except ValueError:
            return Response({"error": "node_id debe ser un número entero."}, status=400)

        new_properties = serializer.validated_data.get("properties", {})
        label = serializer.validated_data["label"]

        # Construir la consulta Cypher usando el label y la propiedad "id"
        query = f"""
        MATCH (n:{label})
        WHERE n.id = $node_id
        SET n += $props
        RETURN n
        """
        params = {"node_id": node_id_int, "props": new_properties}

        # (Opcional) Imprimir query y parámetros para depuración
        print("Query:", query)
        print("Params:", params)

        with neo4j_conn._driver.session() as session:
            result = session.run(query, params)
            record = result.single()

            if record:
                node_data = record["n"]
                updated_props = {}
                for key, val in node_data.items():
                    if hasattr(val, "isoformat"):
                        try:
                            updated_props[key] = val.isoformat()
                        except Exception:
                            updated_props[key] = str(val)
                    else:
                        updated_props[key] = val

                return Response(
                    {
                        "message": "Nodo actualizado correctamente",
                        "node": {
                            "id": node_data.get("id"),
                            "labels": list(node_data.labels),
                            "properties": updated_props,
                        },
                    }
                )
            else:
                return Response({"error": "Nodo no encontrado"}, status=404)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
def update_multiple_nodes_properties(request):
    """
    Endpoint para actualizar múltiples nodos de un mismo label,
    agregando o actualizando las propiedades enviadas.

    Se espera un JSON con:
      - label: El label de los nodos a actualizar (por ejemplo, "Persona").
      - properties: Un diccionario con las propiedades a agregar/actualizar.
    """
    serializer = MultipleNodesUpdateSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        properties = serializer.validated_data["properties"]

        # Construir la consulta Cypher
        query = f"""
        MATCH (n:{label})
        SET n += $props
        RETURN count(n) AS updatedCount
        """
        params = {"props": properties}

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
                return Response(
                    {"error": "No se pudieron actualizar los nodos"}, status=500
                )
    return Response(serializer.errors, status=400)


"""
Eliminar 1 o mas propiedades de un nodos o de varios nodos
"""


@api_view(["PUT"])
def remove_single_node_properties(request):
    """
    Actualiza (remueve) 1 o más propiedades de un nodo específico.
    Se busca el nodo usando su label y su propiedad "id".
    Se espera un JSON:
    {
        "node_id": "1",
        "label": "Persona",
        "properties": ["edad", "ocupacion"]
    }
    La consulta ejecutada será:
    MATCH (n:Persona)
    WHERE n.id = $node_id
    REMOVE n.edad, n.ocupacion
    RETURN elementId(n) AS node_element_id, labels(n) AS labels, properties(n) AS properties
    """
    from neo4j.exceptions import Neo4jError

    serializer = NodePropertiesRemoveSerializer(data=request.data)
    if serializer.is_valid():
        node_id = serializer.validated_data["node_id"]
        label = serializer.validated_data["label"]
        props_to_remove = serializer.validated_data["properties"]

        # Construir la cláusula REMOVE a partir de la lista de propiedades
        remove_clause = ", ".join(f"n.{prop}" for prop in props_to_remove)

        query = f"""
        MATCH (n:{label})
        WHERE n.id = $node_id
        REMOVE {remove_clause}
        RETURN elementId(n) AS node_element_id, labels(n) AS labels, properties(n) AS properties
        """
        try:
            # Convertir node_id a entero si la propiedad se almacena como número
            try:
                node_id_val = int(node_id)
            except ValueError:
                node_id_val = node_id

            params = {"node_id": node_id_val}
            with neo4j_conn._driver.session() as session:
                result = session.run(query, params)
                record = result.single()
                if record:
                    return Response(
                        {
                            "message": "Propiedades eliminadas del nodo",
                            "node": {
                                "id": record["node_element_id"],
                                "labels": record["labels"],
                                "properties": record["properties"],
                            },
                        }
                    )
                else:
                    return Response({"error": "Nodo no encontrado"}, status=404)
        except Neo4jError as e:
            return Response({"error": str(e)}, status=500)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
def remove_multiple_nodes_properties(request):
    """
    Actualiza (remueve) 1 o más propiedades de todos los nodos con un label específico.
    Se espera un JSON:
    {
        "label": "Persona",
        "properties": ["edad", "ocupacion"]
    }
    La consulta ejecutada será:
    MATCH (n:Persona)
    REMOVE n.edad, n.ocupacion
    RETURN count(n) AS updatedCount
    """
    from neo4j.exceptions import Neo4jError

    serializer = MultipleNodesPropertiesRemoveSerializer(data=request.data)
    if serializer.is_valid():
        label = serializer.validated_data["label"]
        props_to_remove = serializer.validated_data["properties"]

        remove_clause = ", ".join(f"n.{prop}" for prop in props_to_remove)

        query = f"""
        MATCH (n:{label})
        REMOVE {remove_clause}
        RETURN count(n) AS updatedCount
        """
        try:
            with neo4j_conn._driver.session() as session:
                result = session.run(query)
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


from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RelationshipCreationSerializer
from .neo4j_connection import neo4j_conn

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
    from .serializers import MultipleNodesDeleteSerializer

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
