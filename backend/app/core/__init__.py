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

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    CatWikiError,
    ConflictException,
    DatabaseException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
    UnauthorizedException,
)

# 避免循环导入，deps 中导入了 database，database 导入了 config
# 如果需要使用 deps，请直接导入 app.core.deps

__all__ = [
    "settings",
    "CatWikiError",
    "NotFoundException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "ConflictException",
    "DatabaseException",
    "ServiceUnavailableException",
]
