from rest_framework import serializers


class NodeCreateSingleSerializer(serializers.Serializer):
    label = serializers.CharField(required=False)


class NodeCreateMultipleLabelsSerializer(serializers.Serializer):
    labels = serializers.ListField(
        child=serializers.CharField(), required=False  # Para múltiples etiquetas
    )


class NodeSerializer(serializers.Serializer):
    label = serializers.CharField(required=False)
    labels = serializers.ListField(
        child=serializers.CharField(), required=False  # Para múltiples etiquetas
    )
    properties = serializers.DictField(child=serializers.JSONField())


class FilterItemSerializer(serializers.Serializer):
    operator = serializers.ChoiceField(
        choices=["=", "<", "<=", ">", ">=", "IN", "CONTAINS"]
    )
    value = serializers.JSONField()  # Permite un valor simple o una lista


class NodeSearchSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    # Ahora, cada filtro es un objeto con operator y value.
    filters = serializers.DictField(child=FilterItemSerializer(), required=False)
    limit = serializers.IntegerField(required=False, default=100)


class AggregatedDataSerializer(serializers.Serializer):
    label = serializers.CharField(required=True)  # Ej: "Persona"
    property = serializers.CharField(required=True)  # Ej: "edad"


class MultipleNodesUpdateSerializer(serializers.Serializer):
    node_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de valores de la propiedad 'id' de los nodos.",
    )
    label = serializers.CharField(
        required=True, help_text="Label de los nodos, por ejemplo, 'Usuario'."
    )
    properties = serializers.DictField(
        required=True, help_text="Diccionario de propiedades a agregar/actualizar."
    )


class MultipleNodesPropertiesRemoveSerializer(serializers.Serializer):
    node_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de valores de la propiedad 'id' de los nodos a actualizar.",
    )
    label = serializers.CharField(
        required=True, help_text="Label de los nodos (por ejemplo, 'Persona')."
    )
    properties = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de nombres de propiedades a eliminar.",
    )


class RelationshipCreationSerializer(serializers.Serializer):
    label1 = serializers.CharField()  # Label del primer nodo (ej: "Persona")
    node1_id = serializers.CharField()  # Valor de la propiedad "id" del primer nodo
    label2 = serializers.CharField()  # Label del segundo nodo (ej: "Empresa")
    node2_id = serializers.CharField()  # Valor de la propiedad "id" del segundo nodo
    rel_type = serializers.CharField()  # Tipo de la relación (ej: "TRABAJA_EN")
    properties = (
        serializers.DictField()
    )  # Propiedades de la relación (al menos 3 claves)


class RelationshipUpdateSerializer(serializers.Serializer):
    label1 = serializers.CharField(required=True)  # Ej: "Persona"
    node1_id = serializers.CharField(
        required=True
    )  # Valor de la propiedad 'id' del primer nodo
    label2 = serializers.CharField(required=True)  # Ej: "Empresa"
    node2_id = serializers.CharField(
        required=True
    )  # Valor de la propiedad 'id' del segundo nodo
    rel_type = serializers.CharField(required=True)  # Ej: "TRABAJA_EN"
    properties = serializers.DictField(
        required=True
    )  # Al menos 3 propiedades, por ejemplo: { "fechaInicio": "2025-01-01", "cargo": "Ingeniero", "salario": 60000 }


class RelationshipBulkUpdateSerializer(serializers.Serializer):
    relationships = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="Lista de objetos que definen cada relación. Cada objeto debe incluir: "
        "label1, node1_id, label2, node2_id, rel_type y las propiedades a establecer (a nivel plano).",
    )


class RelationshipRemoveSerializer(serializers.Serializer):
    label1 = serializers.CharField(required=True)  # Ej: "Persona"
    node1_id = serializers.CharField(
        required=True
    )  # Valor de la propiedad 'id' del primer nodo
    label2 = serializers.CharField(required=True)  # Ej: "Empresa"
    node2_id = serializers.CharField(
        required=True
    )  # Valor de la propiedad 'id' del segundo nodo
    rel_type = serializers.CharField(required=True)  # Ej: "TRABAJA_EN"
    properties = serializers.ListField(
        child=serializers.CharField(), required=True
    )  # Lista de propiedades a eliminar


class MultipleRelationshipRemoveSerializer(serializers.Serializer):
    rel_type = serializers.CharField(required=True)  # Ej: "TRABAJA_EN"
    properties = serializers.ListField(child=serializers.CharField(), required=True)


class NodeDeleteSerializer(serializers.Serializer):
    node_id = serializers.CharField(
        required=True
    )  # Valor de la propiedad "id" del nodo
    label = serializers.CharField(
        required=True
    )  # Label del nodo (por ejemplo, "Persona")


class MultipleNodesDeleteSerializer(serializers.Serializer):
    label = serializers.CharField(required=True)
