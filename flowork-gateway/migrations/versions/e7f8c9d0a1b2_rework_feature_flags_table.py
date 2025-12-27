########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\e7f8c9d0a1b2_rework_feature_flags_table.py total lines 48 
########################################################################

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "e7f8c9d0a1b2"
down_revision = "e6a0af61b36b"
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table("feature_flags", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "rollout_rules", sa.JSON(), nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "allowed_users", sa.JSON(), nullable=True
            )
        )
        batch_op.drop_column("rollout_percentage")
        batch_op.drop_column("allowed_user_ids")
def downgrade():
    with op.batch_alter_table("feature_flags", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "allowed_user_ids",
                sa.JSON(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "rollout_percentage",
                sa.INTEGER(),
                autoincrement=False,
                nullable=False,
                server_default="0",
            )
        )
        batch_op.drop_column("rollout_rules")
        batch_op.drop_column("allowed_users")
