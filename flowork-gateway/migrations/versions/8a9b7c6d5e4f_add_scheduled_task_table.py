########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\8a9b7c6d5e4f_add_scheduled_task_table.py total lines 38 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "a1b2c3d4e5f6"
down_revision = "7e70c5f4d075"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "scheduled_tasks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("engine_id", sa.String(), nullable=False),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("os_task_name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["engine_id"],
            ["registered_engines.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("os_task_name"),
    )
def downgrade():
    op.drop_table("scheduled_tasks")
