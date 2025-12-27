########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\b1c2d3e4f5a6_add_staged_file_path_to_submissions.py total lines 18 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = "b1c2d3e4f5a6"
down_revision = "4f2ef23f8289"
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table("marketplace_submissions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("staged_file_path", sa.String(), nullable=True))
def downgrade():
    with op.batch_alter_table("marketplace_submissions", schema=None) as batch_op:
        batch_op.drop_column("staged_file_path")
