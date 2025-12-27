########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\4f2ef23f8289_add_feature_flags_table.py total lines 27 
########################################################################

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "4f2ef23f8289"
down_revision = "165c40dc0302"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("rollout_percentage", sa.Integer(), nullable=False),
        sa.Column(
            "allowed_user_ids", sa.JSON(), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
def downgrade():
    op.drop_table("feature_flags")
