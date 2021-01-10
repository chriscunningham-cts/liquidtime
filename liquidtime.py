#!/usr/bin/env python3

import requests
import click
import json
import datetime
import yaml

api_path = 'https://app.liquidplanner.com/api/v1'


def headers(token):
    return {'Authorization': f"Bearer {token}"}


def get_member_id(token):
    account_url = f"{api_path}/account"
    account = requests.get(
        account_url, headers=headers(token)
    ).json()
    return account['id']


def find_task(workspace_id, token, query):
    queries_url = f"{api_path}/workspaces/{workspace_id}/treeitems"
    params = {'filter[]': f"name={query.replace(' ', '_')}"}
    results = requests.get(
        queries_url, headers=headers(token), params=params
    ).json()
    # click.echo(json.dumps(results, indent=4, sort_keys=True))

    # the activity_id can live at one of two levels
    toplevel = [
        result for result in results if result['activity_id'] is not None
    ]
    if toplevel:
        # there is only one activity
        return toplevel[0]['activity_id'], toplevel[0]['id']
    else:
        # there are sub-activities, which all have the same activity_id
        for assignment in results[0]['assignments']:
            return assignment['activity_id'], results[0]['id']


def add_timesheet_entry(
    workspace_id, token, activity_id, task_id,
    note, work, work_performed_on, append, confirm
):
    time_add_url = f"{api_path}/workspaces/{workspace_id}/tasks/{task_id}/track_time"
    member_id = get_member_id(token)
    payload = {
        'activity_id': activity_id,
        'member_id': member_id,
        'note': note,
        'work': work,
        'work_performed_on': work_performed_on,
    }
    click.echo()
    if not confirm and not click.confirm(
        f"Adding the following work:\n{payload}\nDo you want to continue?"
    ):
        click.echo('Work not added to timesheet.')
        return None

    params = {'append': append}

    postresult = requests.post(
        time_add_url, headers=headers(token), params=params, data=payload
    ).json()
    click.echo(
        f"Added to timesheet {postresult['timesheet_entry']['timesheet_id']}."
    )
    return postresult['timesheet_entry']['timesheet_id']


def submit_timesheet(workspace_id, token, timesheet_id, confirm):
    timesheet_submit_url = f"{api_path}/workspaces/{workspace_id}/timesheets/{timesheet_id}/submit"
    if not confirm and not click.confirm(
        f"Do you want to submit timesheet {timesheet_id} as complete?"
    ):
        click.echo('Timesheet not submitted.')
        return False
    postresult = requests.post(
        timesheet_submit_url, headers=headers(token)
    ).json()
    click.echo(f"Timesheet {timesheet_id} submitted.\n{postresult}")
    return True


@click.group()
def helpme():
    pass


@click.command()
@click.option(
    "--token", '-t',
    envvar='LP_TOKEN',
    required=True,
    prompt='LP_TOKEN',
    help='Your LP API token'
)
@click.option(
    "--workspace_id", '-w',
    envvar='LP_WORKSPACE_ID',
    required=True,
    prompt='LP_WORKSPACE_ID',
    help='Your LP workspace ID'
)
@click.option(
    "--date", '-d',
    help='The date of the work',
    default=datetime.date.today()
)
def get_timesheet_entries(workspace_id, token, date):
    timesheets_url = f"{api_path}/workspaces/{workspace_id}/timesheet_entries"
    params = {'member_id': get_member_id(token)}
    if date:
        params['start_date'] = params['end_date'] = date
    timesheets = requests.get(
        timesheets_url, headers=headers(token), params=params
    ).json()

    for timesheet in timesheets:
        print(json.dumps(timesheet, indent=4, sort_keys=True))


@ click.command()
@ click.option(
    "--token", '-t',
    envvar='LP_TOKEN',
    required=True,
    prompt='LP_TOKEN',
    help='Your LP API token'
)
@click.option(
    "--workspace_id", '-w',
    envvar='LP_WORKSPACE_ID',
    required=True,
    prompt='LP_WORKSPACE_ID',
    help='Your LP workspace ID'
)
@click.option(
    "--config", '-c',
    help='The YAML file containing your timesheet information',
    required=True,
)
@click.option(
    '--append/--no-append', '-a',
    default=False,
    help='Append time to existing entries instead of overwriting',
)
@click.option(
    '--confirm/--no-confirm', '-y',
    default=False,
    help='Prompt for confirmation before adding entries',
)
def load_config(workspace_id, token, config, append, confirm):
    # click.echo(f"Parsing timesheet file {config}...")
    with open(config, 'r') as stream:
        bulk_data = yaml.safe_load(stream)

    # click.echo(bulk_data)

    timesheets = []
    for task in bulk_data['tasks']:
        activity_id, task_id = find_task(
            workspace_id, token, task['task_name']
        )
        note = task['note'] if 'note' in task else None
        work = task['work']
        work_performed_on = task['work_performed_on']
        timesheets.append(add_timesheet_entry(
            workspace_id, token, activity_id, task_id,
            note, work, work_performed_on, append, confirm
        ))
    # remove duplicates in list (and None, for non-confirmed additions)
    unique_timesheets = list(set([t for t in timesheets if t is not None]))
    click.echo(f"Timesheets to submit:\n{unique_timesheets}")
    for timesheet_id in unique_timesheets:
        submit_timesheet(workspace_id, token, timesheet_id, confirm)


helpme.add_command(get_timesheet_entries)
helpme.add_command(load_config)
