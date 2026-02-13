#!/bin/bash
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

set -e

echo "🚀 Preparing CatWiki Community Edition (OSS) Release..."

# 1. Backend Cleanup
echo "📦 Stripping Backend Enterprise (EE) Module..."
if [ -d "backend/app/ee" ]; then
    rm -rf backend/app/ee
    echo "✅ backend/app/ee removed."
fi

# 2. Prevent Import Errors
# Even though we use dynamic loading, some static analysis tools or 
# late-binding imports might complain if the package is missing.
echo "🛠️  Creating OSS compatibility bridge..."
# We don't actually need the bridge if everything is wrapped in try-except,
# but having an empty directory with __init__.py is safer for some build tools.
# mkdir -p backend/app/ee && touch backend/app/ee/__init__.py

# 3. Frontend Check (Handled by NEXT_PUBLIC_CATWIKI_EDITION)
echo "🌐 Frontend will be stripped during build using NEXT_PUBLIC_CATWIKI_EDITION=community"

# 4. Obfuscation (Optional Security)
# If you have PyArmor installed, you can enable this to protect specific files
# echo "🔐 Obfuscating core security logic..."
# pyarmor gen backend/app/core/infra/integrity.py

echo "🎉 OSS Preparation Complete!"
echo "To build/run in Community Mode:"
echo "Backend: RUN it directly (EE loader will fallback)"
echo "Frontend: NEXT_PUBLIC_CATWIKI_EDITION=community npm run build"
