########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\880f11028171_add_dynamic_plan_management_tables_and_.py total lines 147 
########################################################################

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "880f11028171"
down_revision = "2a8b3c4d5e6f"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "capabilities",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "plans",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    plans_table = sa.table(
        "plans",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_public", sa.Boolean),
    )
    op.bulk_insert(
        plans_table,
        [
            {
                "id": "free",
                "name": "Free",
                "description": "Free Tier",
                "is_public": True,
            },
            {
                "id": "builder",
                "name": "Builder",
                "description": "Builder Tier",
                "is_public": True,
            },
            {
                "id": "creator",
                "name": "Creator",
                "description": "Creator Tier",
                "is_public": True,
            },
            {
                "id": "architect",
                "name": "Architect",
                "description": "Architect Tier",
                "is_public": True,
            },
        ],
    )
    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "key", name="uq_user_state_key"),
    )
    op.create_table(
        "variables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value_data", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_user_variable_name"),
    )
    op.create_table(
        "plan_capabilities",
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("capability_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["capability_id"],
            ["capabilities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plans.id"],
        ),
        sa.PrimaryKeyConstraint("plan_id", "capability_id"),
    )
    op.create_table(
        "plan_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("paypal_plan_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plans.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("paypal_plan_id"),
    )
    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_subscriptions_tier_plans", "plans", ["tier"], ["id"]
        )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("status", sa.String(), nullable=False, server_default="active")
        )
def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("status")
    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.drop_constraint("fk_subscriptions_tier_plans", type_="foreignkey")
    op.drop_table("plan_prices")
    op.drop_table("plan_capabilities")
    op.drop_table("variables")
    op.drop_table("states")
    op.drop_table("plans")
    op.drop_table("capabilities")
