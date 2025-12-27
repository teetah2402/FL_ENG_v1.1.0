########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\versions\165c40dc0302_add_marketplace_submission_table.py total lines 28 
########################################################################

from alembic import op
import sqlalchemy as sa
revision = '165c40dc0302'
down_revision = '53026d7cbc70'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('marketplace_submissions',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('submitter_user_id', sa.String(), nullable=False),
    sa.Column('component_id', sa.String(), nullable=False),
    sa.Column('component_type', sa.String(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.Column('admin_notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['submitter_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
def downgrade():
    op.drop_table('marketplace_submissions')
