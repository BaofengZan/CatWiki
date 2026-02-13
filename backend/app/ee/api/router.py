# Copyright 2024 CatWiki Authors
#
# Licensed under the CatWiki Open Source License (Modified Apache 2.0);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/CatWiki/CatWiki/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI
from app.core.infra.config import settings


def init_ee_routes(app: FastAPI):
    """
    Inject Enterprise Edition routes into the FastAPI application.
    """
    from app.ee.api import tenants

    # We include the tenants router directly into the app with the admin prefix
    app.include_router(
        tenants.router, prefix=f"{settings.ADMIN_API_V1_STR}/tenants", tags=["admin-tenants"]
    )
