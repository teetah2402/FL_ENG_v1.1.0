########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\18288ec0f59a_add_all_momod_tables_and_audit_log.py total lines 30 
########################################################################

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = '18288ec0f59a'
down_revision = 'a1b2c3d4e5f7'
branch_labels = None
depends_on = None
def upgrade():
    op.drop_table('audit_logs')
    with op.batch_alter_table('marketplace_submissions', schema=None) as batch_op:
        batch_op.drop_column('staged_file_path')
def downgrade():
    with op.batch_alter_table('marketplace_submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('staged_file_path', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_table('audit_logs',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('admin_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('action', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('target_resource', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('ip_address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], name=op.f('audit_logs_admin_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('audit_logs_pkey'))
    )
