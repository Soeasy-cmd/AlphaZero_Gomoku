# AlphaZero Gomoku Web App

这是一个基于 AlphaZero 算法实现的五子棋 AI 的 Web 版本。项目使用 Flask 作为后端，HTML5 Canvas 作为前端。

## 项目结构

*   `app.py`: Flask 应用入口，负责处理游戏逻辑和 AI 推理。
*   `templates/index.html`: 游戏前端界面。
*   `static/`:包含 CSS 样式和 JS 脚本。
*   `model_best_policy_8_8_5.model`: 训练好的 AI 模型 (8x8 棋盘)。
*   `requirements.txt`: Python 依赖包。
*   `Procfile`: Render 部署配置文件。

## 本地运行

1.  安装依赖:
    ```bash
    pip install -r requirements.txt
    ```

2.  运行 Flask 应用:
    ```bash
    python app.py
    ```

3.  在浏览器中打开: `http://127.0.0.1:5000`

## Render 部署步骤

1.  **推送到 GitHub**:
    将本项目代码推送到你新建的 GitHub 仓库 `AlphaZero_Gomoku`。

    ```bash
    git init
    git add .
    git commit -m "Initial commit for Web Deployment"
    git branch -M main
    git remote add origin https://github.com/你的用户名/AlphaZero_Gomoku.git
    git push -u origin main
    ```

2.  **创建 Render 服务**:
    *   注册并登录 [Render](https://render.com/)。
    *   点击 **"New +"** 按钮，选择 **"Web Service"**。
    *   选择 **"Build and deploy from a Git repository"**。
    *   连接你的 GitHub 账号，并选择 `AlphaZero_Gomoku` 仓库。

3.  **配置服务**:
    *   **Name**: 给你的服务起个名字 (例如 `alphazero-gomoku`)。
    *   **Region**: 选择离你最近的节点 (例如 Singapore)。
    *   **Branch**: `main` (或者是你 push 的分支名)。
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt` (Render 通常会自动检测)。
    *   **Start Command**: `gunicorn app:app` (Render 通常会自动从 Procfile 检测)。
    *   Plan 选择 **Free**。

4.  **部署**:
    点击 **"Create Web Service"**。Render 会开始构建并部署你的应用。等待几分钟，你会得到一个 `.onrender.com` 的网址，访问即可开始下棋！
