########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\53026d7cbc70_add_global_kill_switch_table.py total lines 24 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "53026d7cbc70"
down_revision = "880f11028171"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "globally_disabled_components",
        sa.Column("component_id", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "disabled_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.PrimaryKeyConstraint("component_id"),
    )
def downgrade():
    op.drop_table("globally_disabled_components")
