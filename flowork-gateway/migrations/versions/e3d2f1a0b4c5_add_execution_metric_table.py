########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\e3d2f1a0b4c5_add_execution_metric_table.py total lines 52 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "e3d2f1a0b4c5"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "execution_metrics",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("engine_id", sa.String(), nullable=False),
        sa.Column("workflow_context_id", sa.String(), nullable=False),
        sa.Column("preset_name", sa.String(), nullable=True),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("node_name", sa.String(), nullable=True),
        sa.Column("module_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
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
    )
    with op.batch_alter_table("execution_metrics", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_execution_metrics_user_id"), ["user_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_execution_metrics_workflow_context_id"),
            ["workflow_context_id"],
            unique=False,
        )
def downgrade():
    with op.batch_alter_table("execution_metrics", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_execution_metrics_workflow_context_id"))
        batch_op.drop_index(batch_op.f("ix_execution_metrics_user_id"))
    op.drop_table("execution_metrics")
