"""add cascade delete to every table

Revision ID: 3ea30db69377
Revises: 6388fde942e3
Create Date: 2020-07-28 12:36:16.200067

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3ea30db69377'
down_revision = '6388fde942e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('ClientConsent_clientid_fkey', 'ClientConsent', type_='foreignkey')
    op.create_foreign_key('ClientConsent_clientid_fkey', 'ClientConsent', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('ClientConsultContract_clientid_fkey', 'ClientConsultContract', type_='foreignkey')
    op.create_foreign_key('ClientColusultContract_clientid_fkey', 'ClientConsultContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', type_='foreignkey')
    op.create_foreign_key('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('ClientPolicies_clientid_fkey', 'ClientPolicies', type_='foreignkey')
    op.create_foreign_key('ClientPolicies_clientid_fkey', 'ClientPolicies', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('ClientRelease_clientid_fkey', 'ClientRelease', type_='foreignkey')
    op.create_foreign_key('ClientRelease_clientid_fkey', 'ClientRelease', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', type_='foreignkey')
    op.create_foreign_key('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('MedicalHistory_clientid_fkey', 'MedicalHistory', type_='foreignkey')
    op.create_foreign_key('MedicalHistory_clientid_fkey', 'MedicalHistory', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', type_='foreignkey')
    op.create_foreign_key('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('PTHistory_clientid_fkey', 'PTHistory', type_='foreignkey')
    op.create_foreign_key('PTHistory_clientid_fkey', 'PTHistory', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint('remote_registration_clientid_fkey', 'remote_registration', type_='foreignkey')
    op.create_foreign_key('remote_registration_clientid_fkey', 'remote_registration', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('remote_registration_clientid_fkey', 'remote_registration', type_='foreignkey')
    op.create_foreign_key('remote_registration_clientid_fkey', 'remote_registration', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('PTHistory_clientid_fkey', 'PTHistory', type_='foreignkey')
    op.create_foreign_key('PTHistory_clientid_fkey', 'PTHistory', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', type_='foreignkey')
    op.create_foreign_key('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('MedicalHistory_clientid_fkey', 'MedicalHistory', type_='foreignkey')
    op.create_foreign_key('MedicalHistory_clientid_fkey', 'MedicalHistory', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', type_='foreignkey')
    op.create_foreign_key('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientRelease_clientid_fkey', 'ClientRelease', type_='foreignkey')
    op.create_foreign_key('ClientRelease_clientid_fkey', 'ClientRelease', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientPolicies_clientid_fkey', 'ClientPolicies', type_='foreignkey')
    op.create_foreign_key('ClientPolicies_clientid_fkey', 'ClientPolicies', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', type_='foreignkey')
    op.create_foreign_key('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientColusultContract_clientid_fkey', 'ClientConsultContract', type_='foreignkey')
    op.create_foreign_key('ClientConsultContract_clientid_fkey', 'ClientConsultContract', 'ClientInfo', ['clientid'], ['clientid'])
    op.drop_constraint('ClientConsent_clientid_fkey', 'ClientConsent', type_='foreignkey')
    op.create_foreign_key('ClientConsent_clientid_fkey', 'ClientConsent', 'ClientInfo', ['clientid'], ['clientid'])
    # ### end Alembic commands ###
