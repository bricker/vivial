from uuid import UUID
import strawberry.federation as sb

@sb.type
class ConfluenceSpace:
    key: str = sb.field()
    name: str = sb.field()

@sb.type
class AtlassianInstallation:
    id: UUID = sb.field()
    team_id: UUID = sb.field()
    atlassian_cloud_id: str = sb.field()

    @classmethod
    def from_orm(cls, orm: AtlassianInstallationOrm) -> "AtlassianInstallation":
        return AtlassianInstallation(
            id=orm.id,
            team_id=orm.team_id,
            atlassian_cloud_id=orm.atlassian_cloud_id
        )

@sb.input
class AtlassianInstallationInput:
    atlassian_cloud_id: str = sb.field()
