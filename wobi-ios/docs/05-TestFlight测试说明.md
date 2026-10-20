# 卧笔 · TestFlight 测试说明

把下面的内容复制到 App Store Connect → TestFlight → 测试信息 / What to Test。

## Beta App Description（给所有测试员）

```text
卧笔是一个极简的 AI 对话 App：不注册、不订阅，填入你自己的 OpenAI 兼容接口（Base URL、API Key、模型名），就能文字聊天和发图片提问。

第一次打开会自动进入设置页。推荐先用智谱 glm-4v-flash（通常有免费额度，支持看图，具体以控制台为准）：

Base URL: https://open.bigmodel.cn/api/paas/v4
模型: glm-4v-flash
API Key: 在 open.bigmodel.cn 注册后创建

也可以选阿里云百炼、OpenAI、Kimi、硅基流动、OpenRouter 等预设。DeepSeek 目前只支持文字，不能看图。

注意：
1. 本 App 不提供模型服务，API 费用由你自己的 Key 结算。
2. 聊天记录和 Key 只存在本机，不会上传给开发者。
3. 需要 iOS 17 或更新版本。
4. 这是测试版，功能会变；遇到问题请通过 TestFlight 的反馈功能告诉我。
```

## What to Test（每个构建）

```text
请重点测试：
1. 首次启动是否能顺利进入设置页，保存 Base URL / API Key / 模型。
2. 纯文字对话是否正常，流式输出是否逐字出现，停止按钮是否有效。
3. 从相册选择 1–3 张图片，提问“这张图里有什么”，模型是否能正确看图回答。
4. 切换服务商预设、关闭流式输出、关闭“图片以 Data URL 发送”后是否仍能工作。
5. 深色模式、长按复制回答、新对话清空记录是否正常。
6. 任何崩溃、卡住、报错，请附截图和所用服务商/模型名。
```

## 给测试员的安装步骤

```text
1. 在 App Store 搜索并安装 TestFlight（免费）。
2. 用 iPhone 的 Safari 打开我发你的 TestFlight 公开链接。
3. 点“接受” → “安装”。
4. 打开卧笔，按提示填自己的接口信息。
5. 有问题直接在 TestFlight 里截图反馈。
```

## 已知限制（可以主动告知测试员）

- 只支持 HTTPS 接口；
- API Key 存在本机，未加密，建议用低额度 Key；
- 目前是单会话，点“新对话”会清空当前记录；
- 图片会随历史一起重发，多轮带图对话会消耗更多 token；
- 仅 iPhone 布局，iPad 兼容运行；
- 需要 iOS 17+。
