#!/usr/bin/env python3

import os
import liquidtime as lq

token = os.environ['LP_TOKEN']
workspace_id = os.environ['LP_WORKSPACE_ID']


def test_headers():
    assert lq.headers(token) == {'Authorization': f"Bearer {token}"}
