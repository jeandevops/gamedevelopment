class EntityManager:
    def __init__(self):
        """Initializes the EntityManager with an empty entity dictionary"""
        self.entities = {}

    def add_entity(self, entity_id, components):
        """Adds a new entity with its components to the manager"""
        self.entities[entity_id] = components

    def get_entity_by_id(self, entity_id):
        """Returns the entity with the specified ID"""
        return self.entities.get(entity_id, None)

    def get_entities_with_component(self, component_type) -> list[tuple[str, dict]]:
        """Returns all entities that have a specific component type"""
        result = []
        for entity_id, components in self.entities.items():
            if component_type in components:
                result.append((entity_id, components[component_type]))
        return result

    def get_all_entities(self):
        """Returns all entities managed by the EntityManager"""
        return self.entities
