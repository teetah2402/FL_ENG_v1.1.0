########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\d3e4a5f6b7c8_add_executions_and_features_to_plans.py total lines 25 
########################################################################

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "d3e4a5f6b7c8"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table("plans", schema=None) as batch_op:
        batch_op.add_column(sa.Column("max_executions", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "features", sa.JSON(), nullable=True
            )
        )
def downgrade():
    with op.batch_alter_table("plans", schema=None) as batch_op:
        batch_op.drop_column("features")
        batch_op.drop_column("max_executions")
