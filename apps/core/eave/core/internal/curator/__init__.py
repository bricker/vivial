from datetime import datetime
from uuid import UUID

import strawberry






# TODO: remove
def main():


    @strawberry.type
    class Survey:
        id: UUID
        visitor_id: str
        start_time: datetime
        search_area_ids: list[str]
        budget: int
        headcount: int
    
    print("hi")



main()

