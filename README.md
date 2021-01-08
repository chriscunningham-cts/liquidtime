# `liquidtime` README

This is a simple Python application which can be used to fill in Liquid Planner
timesheets.

## Installation

-   Clone this repository
-   Change to its root directory (or open it in a vscode dev container)
-   Run `python setup.py`
-   Run `pip install liquidtime.egg`

## Credentials

First, create an API token by logging into the LP Web interface, clicking on
your user icon and selecting `Settings -> My Settings -> My API Tokens`, then
clicking `Add New Token`, filling in a name and clicking `Save`.

You can immediately test if it's working by querying your current timesheet:

```bash
liquidtime get-timesheet=entries --token XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

(Replace the token with the one you generated.)

This should display your timesheet for today.

You can set the `LP_TOKEN` environment variable to avoid having to pass the
token in every time.

## Usage

```
./liquidtime.py
Usage: liquidtime.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-timesheet-entries
  load-config
```

## Timesheet files

See the [sample config file](sample_config.yaml) file for example
configuration.

## License

MIT: see [license](LICENSE).
