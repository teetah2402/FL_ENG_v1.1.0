########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\a954fe8794ab_add_engineshare_table_and_relations_for_.py total lines 32 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = 'a954fe8794ab'
down_revision = 'ff23e0333e46'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('engine_shares',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('engine_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('shared_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['engine_id'], ['registered_engines.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('engine_id', 'user_id', name='uq_engine_share')
    )
    with op.batch_alter_table('engine_shares', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_engine_shares_engine_id'), ['engine_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_engine_shares_user_id'), ['user_id'], unique=False)
def downgrade():
    with op.batch_alter_table('engine_shares', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_engine_shares_user_id'))
        batch_op.drop_index(batch_op.f('ix_engine_shares_engine_id'))
    op.drop_table('engine_shares')
