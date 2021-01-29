#!/usr/bin/env python3

import requests
import click
import json
import datetime
import yaml

__description__ = 'Liquid Planner timesheet tool'
__version__ = 0.1

api_path = 'https://app.liquidplanner.com/api/v1'


def headers(token):
    return {'Authorization': f"Bearer {token}"}


def handle_errors(response, message):
    if response.status_code == 200:
        return response.json()

    try:
        f = response.json()
        failure_code = f['error']
        failure_message = f['message']
    except ValueError:
        failure_code = f"HTTP {response.status_code}"
        failure_message = response.text
    raise Exception(
        f"{message}: {failure_code}\n"
        f"{failure_message}"
    )


def get_member_id(token):
    account_url = f"{api_path}/account"
    account = handle_errors(
        requests.get(account_url, headers=headers(token)),
        'Failed to get member ID'
    )
    return account['id']


def find_task(workspace_id, token, query):
    queries_url = f"{api_path}/workspaces/{workspace_id}/treeitems"
    params = {'filter[]': f"name={query.replace(' ', '_')}"}
    results = handle_errors(
        requests.get(queries_url, headers=headers(token), params=params),
        'Failed to get tasks'
    )
    # The activity_id can live at one of two levels
    toplevel = [
        result for result in results if result['activity_id'] is not None
    ]
    if toplevel:
        # There is only one activity
        return toplevel[0]['activity_id'], toplevel[0]['id']
    else:
        # There are sub-activities, which all have the same activity_id (if it
        # is set, but it can be null)
        for result in results:
            for assignment in result['assignments']:
                if assignment['activity_id'] is not None:
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

    postresult = handle_errors(
        requests.post(
            time_add_url, headers=headers(token), params=params, data=payload
        ),
        'Failed to add work to timesheet'
    )
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
    postresult = handle_errors(
        requests.post(timesheet_submit_url, headers=headers(token)),
        'Failed to submit timesheet'
    )
    click.echo(f"Timesheet {timesheet_id} submitted.\n{postresult}")
    return True


@click.group()
@click.version_option(prog_name=__description__, version=__version__)
@click.option(
    "--token", '-t',
    envvar='LP_TOKEN', prompt='LP_TOKEN',
    required=True,
    help='Your LP API token',
)
@click.option(
    "--workspace_id", '-w',
    envvar='LP_WORKSPACE_ID', prompt='LP_WORKSPACE_ID',
    required=True,
    help='Your LP workspace ID',
)
@click.pass_context
def cli(ctx, token, workspace_id):
    ctx.obj = {'workspace_id': workspace_id, 'token': token}


@click.command()
@click.option(
    "--date", '-d',
    default=datetime.date.today(),
    help='The date of the work',
)
@click.pass_context
def get_timesheet_entries(ctx, date):
    timesheets_url = f"{api_path}/workspaces/{ctx.obj['workspace_id']}/timesheet_entries"
    params = {'member_id': get_member_id(ctx.obj['token'])}
    if date:
        params['start_date'] = params['end_date'] = date
    timesheets = handle_errors(
        requests.get(timesheets_url, headers=headers(
            ctx.obj['token']), params=params),
        'Failed to get timesheet entries'
    )
    for timesheet in timesheets:
        click.echo(json.dumps(timesheet, indent=4, sort_keys=True))


@click.command()
@click.option(
    "--config", '-c',
    required=True,
    help='The YAML file containing your timesheet information',
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
@click.pass_context
def load_config(ctx, config, append, confirm):
    with open(config, 'r') as stream:
        bulk_data = yaml.safe_load(stream)

    timesheets = []
    for task in bulk_data['tasks']:
        activity_id, task_id = find_task(
            ctx.obj['workspace_id'], ctx.obj['token'], task['task_name']
        )
        note = task['note'] if 'note' in task else None
        work = task['work']
        work_performed_on = task['work_performed_on']
        timesheets.append(add_timesheet_entry(
            ctx.obj['workspace_id'], ctx.obj['token'], activity_id, task_id,
            note, work, work_performed_on, append, confirm
        ))
    # Remove duplicates in list (and None, for non-confirmed additions)
    unique_timesheets = list({t for t in timesheets if t is not None})
    if not unique_timesheets:
        click.echo('No timesheets to submit.')
        return
    else:
        click.echo(f"Timesheets to submit:\n{unique_timesheets}")
        for timesheet_id in unique_timesheets:
            submit_timesheet(
                ctx.obj['workspace_id'],
                ctx.obj['token'], timesheet_id, confirm
            )


cli.add_command(get_timesheet_entries)
cli.add_command(load_config)
