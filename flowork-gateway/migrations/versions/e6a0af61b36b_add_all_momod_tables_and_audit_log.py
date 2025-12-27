########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\e6a0af61b36b_add_all_momod_tables_and_audit_log.py total lines 29 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = 'e6a0af61b36b'
down_revision = '18288ec0f59a'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('audit_logs',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('admin_id', sa.String(), nullable=False),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('target_resource', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('ip_address', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('marketplace_submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('staged_file_path', sa.String(), nullable=True))
def downgrade():
    with op.batch_alter_table('marketplace_submissions', schema=None) as batch_op:
        batch_op.drop_column('staged_file_path')
    op.drop_table('audit_logs')
