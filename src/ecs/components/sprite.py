class SpriteComponent:
    #@TODO: Implement image loading later
    def __init__(self, width: float, height: float, image: str = None):
        """Initializes the SpriteComponent with width, height, and image"""
        self.width = width
        self.height = height
        self.image = image