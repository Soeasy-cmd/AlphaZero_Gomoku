# AlphaZero Gomoku Web App (Railway Deployment)

这是一个基于 AlphaZero 算法实现的五子棋 AI 的 Web 版本。项目使用 Flask 作为后端，HTML5 Canvas 作为前端。

## 部署到 Railway 步骤

Railway 是一个非常快速且开发者友好的部署平台，比 Render 更容易配置。

1.  **准备 GitHub 仓库**:
    *   如果你还没有推送到 GitHub，请先推送：
        ```bash
        git add .
        git commit -m "Prepare for Railway deployment"
        git push origin main
        ```
    *   *如果命令行推送有问题，请继续使用网页上传的方式保持代码同步。*

2.  **创建 Railway 项目**:
    *   访问 [Railway 官网](https://railway.app/) 并登录（推荐使用 GitHub 账号登录）。
    *   点击 **"New Project"** -> **"Deploy from GitHub repo"**。
    *   选择你的仓库 `AlphaZero_Gomoku`。
    *   点击 **"Deploy Now"**。

3.  **配置域名 (可选)**:
    *   部署完成后，点击你的服务方块。
    *   进入 **Settings** 标签页。
    *   找到 **Networking** -> **Generate Domain**。
    *   你会获得一个类似 `xxx.up.railway.app` 的网址，点击即可访问游戏。

## 项目文件说明

*   `app.py`: 核心 Flask 应用。
*   `railway.json`: Railway 专用配置文件，指定了构建方式和启动命令。
*   `requirements.txt`: 依赖列表（已优化 PyTorch CPU 版本）。
