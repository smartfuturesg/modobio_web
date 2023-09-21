from datetime import datetime, timedelta
from math import e


def sleep_durations_aggregation(
    user_id: int, device: str, start_date: datetime, end_date: datetime
):
    return [
        # Filter by user_id and ensure there is data in the data.sleep path
        {
            "$match": {
                "user_id": user_id,
                "wearable": device,
                "data.sleep": {"$exists": True, "$ne": None},
                "timestamp": {
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date + timedelta(days=1),
                },  # timestamp filters start of sleep event. we are interested in when the sleep event ends
                "data.sleep.metadata.end_time": {
                    "$gte": start_date,
                    "$lte": end_date
                    + timedelta(
                        days=1
                    ),  # added an extra day to ensure we get the last sleep event
                },
            }
        },
        {
            "$addFields": {
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$data.sleep.metadata.end_time",
                    }
                }
            }
        },
        {"$group": {"_id": "$date", "entries": {"$push": "$$ROOT"}}},
        {
            "$match": {
                "entries": {
                    "$elemMatch": {
                        "data.sleep.metadata.is_nap": False,
                    }
                }
            }
        },
        {"$unwind": "$entries"},
        {
            "$group": {
                "_id": "$_id",
                "total_duration_asleep": {
                    "$sum": "$entries.data.sleep.sleep_durations_data.asleep.duration_asleep_state_seconds"
                },
                "total_duration_REM": {
                    "$sum": "$entries.data.sleep.sleep_durations_data.asleep.duration_REM_sleep_state_seconds"
                },
                "total_duration_light_sleep": {
                    "$sum": "$entries.data.sleep.sleep_durations_data.asleep.duration_light_sleep_state_seconds"
                },
                "total_duration_deep_sleep": {
                    "$sum": "$entries.data.sleep.sleep_durations_data.asleep.duration_deep_sleep_state_seconds"
                },
                "total_duration_in_bed": {
                    "$sum": "$entries.data.sleep.sleep_durations_data.other.duration_in_bed_seconds"
                },
            }
        },
        {
            "$project": {
                "date": "$_id",
                "_id": 0,
                "total_duration_asleep": 1,
                "total_duration_REM": 1,
                "total_duration_light_sleep": 1,
                "total_duration_deep_sleep": 1,
                "total_duration_in_bed": 1,
            }
        },
    ]


def resting_hr_daily_aggregation(
    user_id: int, device: str, start_date: datetime, end_date: datetime
):
    """
    Resting HR aggregation for the daily data type.
    """
    return [
        {
            "$match": {
                "user_id": user_id,
                "wearable": device,
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$addFields": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
            }
        },
        {
            "$project": {
                "date": 1,
                "heartrateValues": [
                    "$data.daily.heart_rate_data.summary.min_hr_bpm",
                    "$data.daily.heart_rate_data.summary.resting_hr_bpm",
                    "$data.sleep.heart_rate_data.summary.min_hr_bpm",
                    "$data.sleep.heart_rate_data.summary.resting_hr_bpm",
                ],
            }
        },
        {
            "$addFields": {
                "heartrateValues": {
                    "$filter": {
                        "input": "$heartrateValues",
                        "as": "rate",
                        "cond": {
                            "$and": [
                                {"$ne": ["$$rate", None]},
                                {"$ne": ["$$rate", 0]},
                            ]
                        },
                    }
                }
            }
        },
        {"$match": {"heartrateValues": {"$ne": []}}},
        {"$group": {"_id": "$date", "min_hr": {"$min": "$heartrateValues"}}},
        {
            "$project": {
                "date": "$_id",
                "_id": 0,
                "resting_hr": {"$arrayElemAt": ["$min_hr", 0]},
            }
        },
    ]


def resting_hr_sleep_aggregation(
    user_id: int, device: str, start_date: datetime, end_date: datetime
):
    """
    Resting HR aggregation for the sleep data type.
    """
    return [
        {
            "$match": {
                "user_id": user_id,
                "wearable": device,
                "timestamp": {
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date + timedelta(days=1),
                },
                "data.sleep.metadata.end_time": {
                    "$gte": start_date,
                    "$lte": end_date
                    + timedelta(
                        days=1
                    ),  # added an extra day to ensure we get the last sleep event
                },
            }
        },
        {
            "$addFields": {
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$data.sleep.metadata.end_time",
                    }
                }
            }
        },
        {
            "$project": {
                "date": 1,
                "heartrateValues": [
                    "$data.sleep.heart_rate_data.summary.min_hr_bpm",
                    "$data.sleep.heart_rate_data.summary.resting_hr_bpm",
                ],
            }
        },
        {
            "$addFields": {
                "heartrateValues": {
                    "$filter": {
                        "input": "$heartrateValues",
                        "as": "rate",
                        "cond": {
                            "$and": [
                                {"$ne": ["$$rate", None]},
                                {"$ne": ["$$rate", 0]},
                            ]
                        },
                    }
                }
            }
        },
        {"$match": {"heartrateValues": {"$ne": []}}},
        {"$group": {"_id": "$date", "min_hr": {"$min": "$heartrateValues"}}},
        {
            "$project": {
                "date": "$_id",
                "_id": 0,
                "resting_hr": {"$arrayElemAt": ["$min_hr", 0]},
            }
        },
    ]


def steps_aggregation(
    user_id: int, device: str, start_date: datetime, end_date: datetime
):
    return [
        {
            "$match": {
                "user_id": user_id,
                "wearable": device,
                "data.daily.distance_data": {"$exists": True, "$ne": None},
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$addFields": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
            }
        },
        {
            "$group": {
                "_id": "$date",
                "total_distance_meters": {
                    "$sum": "$data.daily.distance_data.distance_meters"
                },
                "total_steps": {"$sum": "$data.daily.distance_data.steps"},
            }
        },
        {
            "$project": {
                "date": "$_id",
                "_id": 0,
                "total_distance_meters": 1,
                "total_steps": 1,
            }
        },
    ]


def calories_aggregation(
    user_id: int, device: str, start_date: datetime, end_date: datetime
):
    return [
        {
            "$match": {
                "user_id": user_id,
                "wearable": device,
                "data.daily.calories_data.total_burned_calories": {
                    "$exists": True,
                    "$ne": None,
                },
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$addFields": {
                "total_calories": "$data.daily.calories_data.total_burned_calories",
                "active_calories": "$data.daily.calories_data.net_activity_calories",
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            }
        },
        {
            "$project": {
                "date": 1,
                "_id": 0,
                "total_calories": 1,
                "active_calories": 1,
            }
        },
    ]
