class EntityManager:
    def __init__(self):
        """Initializes the EntityManager with an empty entity dictionary"""
        self.entities = {}

    def add_entity(self, entity_id: str, components: dict) -> None:
        """Adds a new entity with its components to the manager"""
        self.entities[entity_id] = components

    def get_entity_by_id(self, entity_id: str) -> dict | None:
        """Returns the entity with the specified ID"""
        return self.entities.get(entity_id, None)

    def get_entities_with_components(self, component_type_list: list[str]) -> list[tuple[str, dict]]:
        """Returns all entities that have a specific component type"""
        result = []
        for entity_id, components in self.entities.items():
            if all(component_type in components for component_type in component_type_list):
                result.append((entity_id, components))
        return result