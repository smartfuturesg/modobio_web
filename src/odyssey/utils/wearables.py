

from typing import Dict, List


def oura_data_shaper(wearable_data:List[Dict] ):
    """
    Take list of raw daily data entries from oura ring and responds with a schema 
    consisting of the data to be displayed to the user

    Params
    ------
    wearable_data: dict, one day of raw data from 

    Responds
    ------
    dict
    """
    response = []

    for item in wearable_data:
        item_summary = {}
        item_summary['date'] = item['date']
        item_summary['activity'] = {}
        item_summary['calories'] = {}
        item_summary['sleep'] = {}
        item_summary['vitals'] = {}
        activity = item['data'].get('activity')
        sleep = item['data'].get('sleep', []) # sleep entry is a list of sleep events (naps, rest, sleep)
        
        # calories, step data
        if activity:
            item_summary['calories']['calories_active'] =  int(activity.get('cal_active',0))
            item_summary['calories']['calories_total'] =  int(activity.get('cal_total',0))
            item_summary['calories']['calories_bmr'] =  int(activity.get('cal_total',0)) - int(activity.get('cal_active',0))
            item_summary['activity']['steps'] =  int(activity.get('steps',0))
        
        if len(sleep) > 0:
            # takes the last rest period of the day
            item_summary['vitals']['hr_resting_bpm'] =  float(sleep[-1].get('hr_average', 0)) # in lieu of hr data during non-rest periods
            item_summary['sleep']['hr_resting_bpm'] =  float(sleep[-1].get('hr_average', 0)) 
            item_summary['sleep']['hrv_ms_avg'] =  float(sleep[-1].get('rmssd', 0)) 
            item_summary['sleep']['sleep_duration_seconds'] =  int(sleep[-1].get('total', 0)) 
            item_summary['sleep']['in_bed_duration_seconds'] =  int(sleep[-1].get('duration', 0)) 
            item_summary['sleep']['respiratory_rate_bpm_avg'] =  float(sleep[-1].get('breath_average', 0)) 
            item_summary['sleep']['bed_time_start'] =  sleep[-1].get('bedtime_start', '') 
            item_summary['sleep']['bed_time_end'] =  sleep[-1].get('bedtime_end', '') 

        response.append(item_summary)

    return response

def applewatch_data_shaper(wearable_data:List[Dict]):
    """
    Take list of raw daily data entries from apple watch and responds with a schema 
    consisting of the data to be displayed to the user

    Params
    ------
    wearable_data: dict, one day of raw data from 

    Responds
    ------
    dict
    """
    response = []

    for item in wearable_data:
        item_summary = {}
        item_summary['date'] = item['date']
        item_summary['activity'] = {}
        item_summary['calories'] = {}
        item_summary['sleep'] = {}
        item_summary['vitals'] = {}
        activity = item['data'].get('activity')
        fitness = item['data'].get('fitness')
        sleep = item['data'].get('sleep', {}) 
        asleep = sleep.get('asleep', []) # sleep entry is a list of sleep events (naps, rest, sleep)
        vitals = item['data'].get('vitals') 
        body = item['data'].get('body') 
        
        if fitness:
            item_summary['activity']['steps'] =  fitness.get('stepCount', 0)
        if activity:
            item_summary['calories']['calories_active'] =  fitness.get('activeEnergyBurnedCal', 0)
        if len(asleep) > 0:
            item_summary['sleep']['sleep_duration_seconds'] =  int(asleep[-1].get('durationMS', 0))/1000.0 if asleep[-1].get('durationMS') else None  # takes the last rest period of the day
        if vitals:
            rhr_data = vitals.get('restingHeartRateBmp', {})
            hrv_data = vitals.get('heartRateVariabilitySec', {})
            respiratory_rate_data = vitals.get('respiratoryRateBmp', {})
            item_summary['vitals']['hr_resting_bpm'] =  rhr_data.get('average', 0) 
            item_summary['vitals']['hrv_ms_avg'] =  hrv_data.get('average', 0) 
            item_summary['vitals']['respiratory_rate_bpm_avg'] = respiratory_rate_data.get('average', 0) 
        if body:
            body_temp_data = body.get('bodyTemperatureCelsius',{})
            item_summary['vitals']['body_temp_celsius'] = body_temp_data.get('average', 0)
          
        response.append(item_summary)
    return response


def fitbit_data_shaper(wearable_data:List[Dict]):
    """
    Take list of raw daily data entries from fitbit and responds with a schema 
    consisting of the data to be displayed to the user

    https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date/

    Params
    ------
    wearable_data: dict, one day of raw data from 

    Responds
    ------
    dict
    """
    response = []

    for item in wearable_data:
        item_summary = {}
        item_summary['date'] = item['date']

        item = item['data']

        item_summary['activity'] = {}
        item_summary['calories'] = {}
        item_summary['sleep'] = {}
        item_summary['vitals'] = {}
        heart = item.get('activities-heart') 
        sleep = item.get('sleep',[])
        
        item_summary['activity']['steps'] =  max(item.get('activities-tracker-steps', 0), item.get('activities-steps', 0))
        
        item_summary['calories']['calories_active'] =  max(item.get('activities-activityCalories', 0), item.get('activities-tracker-activityCalories', 0))
        item_summary['calories']['calories_total'] =  max(item.get('activities-calories', 0), item.get('activities-tracker-calories', 0))
        item_summary['calories']['calories_bmr'] =  item.get('activities-caloriesBMR', 0)


        item_summary['vitals']['hr_resting_bpm'] =  heart.get('restingHeartRate', 0)

        
        if len(sleep) > 0:
            for session in sleep:
                if session.get('isMainSleep'):
                    item_summary['sleep']['sleep_duration_seconds'] =  int(session.get('duration', 0))/1000.0 if session.get('durationMS') else None  # takes the last rest period of the day
                    item_summary['sleep']['bed_time_start'] = session.get('startTime', '')
                    item_summary['sleep']['bed_time_end'] = session.get('endTime', '')
                    item_summary['sleep']['in_bed_duration_seconds'] = session.get('timeInBed', 0) * 60
          
        response.append(item_summary)
    return response