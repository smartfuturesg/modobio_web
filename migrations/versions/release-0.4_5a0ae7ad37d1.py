"""release_4
- Add LookupTelehealthSessionDuration
- Add LookupSubscriptions for subscription types
- Add LookupClientBookingWindow
- Add LookupCountriesOfOperations
- Update UserSubscriptions table
- Add LookupNotifications
- Add UserNotifications
- Add LookupTransactionTypes
- Add LookupProfessionalAppointmentConfirmationWindow
- Add LookupDefaultHealthMetrics
- Add ClientTransactionHistory
- Add TelehealthQueueClientPool
- Add LookupTerritoriesofOperation
- Add TelehealthMeetingRooms
- Add SystemVariables
- Add StaffOperationalTerritories
- Add SystemTelehealthSessionCosts


Revision ID: 5a0ae7ad37d1
Revises: d4b6966523ba
Create Date: 2021-01-05 18:05:14.288685

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5a0ae7ad37d1"
down_revision = "d4b6966523ba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "LookupTelehealthSessionDuration",
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
        sa.Column("session_duration", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupSubscriptions",
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
        sa.Column("sub_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True),
        sa.Column("frequency", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("sub_id"),
    )
    op.create_table(
        "LookupClientBookingWindow",
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
        sa.Column("booking_window", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupCountriesOfOperations",
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
        sa.Column("country", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.add_column(
        "UserSubscriptions",
        sa.Column("subscription_status", sa.String(), nullable=True),
    )
    op.add_column(
        "UserSubscriptions",
        sa.Column("subscription_type_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        None,
        "UserSubscriptions",
        "LookupSubscriptions",
        ["subscription_type_id"],
        ["sub_id"],
    )
    op.drop_column("UserSubscriptions", "subscription_type")
    op.drop_column("UserSubscriptions", "subscription_rate")
    op.create_table(
        "LookupNotifications",
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
        sa.Column(
            "notification_type_id", sa.Integer(), autoincrement=True, nullable=False
        ),
        sa.Column("notification_type", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("background_color", sa.String(), nullable=True),
        sa.Column("symbol_color", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("notification_type_id"),
    )
    op.create_table(
        "UserNotifications",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("time_to_live", sa.DateTime(), nullable=True),
        sa.Column("is_staff", sa.Boolean(), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["notification_type_id"],
            ["LookupNotifications.notification_type_id"],
        ),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupTransactionTypes",
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
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupProfessionalAppointmentConfirmationWindow",
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
        sa.Column("confirmation_window", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupDefaultHealthMetrics",
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
        sa.Column("sex", sa.String(length=2), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("bmi_underweight", sa.Float(), nullable=True),
        sa.Column("bmi_normal_min", sa.Float(), nullable=True),
        sa.Column("bmi_normal_max", sa.Float(), nullable=True),
        sa.Column("bmi_overweight_min", sa.Float(), nullable=True),
        sa.Column("bmi_overweight_max", sa.Float(), nullable=True),
        sa.Column("bmi_obese", sa.Float(), nullable=True),
        sa.Column("ecg_metric_1", sa.String(), nullable=True),
        sa.Column("ecg_metric_2_bpm_min", sa.Integer(), nullable=True),
        sa.Column("ecg_metric_2_bpm_max", sa.Integer(), nullable=True),
        sa.Column("sp_o2_spot_check", sa.Integer(), nullable=True),
        sa.Column("sp_o2_nighttime_avg", sa.Integer(), nullable=True),
        sa.Column("sleep_total_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_deep_min_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_deep_max_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_rem_min_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_rem_max_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_quality_min_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_quality_max_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_light_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_time_awake_minutes", sa.Integer(), nullable=True),
        sa.Column("sleep_latency_minutes", sa.Integer(), nullable=True),
        sa.Column("bedtime_consistency_minutes", sa.Integer(), nullable=True),
        sa.Column("wake_consistency_minutes", sa.Integer(), nullable=True),
        sa.Column("heart_rate_rest_average_min", sa.Integer(), nullable=True),
        sa.Column("heart_rate_rest_average_max", sa.Integer(), nullable=True),
        sa.Column("heart_rate_rest_lowest_min", sa.Integer(), nullable=True),
        sa.Column("heart_rate_rest_lowest_max", sa.Integer(), nullable=True),
        sa.Column("heart_rate_walking_min", sa.Integer(), nullable=True),
        sa.Column("heart_rate_walking_max", sa.Integer(), nullable=True),
        sa.Column("heart_rate_average_min", sa.Integer(), nullable=True),
        sa.Column("heart_rate_average_max", sa.Integer(), nullable=True),
        sa.Column(
            "heart_rate_variability_average_milliseconds", sa.Integer(), nullable=True
        ),
        sa.Column(
            "heart_rate_variability_highest_milliseconds", sa.Integer(), nullable=True
        ),
        sa.Column("respiratory_rate_min_per_minute", sa.Integer(), nullable=True),
        sa.Column("respiratory_rate_max_per_minute", sa.Integer(), nullable=True),
        sa.Column("body_temperature_deviation_fahrenheit", sa.Float(), nullable=True),
        sa.Column("steps_per_day", sa.Integer(), nullable=True),
        sa.Column("steps_walking_equivalency_miles", sa.Integer(), nullable=True),
        sa.Column("calories_total", sa.Integer(), nullable=True),
        sa.Column("calories_active_burn_min", sa.Integer(), nullable=True),
        sa.Column("calories_active_burn_max", sa.Integer(), nullable=True),
        sa.Column("inactivity_minutes", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "ClientTransactionHistory",
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
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("payment_method", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "TelehealthQueueClientPool",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profession_type", sa.String(), nullable=True),
        sa.Column("target_date", sa.DateTime(), nullable=True),
        sa.Column("priority", sa.Boolean(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("medical_gender", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "LookupTerritoriesofOperation",
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
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("sub_territory", sa.String(), nullable=True),
        sa.Column("sub_territory_abbreviation", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "TelehealthMeetingRooms",
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
        sa.Column("room_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_name", sa.String(), nullable=True),
        sa.Column("client_user_id", sa.Integer(), nullable=False),
        sa.Column("staff_user_id", sa.Integer(), nullable=False),
        sa.Column("client_access_token", sa.String(), nullable=True),
        sa.Column("staff_access_token", sa.String(), nullable=True),
        sa.Column("room_status", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["client_user_id"],
            ["User.user_id"],
        ),
        sa.ForeignKeyConstraint(
            ["staff_user_id"],
            ["User.user_id"],
        ),
        sa.PrimaryKeyConstraint("room_id"),
    )
    op.create_table(
        "SystemVariables",
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
        sa.Column("var_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("var_name", sa.String(), nullable=True),
        sa.Column("var_value", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("var_id"),
    )
    op.create_table(
        "StaffOperationalTerritories",
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
        sa.Column("operational_territory_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["operational_territory_id"],
            ["LookupTerritoriesofOperation.idx"],
        ),
        sa.ForeignKeyConstraint(["role_id"], ["StaffRoles.idx"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["User.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idx"),
    )
    op.create_table(
        "SystemTelehealthSessionCosts",
        sa.Column("cost_id", sa.Integer(), autoincrement=True, nullable=False),
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
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("profession_type", sa.String(), nullable=False),
        sa.Column("session_cost", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "session_min_cost", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.Column(
            "session_max_cost", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.UniqueConstraint("country", "profession_type"),
        sa.PrimaryKeyConstraint("cost_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("SystemTelehealthSessionCosts"),
    op.drop_table("StaffOperationalTerritories")
    op.drop_table("SystemVariables")
    op.drop_table("TelehealthMeetingRooms")
    op.drop_table("LookupTerritoriesofOperation")
    op.drop_table("TelehealthQueueClientPool")
    op.drop_table("ClientTransactionHistory")
    op.drop_table("LookupDefaultHealthMetrics")
    op.drop_table("LookupProfessionalAppointmentConfirmationWindow")
    op.drop_table("LookupTransactionTypes")
    op.drop_table("UserNotifications")
    op.drop_table("LookupNotifications")
    op.add_column(
        "UserSubscriptions",
        sa.Column(
            "subscription_rate",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "UserSubscriptions",
        sa.Column(
            "subscription_type", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(None, "UserSubscriptions", type_="foreignkey")
    op.drop_column("UserSubscriptions", "subscription_type_id")
    op.drop_column("UserSubscriptions", "subscription_status")
    op.drop_table("LookupCountriesOfOperations")
    op.drop_table("LookupClientBookingWindow")
    op.drop_table("LookupSubscriptions")
    op.drop_table("LookupTelehealthSessionDuration")
    # ### end Alembic commands ###
