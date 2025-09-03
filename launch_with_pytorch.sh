#!/bin/zsh
set -euo pipefail

# 设置应用使用的 PyTorch 路径（Python 3.10 版轮子）
export PYTHONPATH="/Users/edy/code/cursor/baishi/site-packages310/extracted:${PYTHONPATH:-}"
export DYLD_LIBRARY_PATH="/Users/edy/code/cursor/baishi/site-packages310/extracted/torch/lib:${DYLD_LIBRARY_PATH:-}"

# 修复部分环境下证书链不可用导致的 HTTPS 验证失败
# 优先使用系统 CA 证书；若需要，可改为指向 certifi 的证书
# 使用打包的 CA 证书（如不可用再回退到系统证书）
export SSL_CERT_FILE="/Users/edy/code/cursor/baishi/assets/cacert.pem"
export REQUESTS_CA_BUNDLE="/Users/edy/code/cursor/baishi/assets/cacert.pem"
export CURL_CA_BUNDLE="/Users/edy/code/cursor/baishi/assets/cacert.pem"

# 启动应用
exec "/Users/edy/code/cursor/baishi/百世.app/Contents/MacOS/百世"


