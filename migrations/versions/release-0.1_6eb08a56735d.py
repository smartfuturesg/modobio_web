"""All release_1 database changes

Revision ID: 6eb08a56735d
Revises: 04ea7e0894a4
Create Date: 2021-01-15 12:27:40.462673

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6eb08a56735d"
down_revision = "04ea7e0894a4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "LookupGoals",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("goal_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("goal_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("goal_id"),
    )
    op.create_table(
        "MedicalLookUpSTD",
        sa.Column("std_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("std", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("std_id"),
    )
    op.create_table(
        "UserTokensBlacklist",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_index(
        op.f("ix_UserTokensBlacklist_token"),
        "UserTokensBlacklist",
        ["token"],
        unique=True,
    )
    op.create_table(
        "ClientClinicalCareTeam",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("team_member_email", sa.String(), nullable=True),
        sa.Column("team_member_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["team_member_user_id"], ["User.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupDrinks",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("drink_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("primary_goal_id", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["primary_goal_id"],
            ["LookupGoals.goal_id"],
        ),
        sa.PrimaryKeyConstraint("drink_id"),
    )
    op.create_table(
        "MedicalExternalMR",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("med_record_id", sa.String(), nullable=False),
        sa.Column("institute_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["institute_id"], ["MedicalInstitutions.institute_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
        sa.UniqueConstraint("user_id", "med_record_id", "institute_id"),
    )
    op.create_table(
        "MedicalGeneralInfo",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("primary_doctor_contact_name", sa.String(length=50), nullable=True),
        sa.Column("primary_doctor_contact_phone", sa.String(length=20), nullable=True),
        sa.Column("primary_doctor_contact_email", sa.String(), nullable=True),
        sa.Column("blood_type", sa.String(), nullable=True),
        sa.Column("blood_type_positive", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "MedicalGeneralInfoMedicationAllergy",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("medication_name", sa.String(), nullable=True),
        sa.Column("allergy_symptoms", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "MedicalGeneralInfoMedications",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("medication_name", sa.Text(), nullable=True),
        sa.Column("medication_dosage", sa.Float(), nullable=True),
        sa.Column("medication_units", sa.String(), nullable=True),
        sa.Column("medication_freq", sa.Integer(), nullable=True),
        sa.Column("medication_times_per_freq", sa.Integer(), nullable=True),
        sa.Column("medication_time_units", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "MedicalSTDHistory",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("std_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["std_id"], ["MedicalLookUpSTD.std_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "MedicalSocialHistory",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ever_smoked", sa.Boolean(), nullable=True),
        sa.Column("currently_smoke", sa.Boolean(), nullable=True),
        sa.Column("last_smoke_date", sa.Date(), nullable=True),
        sa.Column("last_smoke", sa.Integer(), nullable=True),
        sa.Column("last_smoke_time", sa.String(), nullable=True),
        sa.Column("avg_num_cigs", sa.Integer(), nullable=True),
        sa.Column("num_years_smoked", sa.Integer(), nullable=True),
        sa.Column("plan_to_stop", sa.Boolean(), nullable=True),
        sa.Column("avg_weekly_drinks", sa.Integer(), nullable=True),
        sa.Column("avg_weekly_workouts", sa.Integer(), nullable=True),
        sa.Column("job_title", sa.String(length=100), nullable=True),
        sa.Column("avg_hourly_meditation", sa.Integer(), nullable=True),
        sa.Column("sexual_preference", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "MedicalSurgeries",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("surgery_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("client_user_id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=False),
        sa.Column("surgery_category", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("surgeon", sa.String(), nullable=True),
        sa.Column("institution", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["client_user_id"], ["User.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["reporter_user_id"],
            ["User.user_id"],
        ),
        sa.PrimaryKeyConstraint("surgery_id"),
    )
    op.create_table(
        "StaffRecentClients",
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("staff_user_id", sa.Integer(), nullable=False),
        sa.Column("client_user_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["client_user_id"], ["User.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["staff_user_id"], ["User.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupDrinkIngredients",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=True,
        ),
        sa.Column("idx", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("drink_id", sa.Integer(), nullable=False),
        sa.Column("is_primary_ingredient", sa.Boolean(), nullable=True),
        sa.Column("is_key_additive", sa.Boolean(), nullable=True),
        sa.Column("ingredient_name", sa.String(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["drink_id"],
            ["LookupDrinks.drink_id"],
        ),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.drop_table("staff_recent_clients")
    op.drop_table("ClientExternalMR")
    op.add_column("User", sa.Column("biological_sex_male", sa.Boolean(), nullable=True))
    op.drop_column("User", "biologoical_sex_male")
    op.add_column("UserLogin", sa.Column("refresh_token", sa.String(), nullable=True))
    op.drop_index("ix_UserLogin_token", table_name="UserLogin")
    op.create_unique_constraint(None, "UserLogin", ["refresh_token"])
    op.create_unique_constraint(None, "UserLogin", ["user_id"])
    op.drop_column("UserLogin", "token")
    op.drop_column("UserLogin", "token_expiration")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "UserLogin",
        sa.Column(
            "token_expiration",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "UserLogin",
        sa.Column("token", sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "UserLogin", type_="unique")
    op.drop_constraint(None, "UserLogin", type_="unique")
    op.create_index("ix_UserLogin_token", "UserLogin", ["token"], unique=True)
    op.drop_column("UserLogin", "refresh_token")
    op.add_column(
        "User",
        sa.Column(
            "biologoical_sex_male", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("User", "biological_sex_male")
    op.create_table(
        "ClientExternalMR",
        sa.Column(
            "idx",
            sa.INTEGER(),
            server_default=sa.text("nextval('\"ClientExternalMR_idx_seq\"'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("med_record_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("institute_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["institute_id"],
            ["MedicalInstitutions.institute_id"],
            name="ClientExternalMR_institute_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["User.user_id"],
            name="ClientExternalMR_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("idx", name="ClientExternalMR_pkey"),
        sa.UniqueConstraint(
            "user_id",
            "med_record_id",
            "institute_id",
            name="ClientExternalMR_user_id_med_record_id_institute_id_key",
        ),
    )
    op.create_table(
        "staff_recent_clients",
        sa.Column("idx", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("staff_user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("client_user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "timestamp", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["client_user_id"],
            ["User.user_id"],
            name="staff_recent_clients_client_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["staff_user_id"],
            ["User.user_id"],
            name="staff_recent_clients_staff_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("idx", name="staff_recent_clients_pkey"),
    )
    op.drop_table("LookupDrinkIngredients")
    op.drop_table("StaffRecentClients")
    op.drop_table("MedicalSurgeries")
    op.drop_table("MedicalSocialHistory")
    op.drop_table("MedicalSTDHistory")
    op.drop_table("MedicalGeneralInfoMedications")
    op.drop_table("MedicalGeneralInfoMedicationAllergy")
    op.drop_table("MedicalGeneralInfo")
    op.drop_table("MedicalExternalMR")
    op.drop_table("LookupDrinks")
    op.drop_table("ClientClinicalCareTeam")
    op.drop_index(
        op.f("ix_UserTokensBlacklist_token"), table_name="UserTokensBlacklist"
    )
    op.drop_table("UserTokensBlacklist")
    op.drop_table("MedicalLookUpSTD")
    op.drop_table("LookupGoals")
    # ### end Alembic commands ###
