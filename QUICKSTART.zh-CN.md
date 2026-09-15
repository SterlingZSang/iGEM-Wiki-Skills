# iGEM Wiki Skills 中文快速入门

这套 skill 用来帮助 iGEM 队伍理解、规划、编写、实现和审核 Wiki。你不需要先学会六个 skill 的分工：不确定时直接使用 `$igem-wiki`，它会根据任务选择相应模块。

## 1 分钟安装

先取得仓库：

```bash
git clone https://github.com/SterlingZSang/iGEM-Wiki-Skills.git
cd iGEM-Wiki-Skills
```

先预览项目内安装，不会修改文件：

```bash
python3 scripts/install_skills.py /path/to/wiki/.agents/skills
```

确认目标目录和差异无误后执行：

```bash
python3 scripts/install_skills.py /path/to/wiki/.agents/skills --apply
```

只需要 Model 模块时：

```bash
python3 scripts/install_skills.py /path/to/wiki/.agents/skills \
  --skill igem-model-wiki --apply
```

安装协调器 `igem-wiki` 时应安装全部六个模块；单独使用某个领域 skill 时不要求安装其他模块。更新已有目录时，安装器会先创建备份，并且不会触碰未选择的 skill 或其他项目文件。

## 检查安装

以下命令只读，不会自动修复或覆盖文件：

```bash
python3 igem-wiki/scripts/doctor.py /path/to/wiki/.agents/skills \
  --source . --project-root /path/to/wiki
```

它会检查安装完整性、版本、与当前源码的差异、越界链接、符号链接、checkpoint，以及本赛季规则快照是否需要重新核实。赛季过期只是提醒，不会把健康安装判为失败。

## 第一次怎么提问

最简单的方式是直接说目标：

```text
使用 $igem-wiki 检查我们目前最应该先完善哪个页面，只给方案，不修改文件。
```

如果任务已经明确，可以直接使用领域 skill：

```text
使用 $igem-model-wiki 审核 drylab-model.html，重点检查图表是否支持构建体选择；不要修改文件。
```

```text
使用 $igem-wetlab-wiki 把这个失败实验整理成一个 DBTL cycle，并保留失败原因和下一轮设计。
```

```text
使用 $igem-hp-wiki 检查这些访谈是否真的改变了项目，不要把接触人数当作 Integrated Human Practices。
```

完整请求通常包含以下四项；已经能从项目中读取的内容不需要重复说明：

- **目标：**理解、调研、规划、编写、实现或审核。
- **对象：**Wiki 根目录、具体页面、模型、实验或记录。
- **范围：**只读还是允许修改，以及不能改变的页面或视觉元素。
- **证据：**代码、数据、图、实验记录、访谈记录和已知限制。

## 理解材料和编写 Wiki 是两种任务

如果你暂时只想学习项目内容，请明确说“帮我理解，不要改 Wiki”：

```text
使用 $igem-model-wiki，用中文向刚加入队伍的成员解释 Model 3；不要重写 Wiki。
```

skill 会区分原始证据、计算结果、推论与计划，不会自动把教学解释变成英文发布文稿。准备发布时，再单独要求生成或修改 Wiki 内容。

## 计算量不确定时

```text
使用 $igem-model-wiki，先用小规模 smoke test 估算运行时间、内存和存储，再判断本地还是 HPC；估算前不要启动完整参数扫描。
```

完成计算不等于完成生物学验证。模型输出仍应说明输入、单位、参数来源、随机种子、运行环境、敏感性和实验边界。

## 中断后继续

直接说“继续”即可。skill 会先检查当前对话、实时文件、仓库状态和生成物，避免重复已经完成的工作。

只有在你授权持久化 checkpoint 时，才会写入 checkpoint。未指定路径时默认使用：

```text
<project-root>/.igem-wiki/checkpoint.md
```

checkpoint 不应保存密码、API key、可识别访谈原文或不必要的私人数据。

## 更新 skill

在仓库中取得新版后，先预览，再应用：

```bash
git pull
python3 scripts/install_skills.py /path/to/wiki/.agents/skills
python3 scripts/install_skills.py /path/to/wiki/.agents/skills --apply
```

安装器会报告哪些模块将被安装、更新或保持不变。正式发布版本以 GitHub Release、根目录 `VERSION` 和各 skill 的 `manifest.json` 一致为准。
