"""Added role into the user table

Revision ID: 718457e13dc5
Revises: 8878553621c0
Create Date: 2026-10-03 09:08:06.978600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '718457e13dc5'
down_revision: Union[str, Sequence[str], None] = '8878553621c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
