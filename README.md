# 卧笔 Woby

<p align="center">
  <img src="wobi-ios/tools/icon-preview.png" width="160" alt="卧笔 App 图标">
</p>

卧笔是一个极简的 AI 对话应用：没有账号、没有订阅，接口和 API Key 由用户自己配置，支持文字对话和看图。

这个仓库包含两个版本：

| 版本 | 目录 | 技术栈 | 分发方式 |
|---|---|---|---|
| iOS 原生 | [`wobi-ios/`](wobi-ios/README.md) | SwiftUI · iOS 17+ | TestFlight / App Store |
| 微信小程序 | [`wobi-miniprogram/`](wobi-miniprogram/README.md) | WXML / WXSS / JavaScript | 微信开发者工具预览、体验版 |

## 快速开始

### iOS 原生版

需要一台 Mac 和 Xcode。打开 `wobi-ios/Wobi.xcodeproj`，在 Signing & Capabilities 里选择 Team、修改 Bundle Identifier，然后运行。

- [项目说明](wobi-ios/README.md)
- [TestFlight 发布指南](wobi-ios/docs/01-TestFlight发布指南.md)
- [App Store 上架指引](wobi-ios/docs/02-AppStore上架.md)
- [常见问题](wobi-ios/docs/03-常见问题.md)

### 微信小程序版

不需要 Mac，也不需要 Apple Developer 账号。用微信开发者工具导入 `wobi-miniprogram/`，填入自己的 AppID，配置请求域名后即可在手机微信里预览。

- [小程序说明](wobi-miniprogram/README.md)

## 功能

- 文字对话，流式输出
- 相册/相机选图，发给视觉模型
- 自定义 Base URL、模型、API Key、系统提示词
- 设置只保存在本机；没有开发者服务器
- 原生版支持任意 OpenAI 兼容 HTTPS 接口；小程序版受微信域名白名单限制

## 仓库说明

- 本仓库不包含 `原始项目交付文档/`（内部账号、服务器和凭证资料）。
- 不包含构建产物、`wobi-ios.zip` 和小程序本地私有配置（`project.private.config.json`）。
- 请勿把真实 API Key 提交到仓库；两个版本都设计成由用户自己填写 Key。
