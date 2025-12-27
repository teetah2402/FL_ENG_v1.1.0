########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\c5e4b3a2d1f0_add_public_address_and_index.py total lines 20 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = 'c5e4b3a2d1f0'
down_revision = 'd3e4a5f6b7c8'
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('public_address', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_public_address'), ['public_address'], unique=True)
def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_public_address'))
        batch_op.drop_column('public_address')
