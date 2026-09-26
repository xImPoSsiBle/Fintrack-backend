"""seed default categories

Revision ID: e18df2c8cd31
Revises: ea408dcb49f6
Create Date: 2026-09-23 14:17:58.818236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e18df2c8cd31'
down_revision: Union[str, Sequence[str], None] = 'ea408dcb49f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    categories_table = sa.table(
        "categories",
        sa.column("name", sa.String),
        sa.column("type", sa.Enum("income", "expense", name="transactiontype")),
        sa.column("user_id", sa.Integer),
    )

    op.bulk_insert(
        categories_table,
        [
            {"name": "Зарплата", "type": "income", "user_id": None},
            {"name": "Подработка", "type": "income", "user_id": None},
            {"name": "Продукты", "type": "expense", "user_id": None},
            {"name": "Транспорт", "type": "expense", "user_id": None},
            {"name": "Жильё", "type": "expense", "user_id": None},
            {"name": "Развлечения", "type": "expense", "user_id": None},
            {"name": "Здоровье", "type": "expense", "user_id": None},
        ]
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
