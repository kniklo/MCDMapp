import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from typing import Optional


class Alternative(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    @classmethod
    def delete_by_id(cls, alt_id):
        alternative = cls.query.get(alt_id)
        if(alternative):
            db.session.delete(alternative)
            db.session.commit()
            return True
        return False


class Criterion(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    weight: so.Mapped[Optional[float]] = so.mapped_column(default=0.0)
    #parent_id: so.Mapped[int | None] = so.mapped_column(sa.ForeignKey(Criterion.id)),
#                                                index=True)