# AlphaZero Gomoku (Hugging Face Spaces 部署指南)

Hugging Face Spaces 是目前最适合部署 AI 项目的免费平台：
1.  **无需绑定信用卡**。
2.  **永久免费的 CPU 额度** (2 vCPU + 16GB RAM)，比 Render 强 20 倍。
3.  **完美支持 Docker**。

## 部署步骤

1.  **注册账号**:
    前往 [Hugging Face](https://huggingface.co/join) 注册一个账号（需验证邮箱）。

2.  **创建 Space**:
    *   登录后，点击右上角头像 -> **New Space**。
    *   **Space Name**: 填写 `AlphaZero-Gomoku` (或任意名字)。
    *   **License**: `MIT` (可选)。
    *   **Select the Space SDK**: 选择 **Docker** (非常重要！)。
    *   **Choose a template**: 选择 **Blank**。
    *   **Space Hardware**: 保持默认的 **CPU basic (Free)**。
    *   点击 **Create Space**。

3.  **上传代码**:
    有两种方式将代码上传到 Space，**推荐使用最简单的网页上传**：

    *   在创建好的 Space 页面，点击顶部菜单的 **Files**。
    *   点击 **Add file** -> **Upload files**。
    *   将你本地文件夹中的**所有文件**（除了 `.git` 文件夹）拖拽进去。
        *   核心文件包括：`Dockerfile`, `app.py`, `requirements.txt`, `model文件`, `static/`, `templates/`, `game.py` 等。
    *   在 Commit changes 下方点击 **Commit changes to main**。

4.  **等待构建**:
    *   上传后，点击 **App** 标签页。
    *   你会看到 "Building" 的状态。等待几分钟构建完成。
    *   出现 "Running" 后，你就能看到游戏界面了！

## 为什么这一步能解决速度问题？
Hugging Face 提供的免费 CPU 是 **2核 Xeon**，配合 16GB 大内存，对于我们优化的 PyTorch 模型来说，算力绰绰有余，下棋速度会非常流畅。
