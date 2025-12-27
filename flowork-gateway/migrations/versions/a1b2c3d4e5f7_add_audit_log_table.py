########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\a1b2c3d4e5f7_add_audit_log_table.py total lines 31 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "a1b2c3d4e5f7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("admin_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_resource", sa.String(), nullable=True),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["admin_users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
def downgrade():
    op.drop_table("audit_logs")
