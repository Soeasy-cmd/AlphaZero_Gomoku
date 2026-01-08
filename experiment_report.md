# 实验报告：AlphaZero 五子棋 Web 部署与实现

作者：小组（组长：邓跃设 23040108）

项目直连网址：https://so-easy-alphazero-gomoku.hf.space

## 一、实验目的

- 将开源的 AlphaZero_Gomoku 项目（参考代码与模型来自：https://github.com/junxiaosong/AlphaZero_Gomoku）部署为可交互的 Web 应用。
- 优化运行性能，保证用户在免费托管环境下能有可用体验。
- 撰写本次工作与分工报告，记录实现过程与注意事项。

## 二、实验环境与限制

- 开发语言：Python 3.x
- 主要依赖：`Flask`, `numpy`, `gunicorn`, `torch`（CPU 版）
- 托管平台：Hugging Face Spaces（Docker / CPU Basic）
- 说明：我们使用的是开源训练好的模型文件（例如 `best_policy_8_8_5.model`），本实验**不进行模型训练**，仅进行推理与部署。训练资源与时间需求较高，超出本实验条件。

## 三、项目结构（主要文件）

- `app.py`：Flask 后端，提供 `/api/move` 接口并加载策略价值网络与 MCTS。
- `game.py`：棋盘与游戏规则实现。
- `mcts_alphaZero.py`：MCTS 算法实现（AlphaZero 风格）。
- `policy_value_net_numpy.py`：原始的 numpy 推理实现（参考）。
- `policy_value_net_pytorch.py`：我们集成或改写为 PyTorch 推理以提高速度。
- `static/`、`templates/`：前端页面与静态资源（HTML、CSS、JS）。
- 模型文件：`best_policy_8_8_5.model`（预训练模型，来自原仓库）。

## 四、算法与实现要点

1. AlphaZero 思路概述：
   - 使用策略-价值网络（policy-value network）对局面进行估值与给出先验概率分布。
   - 使用 MCTS（蒙特卡洛树搜索）结合网络输出进行多次模拟（playout），最终选取访问次数或概率最高的动作。

2. 我们的实现细节：
   - 原项目包含基于 Theano/纯 numpy 的推理实现。该实现可读性好但在普通 CPU 上速度较慢。
   - 为提高运行速度并降低部署平台超时风险，我们将推理实现改为 PyTorch（CPU）版本，利用 PyTorch 的底层加速来提升推理效率。
   - 在 Web 后端中采用无状态（stateless）交互：前端上传当前的落子历史，后端重建棋盘并返回 AI 的下一步。这种方式便于横向扩展并适合 HTTP 服务。

3. 参数与折中：
   - `n_playout`（MCTS 模拟次数）是性能与棋力的权衡。免费托管环境下初始选用较小模拟次数以保证响应速度，后续可根据平台资源调整。

## 五、部署过程（要点）

1. 将所有项目文件上传到 Hugging Face Spaces（选择 SDK 为 Docker），并在 `README.md` 中加入 YAML metadata：

```
---
title: AlphaZero Gomoku
emoji: 
colorFrom: gray
colorTo: gray
sdk: docker
pinned: false
app_port: 7860
---
```

2. 在项目根目录添加 `Dockerfile`，示例：

```
FROM python:3.9-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
RUN mkdir -p /code/.cache && chmod -R 777 /code
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
```

3. `requirements.txt` 中包含 `--extra-index-url https://download.pytorch.org/whl/cpu` 行以便安装 PyTorch CPU 轮子，示例格式：

```
--extra-index-url https://download.pytorch.org/whl/cpu
Flask==3.0.0
numpy
gunicorn
torch
```

4. 上传完成后等待 Spaces 自动构建，构建成功后即可通过直连域名访问：`https://so-easy-alphazero-gomoku.hf.space`。

## 六、前端与交互说明

- 前端使用 HTML5 Canvas 绘制棋盘与棋子，使用 `static/js/script.js` 处理点击事件与和后端的 AJAX 通信。
- 前端将当前落子历史（一个整型序列）通过 POST 提交到 `/api/move`，后端返回 AI 的落子编号与是否结束信息。

## 七、测试与验证

- 本实验在 Hugging Face Spaces 的 CPU Basic 环境上完成部署并验证可以正常下棋，AI 响应时间取决于 `n_playout` 值与平台 CPU 性能。
- 由于没有训练过程，本次结果仅用于功能性验证与部署性能评估。

## 八、分工（随机分配）

组长（总体协调与部署）：邓跃设 23040108

- 伍原宏 23012656：后端与模型接入（负责 `app.py` 与模型加载逻辑）。
- 张耀尹 23012677：前端与可视化（负责 `templates/index.html` 与 `static/js`、`static/css` 的美化）。
- 康照虎 23012610：测试与性能评估（负责设置 `n_playout` 测试计划并记录响应时间）。
- 向红宇 23040099：实验报告与文档整理（负责最终 `experiment_report.md` 的校对与提交）。

（若需要调整，请组长在 `group.txt` 中更新并提交修改到仓库。）

## 九、结果、讨论与建议

- 结果：部署后可通过 `https://so-easy-alphazero-gomoku.hf.space` 访问并进行人机对弈。使用 PyTorch 推理版本能显著降低单步响应时间。
- 局限：未经训练，模型效果依赖于外部提供的预训练文件；训练成本高，不在本次实验范围。
- 建议：
  - 若长期对外提供服务，建议把 `n_playout` 配置为可变参数并在部署时根据实例规格灵活调优；
  - 若需更高性能或多人并发，考虑部署在支持 GPU 的付费实例或使用带弹性伸缩的云服务；
  - 若要复现训练流程，可参考原仓库：https://github.com/junxiaosong/AlphaZero_Gomoku 并在自有 GPU 环境中运行训练脚本。

## 十、参考与致谢

- 代码与模型参考：Junxiao Song 的开源仓库：https://github.com/junxiaosong/AlphaZero_Gomoku
- Hugging Face Spaces 文档：https://huggingface.co/docs

---

如需我把此报告提交并 `git push` 到你指定的 GitHub 仓库，请告知。你也可以在本地或 Hugging Face 的 Files 页面中直接下载或编辑此 `experiment_report.md` 文件.
