from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, text


def make_team_fk() -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["team_id"],
        ["teams.id"],
        ondelete="CASCADE",
    )


def make_team_composite_fk(fk_column: str, foreign_table: str) -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["team_id", fk_column],
        [f"{foreign_table}.team_id", f"{foreign_table}.id"],
        ondelete="CASCADE"
    )


UUID_DEFAULT_EXPR = text("(gen_random_uuid())")


def make_team_composite_pk() -> PrimaryKeyConstraint:
    return PrimaryKeyConstraint(
        "team_id",
        "id",
    )
