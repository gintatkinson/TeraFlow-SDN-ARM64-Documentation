# Copyright 2022-2025 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging, requests
from flask import Blueprint, Response, request

LOGGER = logging.getLogger(__name__)
grafana = Blueprint('grafana', __name__)

GRAFANA_URL = 'http://localhost:3000'

@grafana.route('/grafana/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'{GRAFANA_URL}/grafana/{path}'
    if request.query_string:
        url += f'?{request.query_string.decode("utf-8")}'
    
    try:
        # Strip Origin and Referer headers to bypass Grafana's "Origin not allowed" CSRF check
        headers = {key: value for (key, value) in request.headers if key.lower() not in ['host', 'origin', 'referer']}
        
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(response.content, response.status_code, headers)
    except Exception as e:
        LOGGER.error(f'Error proxying to Grafana: {str(e)}')
        return f'Error proxying to Grafana: {str(e)}', 500

@grafana.route('/grafana/')
@grafana.route('/grafana')
def proxy_root():
    return proxy('')
