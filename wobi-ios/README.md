# 卧笔 Wobi

一个极简的 iOS AI 对话 App：**没有账号、没有订阅、没有服务端**，填上你自己的 OpenAI 兼容接口，就能文字聊天、发图片问问题。

<p align="center">
  <img src="tools/icon-preview.png" width="180" alt="卧笔 App 图标">
</p>

## 已实现

- 单页对话，流式输出（逐字出现），可随时停止
- 从相册选图（最多 3 张），自动压缩到最长边 1400px 的 JPEG 再发送
- 任意兼容 OpenAI `POST /chat/completions` 的接口：Base URL、API Key、模型名全部自己填
- 7 个常用服务商预设：智谱 GLM、阿里云百炼、OpenAI、Kimi、硅基流动、OpenRouter、DeepSeek
- 可改系统提示词；可开关流式输出；可切换图片以 Data URL / 纯 Base64 发送
- 设置和聊天记录只存本机；深色模式；回答可长按复制
- 首次启动自动弹出设置页引导配置
- 自带 App 图标、隐私清单，工程可直接用 Xcode 打开

刻意没做：多会话列表、语音、Markdown 代码高亮、账号体系。保持简单。

## 在 Mac 上跑起来（约 5 分钟）

需要：macOS 14+、Xcode 15.4+（推荐 Xcode 16）、一台 iPhone（iOS 17+）或模拟器。

1. 双击打开 `Wobi.xcodeproj`。
2. 左侧选中 **Wobi** target → **Signing & Capabilities**：
   - **Team** 选择你的 Apple ID（免费 Apple ID 也可以先跑真机）；
   - **Bundle Identifier** 改成你自己的，例如 `com.你的名字.wobi`。
3. 顶部运行目标选一台 iPhone（或模拟器），按 **⌘R**。
4. 首次启动会自动弹出设置，填：
   - **Base URL**：例如 `https://open.bigmodel.cn/api/paas/v4`
   - **API Key**：在对应服务商控制台申请
   - **模型**：例如 `glm-4v-flash`
   - 点「保存」，然后发一句「你好」测试。

> 想在模拟器里用相机/相册：直接拖图片进模拟器，再在 App 里点相册按钮即可。
>
> **自己真机试用不需要 99 美元**：免费 Apple ID 的 Personal Team 就能装到自己的 iPhone，只是描述文件 7 天过期，重新按一次 ⌘R 就能续上。要走 TestFlight 给别人测试，才需要付费的 Apple Developer Program。

## 推荐的服务商

| 服务商 | Base URL | 模型示例 | 看图 | 说明 |
|---|---|---|---|---|
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4v-flash` | ✅ | 有免费/低价视觉模型，国内较容易上手 |
| 阿里云百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-vl-plus` | ✅ | 新用户通常有免费额度 |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | ✅ | 需要可访问 OpenAI 的网络 |
| 月之暗面 Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k-vision-preview` | ✅ | 按量计费 |
| 硅基流动 | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-VL-72B-Instruct` | ✅ | 可选多种开源视觉模型 |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` | ✅ | 一个 Key 切换多家模型 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | ❌ | 目前只支持文字 |

App 里直接选预设即可自动填 Base URL 和模型，只需再填 API Key。

## 发布到 TestFlight

一句话回答你最关心的问题：

- **TestFlight 对测试员免费**，拿到公开链接的人都能免费装；
- 但**开发者需要 Apple Developer Program，99 美元/年**（中国区约 ¥688/年，以苹果结算页为准）；
- 外部测试**最多 10,000 人**，每个构建**只有 90 天有效期**，且第一个外部构建要过 **Beta 审核**；
- 它**不是** App Store：别人搜不到，只能通过链接加入，90 天后会过期。

完整步骤（注册、建 App、签名、Archive、上传、公开链接、测试员安装、常见报错）：

→ **[docs/01-TestFlight发布指南.md](docs/01-TestFlight发布指南.md)**

以后想真正让所有人搜得到、随时下载，需要上架 App Store（免费 App 没有额外上架费，但要过 App Review，中国大陆还涉及 App 备案）：

→ **[docs/02-AppStore上架.md](docs/02-AppStore上架.md)**

其他：

- [docs/03-常见问题.md](docs/03-常见问题.md)
- [docs/04-隐私政策模板.md](docs/04-隐私政策模板.md)
- [docs/05-TestFlight测试说明.md](docs/05-TestFlight测试说明.md)

## 目录结构

```
wobi-ios/
├─ Wobi.xcodeproj/            # Xcode 工程（含共享 scheme）
├─ Wobi/
│  ├─ Info.plist
│  ├─ PrivacyInfo.xcprivacy   # 隐私清单
│  ├─ Assets.xcassets/        # App 图标 + 主题色
│  └─ Sources/
│     ├─ WobiApp.swift
│     ├─ Models.swift
│     ├─ SettingsStore.swift  # 用户配置（UserDefaults）
│     ├─ ChatClient.swift     # OpenAI 兼容接口 + SSE 解析
│     ├─ ChatStore.swift      # 对话状态 + 本地持久化
│     ├─ ImageTool.swift      # 图片压缩
│     ├─ ChatView.swift       # 对话界面
│     └─ SettingsView.swift   # 设置界面
├─ docs/                      # 发布、FAQ、隐私政策
├─ tools/                     # 图标生成、工程生成、静态校验（可选）
└─ .github/workflows/         # GitHub Actions 编译检查
```

## 已知限制（有意为之）

- **只支持 HTTPS**：iOS 的 ATS 默认禁止明文 HTTP。若你要连自建的 `http://` 网关，需要在 `Info.plist` 里加 ATS 例外，并自行评估风险。
- **API Key 存在 UserDefaults**，未加密。只适合自己的设备；不要把装了 Key 的手机借人。
- **iOS 17+**：用到了新版 SwiftUI API。
- **iPhone only**：iPad 以兼容模式运行。
- **图片会随历史一起重发**：多轮带图对话会消耗更多 token；聊久了建议开新对话。
- 没有 Mac 就无法编译/上传（Xcode 只有 macOS 版）。可以租云 Mac，或把代码推到 GitHub 用 CI 编译；见发布指南。

## 验证状态

开发环境是 Windows，**没有 Xcode，所以还没有真正编译过**。已经做的检查：

- `python tools/validate_project.py`：pbxproj 语法、对象引用、文件引用、plist、资源目录、scheme、Swift 括号平衡全部通过；
- 人工核对了 SwiftUI/iOS 17 API 与 Info.plist 配置；
- App 图标为 1024×1024、RGB、无透明通道（App Store 硬性要求）。

第一次在 Mac 上打开如果报错，把 Xcode 的红色报错贴给开发者，通常几分钟能修好。仓库里的 `.github/workflows/build.yml` 也可以直接在 GitHub 上跑一次编译检查。

## 隐私

卧笔不运营服务器，不收集、不上传任何数据给开发者。你填的接口地址和 Key、聊天记录都只存在本机；发消息时内容直接发送给你配置的第三方服务商，受该服务商隐私政策约束。详见 [隐私政策模板](docs/04-隐私政策模板.md)。
