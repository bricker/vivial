class Category:
    id: str
    subcategory_id: str | None

    def __init__(self, id: str, subcategory_id: str | None = None) -> None:
        self.id = id
        self.subcategory_id = subcategory_id
