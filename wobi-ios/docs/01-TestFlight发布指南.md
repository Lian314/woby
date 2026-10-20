# 卧笔 · TestFlight 发布指南

> 目标：把现在这份代码变成一条 TestFlight 公开链接，让任何人点开就能免费安装测试。
>
> 前提：**一台 Mac（或云 Mac）+ Apple Developer Program 付费账号**。Windows 不能编译 iOS App，也没有官方上传 TestFlight 的工具。

官方说明：

- <https://developer.apple.com/testflight/>
- <https://developer.apple.com/programs/>（$99/年，含 TestFlight 和 App Store 分发）

---

## 0. 先看结论

| 问题 | 答案 |
|---|---|
| 自己 iPhone 真机试用要钱吗？ | **不要**。免费 Apple ID + Xcode 就能装，7 天过期，重新 Run 即可 |
| 发布到 TestFlight 要钱吗？ | 开发者需要 **Apple Developer Program，99 美元/年**；TestFlight 功能本身不再单独收费 |
| 测试员下载要钱吗？ | **不要**。免费安装，App 内也没有内购 |
| 用户可以“随便下载”吗？ | **不是搜索下载**。公开链接谁拿到谁都能加入，但最多 **10,000 名外部测试员**，且 App Store 里搜不到 |
| 链接永久有效吗？ | **不**。每个构建从上传起 **90 天**有效，过期要传新构建 |
| 要审核吗？ | **外部测试**的第一个构建要过 Beta App Review；**内部测试**不需要 |
| 能上架 App Store 吗？ | 可以，另走 App Review。免费 App 没有额外上架费 |

一句话：**TestFlight 适合“发链接给一批人免费试用”，不是正式发行渠道。**

---

## 1. 需要准备什么

1. **Apple ID**：开启双重认证。
2. **Apple Developer Program**：个人 99 美元/年；公司需要 D-U-N-S 编号。
3. **Mac**：macOS 14 或更新，安装 Xcode 15.4+（推荐 Xcode 16）。
4. **iPhone（可选）**：iOS 17+，用来真机试跑。
5. **App Store Connect** 能登录（付费账号开通后自动有权限）。

> 免费 Apple ID 也能在 Xcode 里把 App 装到自己手机上（7 天过期），但**不能上传 TestFlight**。
>
> 如果你只是想自己先试用，**不要急着买会员**：用免费 Apple ID 的 Personal Team 就够。等确定要继续发给别人测试，再注册付费账号。

---

## 2. 注册 Apple Developer Program

1. 打开 <https://developer.apple.com/programs/>，点 **Enroll**。
2. 用 Apple ID 登录，选择 **Individual（个人）** 或 **Organization（公司）**：
   - 个人：填真实姓名、地址，按提示做身份验证；
   - 公司：需要 D-U-N-S 编号，且账号持有人要有授权。
3. 支付 99 美元/年（中国区以苹果结算页为准，通常约 ¥688/年）。
4. 等待审核，常见 1–2 个工作日，偶尔更久。通过后会收到邮件。
5. 打开 <https://appstoreconnect.apple.com>，确认能看到 **Apps**。

> 续费每年一次。到期不续，TestFlight 构建和 App Store 上的 App 都会受影响。

---

## 3. 创建 Bundle ID 和 App 记录

### 3.1 注册 Bundle ID

1. 打开 <https://developer.apple.com/account> → **Certificates, Identifiers & Profiles** → **Identifiers**。
2. 点 **+** → 选 **App IDs** → **App** → Continue。
3. 填写：
   - **Description**：`Wobi`
   - **Bundle ID**：选 **Explicit**，填一个你自己的反向域名，例如 `com.yourname.wobi`
   - **Capabilities**：一个都不用勾。
4. Continue → Register。

> Bundle ID 全球唯一。如果提示已被占用，换一个，例如 `com.yourname.wobiapp`。
> 这个值必须和 Xcode 里 **Signing & Capabilities → Bundle Identifier** 完全一致。

### 3.2 创建 App 记录

1. 打开 <https://appstoreconnect.apple.com> → **Apps** → 左上角 **+** → **New App**。
2. 填写：
   - **Platforms**：iOS
   - **Name**：`卧笔`（App Store 全局唯一；如果被占用，用 `卧笔 - 极简 AI 对话` 这类名字）
   - **Primary Language**：简体中文
   - **Bundle ID**：选刚注册的那个
   - **SKU**：`wobi-001`（内部编号，随便填，创建后不能改）
   - **User Access**：Full Access
3. 创建后先不用填 App Store 页面，TestFlight 用不到那么多信息。

---

## 4. 在 Xcode 里签名并上传

### 4.1 打开工程

```text
wobi-ios/Wobi.xcodeproj
```

### 4.2 设置签名

1. 左侧点项目名 **Wobi** → TARGETS 里的 **Wobi** → **Signing & Capabilities**。
2. 勾选 **Automatically manage signing**。
3. **Team** 选你的开发者团队。
4. **Bundle Identifier** 改成 3.1 注册的那个。
5. 如果 Team 下拉框是空的：Xcode → **Settings…** → **Accounts** → 用 Apple ID 登录。

### 4.3 Archive

1. 顶部运行目标从模拟器改成 **Any iOS Device (arm64)**。
2. 菜单 **Product → Archive**。
3. 编译完成后会自动弹出 **Organizer**。
4. 选中刚生成的 Archive → 右侧 **Distribute App** → **App Store Connect** → **Upload**。
5. 一路 Next：
   - 签名选 **Automatically manage signing**
   - 不要选 Export，选 **Upload**
6. 看到 **Upload Success** 后，去 App Store Connect 等处理。

> 第一次上传通常 5–60 分钟处理完成；状态会从 “Processing” 变成可用。
>
> **构建号必须递增**：每次上传前把 target 的 **Build**（`CURRENT_PROJECT_VERSION`）从 1 改成 2、3……否则会报 “build number already used”。
>
> 版本号（`MARKETING_VERSION`）现在是 `1.0`，可以保持不变。

### 4.4 加密合规

`Info.plist` 里已经设置：

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

所以上传时不会再问“是否使用加密”。如果还是被问，选 **No / 只使用豁免加密**。

---

## 5. 在 App Store Connect 配置 TestFlight

打开 App Store Connect → 你的 App → **TestFlight**。

### 5.1 填写测试信息

- **Beta App Description**：给测试员看的简介，例如：
  > 卧笔是一个极简 AI 对话工具。进入后先在右上角设置里填入你自己的 OpenAI 兼容接口（Base URL、API Key、模型），然后就可以文字聊天、发图片提问。App 本身不需要注册，也不收集你的数据。
- **Feedback Email**：你的邮箱。
- **Contact Information**：真实姓名、电话、邮箱（审核用）。
- 每个构建的 **What to Test**：可以直接用 [05-TestFlight测试说明.md](05-TestFlight测试说明.md) 里的文案。

### 5.2 内部测试（最快，不用审核）

1. **Internal Testing** → **+** 新建组，例如 `Team`。
2. 添加测试员：必须是 App Store Connect → **Users and Access** 里的成员（最多 100 人）。
3. 把构建加到组里，勾选自动分发。
4. 测试员会收到 TestFlight 邀请邮件。

> 内部测试不需要 Beta App Review，适合先给自己和同事验证。

### 5.3 外部测试 + 公开链接（你要的“随便下载”）

1. **External Testing** → **+** 新建组，例如 `Public`。
2. 添加构建 → 填写 **What to Test** → **Submit for Beta App Review**。
3. 审核通过后，在组里打开 **Public Link**，复制链接，形如：
   ```text
   https://testflight.apple.com/join/AbCdEfGh
   ```
4. 把链接发给任何人，最多 10,000 名外部测试员。
5. 人满了可以关闭链接；也可以设置设备/系统版本条件。

### 5.4 测试员怎么装

1. 在 App Store 搜索并下载 **TestFlight**（免费）。
2. 用 iPhone 的 Safari 打开公开链接。
3. 点 **Accept / 接受** → **Install / 安装**。
4. 回到桌面打开 **卧笔**，在设置里填自己的接口信息。

> 测试员需要 Apple ID，但不需要付任何费用；本 App 需要 iOS 17+。

---

## 6. 90 天规则与更新版本

- 每个构建从上传起 **90 天**有效。过期后测试员打开会提示 “This beta has expired”，需要装新构建。
- 更新流程：改代码 → 把 **Build** 加 1 → 重新 Archive / Upload → 在 TestFlight 里把新构建加到外部组 → 提交 Beta 审核（通常比首次快）→ 审核通过后自动分发给测试员。
- 公开链接本身不变，除非你关闭或重建。

---

## 7. 费用清单

| 项目 | 费用 |
|---|---|
| Apple Developer Program | **99 美元/年**（约 ¥688，以苹果结算为准） |
| TestFlight 测试员 | 免费 |
| App 本身 | 免费（无内购、无订阅） |
| AI 接口调用 | 由用户自己的 API Key 付费给服务商 |
| 借 Mac | 免费；租云 Mac 按小时/月计费 |
| 上架 App Store | 无按下载收费；中国区备案费用视情况 |

---

## 8. 没有 Mac 怎么办

Windows 无法运行 Xcode，也没有苹果官方的 Windows 上传工具。可选：

1. **借一台 Mac（最省事）**：装 Xcode、登录 Apple ID、Archive、Upload，熟悉的话 30–60 分钟。
2. **租云 Mac**：MacinCloud、MacStadium、AWS EC2 Mac 等，按小时或按月；远程桌面操作，流程完全一样。
3. **CI 构建**：GitHub Actions 的 macOS runner、Codemagic、Xcode Cloud 都能编译；但上传 TestFlight 要配置签名证书和 App Store Connect API Key，属于进阶玩法。
   - 仓库里 `.github/workflows/build.yml` 已提供**编译检查**（不签名、不上传），推到 GitHub 就能免费验证代码是否能编译。
4. **Xcode Cloud**：苹果自带 CI，需要开发者账号；第一次配置仍需在 Xcode 里点几下。

> 不要购买“代上传”服务，也不要把 Apple ID 密码/双重认证验证码交给别人。

---

## 9. 常见报错

| 报错 | 原因 | 处理 |
|---|---|---|
| `No signing certificate "iOS Distribution" found` | 没选 Team / 证书没生成 | 打开自动签名，确认 Team，联网后重试 |
| `Failed to register bundle identifier` | Bundle ID 被占用 | 换一个 Bundle ID，并同步改 Xcode 和 App Store Connect |
| `The provided entity includes an attribute with a value that has already been used` | App 名称已被占用 | 换 App 名，例如加副标题 |
| `Invalid Bundle. ... does not contain a bundle executable` | Info.plist / target 配置被改坏 | 恢复 `Info.plist`，确认 target 是 Application |
| `Missing Compliance` | 加密合规没回答 | 确认 `ITSAppUsesNonExemptEncryption` 为 false；仍在 ASC 里回答一次 |
| `Invalid App Store Icon` | 图标有透明通道或尺寸不对 | 用 1024×1024、无 alpha 的 PNG（本项目已满足） |
| `Build number already used` | 构建号重复 | Xcode target → General → Build 加 1 |
| 上传后一直 Processing | 苹果后台排队 | 等 30–60 分钟；检查邮箱是否有苹果邮件 |
| Beta 审核被拒 | 测试说明不完整、崩溃、隐私问题 | 按 Resolution Center 的说明改，再重新提交 |
| 公开链接显示 “This beta is full” | 达到 10,000 人 | 关闭链接或清理测试员 |

---

## 10. 安全与合规

- **不要把开发者自己的 API Key 打进 App**。卧笔的设计是每个用户填自己的 Key，费用也由用户承担。
- API Key 目前存在本机 `UserDefaults`，未加密；不要共用设备。
- App 不收集数据，但用户的消息和图片会直接发给他自己配置的第三方模型服务，请让测试员知悉。
- 在中国大陆**上架 App Store** 还涉及 App 备案和生成式 AI 相关合规要求；TestFlight 测试阶段通常不涉及上架备案，但请以苹果和监管的最新要求为准。
- 不要公开分享含有个人 Key 的截图或日志。

---

## 11. 下一步

TestFlight 跑顺之后，如果想真正公开上架、让所有人随时下载：

→ [02-AppStore上架.md](02-AppStore上架.md)
