from eave.archer.service_graph import Service


class ServiceRegistry:
    services: dict[str, Service]

    def __init__(self) -> None:
        self.services = {}

    def register(self, service: Service) -> Service:
        service = self.services.setdefault(service.id, service)
        return service

    def get(self, id: str) -> Service | None:
        return self.services.get(id)

# FIXME: thread safety
SERVICE_REGISTRY = ServiceRegistry()
