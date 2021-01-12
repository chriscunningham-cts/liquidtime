# `liquidtime` README

This is a simple Python application which can be used to fill in Liquid Planner
timesheets. It was written for internal use by [CTS](https://cts.co).

## Installation

-   Clone this repository
-   Change to its root directory (or open it in a vscode dev container)
-   Run `python setup.py bdist_wheel`
-   Run `pip install dist/liquidtime*.whl`

## Credentials

1.  Set the `LP_WORKSPACE_ID` environment variable to the Liquid Planner
    workspace you're using. For CTS this is `181807`.
2.  Create an API token by logging into the LP Web interface, clicking on
    your user icon and selecting `Settings -> My Settings -> My API Tokens`,
    then clicking `Add New Token`, filling in a name and clicking `Save`.

You can immediately test if it's working by querying your current timesheet:

```bash
liquidtime get-timesheet-entries --token XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

(Replace the token with the one you generated.)

This should display your timesheet for today.

You can set the `LP_TOKEN` environment variable to avoid having to pass the
token in every time.

## Usage

Run `liquidtime` for runtime documentation.

```
liquidtime
Usage: liquidtime [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-timesheet-entries
  load-config
```

The primary command is `liquidtime load-config -c <configfile>`, which will
parse a YAML configuration file (such as the
[sample config file](sample_config.yaml)) and add all the entries within to
the user associated with your API token. For each work entry you will be
prompted to confirm before the work is added; the `--confirm` flag will bypass
this.

The tool will overwrite existing data for the task in question on a given day
unless the `--append` option is used, in which case it will append time to
existing work on a particular day.

Once add work has been added, the tool will prompt you to submit any timesheets
it has added to. Note that this prevents further additions, so only do this
once you're ready to submit a complete timesheet.

## Timesheet files

See the [sample config file](sample_config.yaml) file for example
configuration. Each entry in the `tasks` list must contain the following:

-   `task_name`: This is the unique name of the task to record
    time against in Liquid Planner. You can obtain this through the Web
    interface.
-   `work`: The number of hours recorded against the task that day.
-   `work_performed_on`: The date of the work.

You can additionally set the following per-task:

-   `note`: An entry for the notes field. This can contain line breaks.

There can be multiple entries for a single date, to account for working on more
than one task per day.

## TODO

-   Permit relative or regular dates in the config file instead of absolute
    ones, e.g. `Monday`.
-   Implement additional submission fields, e.g. estimates.
-   Add unit tests.
-   Make Click configuration more idiomatic.
-   Push to PyPI.

## Authors

-   [Chris Cunningham](mailto:chris.cunningham@cts.co)

## License

MIT: see [license](LICENSE).
