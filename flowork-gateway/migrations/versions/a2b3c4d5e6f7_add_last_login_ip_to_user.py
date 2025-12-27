########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\a2b3c4d5e6f7_add_last_login_ip_to_user.py total lines 18 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "a2b3c4d5e6f7"
down_revision = "e7f8c9d0a1b2"
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("last_login_ip", sa.String(), nullable=True))
def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("last_login_ip")
