#!/usr/bin/env python3

import os
import liquidtime as lq
from click.testing import CliRunner


token = os.environ['LP_TOKEN']
workspace_id = os.environ['LP_WORKSPACE_ID']
member_id = os.environ['LP_MEMBER_ID']


def test_cli():
    runner = CliRunner()
    result = runner.invoke(lq.cli)
    assert result.exit_code == 0
    # assert result.output == '(help documentation)'


def test_headers():
    assert lq.headers(token) == {'Authorization': f"Bearer {token}"}


def test_get_member_id():
    assert lq.get_member_id(token) == int(member_id)
