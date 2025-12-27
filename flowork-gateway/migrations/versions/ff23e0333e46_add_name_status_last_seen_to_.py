########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\ff23e0333e46_add_name_status_last_seen_to_.py total lines 28 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = 'ff23e0333e46'
down_revision = 'c5e4b3a2d1f0'
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('user_backups', schema=None) as batch_op:
        batch_op.alter_column('backup_file_path',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('salt_b64',
               existing_type=sa.VARCHAR(),
               nullable=True)
def downgrade():
    with op.batch_alter_table('user_backups', schema=None) as batch_op:
        batch_op.alter_column('salt_b64',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('backup_file_path',
               existing_type=sa.VARCHAR(),
               nullable=False)
