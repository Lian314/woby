# 卧笔 · App Store 上架指引（可选）

> TestFlight 是测试渠道：10,000 人上限、90 天过期、搜不到。
> 如果你希望任何人随时能在 App Store 搜索并下载，就需要走这一步。
>
> **免费 App 不需要为下载量向苹果付费**，但需要有效的 Apple Developer Program 账号，并通过 App Review。

---

## 1. TestFlight 和 App Store 的区别

| | TestFlight | App Store |
|---|---|---|
| 谁能装 | 拿到链接/邀请的人 | 所有人（按上架地区） |
| 人数上限 | 外部 10,000 | 无 |
| 有效期 | 每个构建 90 天 | 长期，除非下架 |
| 能否搜索 | 不能 | 能 |
| 审核 | Beta App Review（外部） | App Review（更严格） |
| 费用 | 含在开发者年费里 | 免费 App 无额外上架费 |

---

## 2. 上架前准备

- [ ] TestFlight 上跑了至少几天，没有崩溃和明显 bug
- [ ] App 图标：1024×1024、RGB、无透明通道（本项目已满足）
- [ ] 截图：至少一套 6.9 英寸 iPhone 截图（建议 3–5 张，1320×2868 或按 App Store Connect 当前要求）
- [ ] 隐私政策 URL（可公开访问；模板见 [04-隐私政策模板.md](04-隐私政策模板.md)）
- [ ] 支持 URL（可以是 GitHub 仓库、Notion 页面或简单官网）
- [ ] 支持邮箱
- [ ] App 描述、关键词、副标题
- [ ] 年龄分级问卷
- [ ] App 隐私问卷
- [ ] 中国大陆区：App 备案（ICP备案）等合规事项，见第 7 节

---

## 3. 在 App Store Connect 填写 App 信息

打开 App Store Connect → 你的 App → **App Store** 标签页。

### 3.1 App Information

- **Name**：`卧笔`（如果被占用，改成 `卧笔 - 极简 AI 对话`；这个名字会显示在 App Store）
- **Subtitle**：`极简 AI 对话，自带 Key`（30 字符以内）
- **Primary Category**：效率
- **Secondary Category**：工具（可选）
- **Content Rights**：不包含第三方版权内容（按实际情况）
- **Age Rating**：按问卷如实填写

### 3.2 Pricing and Availability

- **Price**：Free
- **Availability**：选择要上架的国家/地区。中国大陆区需要额外备案，确认后再勾选。

### 3.3 App Privacy

卧笔没有开发者服务器、没有统计 SDK、没有广告，也不把数据回传给我们。按实际情况通常可以选：

> **Data Not Collected（不收集数据）**

但要在隐私政策里说清楚：用户的消息、图片和 API Key 会直接发送到**用户自己配置的第三方模型服务**，不由卧笔开发者接收。若苹果审核认为这属于“收集”，按审核要求调整问卷，保持与隐私政策一致。

### 3.4 Version Information

需要填：

- **Screenshots**：6.9 英寸 iPhone 一套（可先在模拟器里截图）
- **Promotional Text**（可选，170 字符以内）
- **Description**
- **Keywords**（100 字符以内，用英文逗号分隔）
- **Support URL**
- **Privacy Policy URL**
- **Copyright**：例如 `2026 你的名字`

#### 可直接改用的文案

**副标题**

```text
极简 AI 对话，自带 Key
```

**宣传文本**

```text
不注册、不订阅。填上你自己的 OpenAI 兼容接口，就能文字聊天、发图片提问。
```

**描述**

```text
卧笔是一个极简的 AI 对话工具。

它不要求你注册账号，也不提供订阅。你只需要在设置里填入自己的 OpenAI 兼容接口（Base URL、API Key、模型名），就可以开始聊天。

主要功能：
• 文字对话，支持流式输出，逐字显示
• 从相册选择图片，让模型看图回答
• 支持智谱、阿里云百炼、OpenAI、Kimi、硅基流动、OpenRouter 等兼容接口预设
• 可自定义系统提示词、模型名和接口地址
• 聊天记录只保存在本机，可随时开启新对话
• 支持深色模式，回答可长按复制

卧笔本身不运营 AI 服务，不收集你的数据。模型调用由你选择的服务商提供，费用也由你的 API Key 直接结算。

适合已经拥有 API Key、想要一个干净、无广告、无订阅的 AI 聊天客户端的用户。
```

**关键词**

```text
AI,聊天,对话,看图,视觉,极简,API,OpenAI,兼容,自带Key
```

**支持 URL / 隐私政策 URL**

可以先用 GitHub Pages 或 Notion 公开页面占位，例如：

```text
https://yourname.github.io/wobi/
https://yourname.github.io/wobi/privacy.html
```

（把 `yourname` 换成你的 GitHub 用户名。）

---

## 4. 提交审核

1. 在 **App Store** 标签页准备好版本信息。
2. **Build** 区域选择已经上传并通过处理的构建。
3. 回答 **Export Compliance**（本项目 `ITSAppUsesNonExemptEncryption=false`，通常选“不使用非豁免加密”）。
4. 点 **Add for Review** → **Submit to App Review**。
5. 审核通常 1–3 天，可能更久；状态在 App Store Connect 里看。
6. 通过后可以选自动发布或手动发布。

---

## 5. 常见被拒原因与处理

| 原因 | 处理 |
|---|---|
| 崩溃、白屏、无法完成核心流程 | 确保不填 Key 时也有清晰引导；本项目首次启动会自动打开设置页 |
| 测试账号/审核说明不完整 | 在 App Review Information 里说明：App 需要用户自己的 API Key，附一个可用的测试 Key 或录屏 |
| 隐私政策缺失或不一致 | 填可访问的 URL；说明数据只存在本机、请求直连用户配置的服务商 |
| 图标/截图不合规 | 图标无 alpha；截图不能含“测试版”“Beta”等字样 |
| 功能过于简单/重复 | 说明差异点：极简、自带 Key、无账号、无订阅；审核仍可能主观 |
| AI 内容合规问题 | 说明卧笔不提供模型服务，内容由用户自带 Key 的第三方模型生成；必要时加入内容提示 |
| 中国大陆区缺少备案 | 完成 App 备案后再勾选中国大陆区 |

> App Review 可能会要求你提供一个可用的 API Key 供审核测试。**不要提供你自己的长期主 Key**；可以临时创建一个低额度 Key，审核结束后删除。

---

## 6. 上架之后

- 版本更新同样走 Archive → Upload → 提交审核。
- 崩溃和用户反馈在 App Store Connect → **Ratings and Reviews** / **Crashes** 里看。
- TestFlight 可以继续用于下一版本的内部测试。

---

## 7. 中国大陆区的额外事项（重要）

如果要在**中国大陆区 App Store** 上架：

1. **App 备案（ICP备案）**：自 2023 年起，面向中国大陆分发的 App 需要完成备案，具体材料和流程以工信部及苹果最新要求为准。
2. **生成式 AI 相关合规**：如果 App 被认定为向公众提供生成式 AI 服务，可能涉及算法备案、安全评估等要求。卧笔本身不提供模型服务，而是让用户自带 Key 直连第三方；这能降低一部分责任，但不等于自动合规，正式公开运营前建议咨询专业人士。
3. **内容安全**：公开上架后，用户可能输入敏感内容；需要准备相应的用户协议、投诉渠道和内容处理机制。

TestFlight 阶段通常不涉及上架备案，但公开测试同样要遵守法律法规和苹果的测试政策。

---

## 8. 提交前检查清单

- [ ] Bundle ID 与 App Store Connect 一致
- [ ] 版本号/构建号正确
- [ ] 图标 1024、无 alpha
- [ ] 至少一套 iPhone 6.9" 截图
- [ ] 隐私政策 URL 可访问
- [ ] 支持 URL 可访问
- [ ] App 隐私问卷与隐私政策一致
- [ ] 审核联系人、测试 Key（如需要）已填写
- [ ] 中国大陆区备案/合规已确认
