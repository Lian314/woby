import Foundation

// MARK: - 对话数据

enum ChatRole: String, Codable, Sendable {
    case user
    case assistant
}

struct Attachment: Codable, Identifiable, Equatable, Sendable {
    var id: UUID = UUID()
    var jpegData: Data

    /// data:image/jpeg;base64,...（OpenAI / DashScope / OpenRouter 等使用这种格式）
    var dataURL: String {
        "data:image/jpeg;base64,\(jpegData.base64EncodedString())"
    }

    /// 纯 base64，不含 data: 前缀（个别服务商使用）
    var rawBase64: String {
        jpegData.base64EncodedString()
    }
}

struct ChatMessage: Codable, Identifiable, Equatable, Sendable {
    var id: UUID = UUID()
    var role: ChatRole
    var text: String
    var images: [Attachment] = []
    var createdAt: Date = Date()
    var isError: Bool = false
}

// MARK: - 预设服务商

struct ProviderPreset: Identifiable, Hashable {
    var id: String { name }
    var name: String
    var baseURL: String
    var model: String
    var hint: String

    static let all: [ProviderPreset] = [
        ProviderPreset(
            name: "智谱 GLM（有免费模型）",
            baseURL: "https://open.bigmodel.cn/api/paas/v4",
            model: "glm-4v-flash",
            hint: "在 open.bigmodel.cn 注册并创建 API Key。glm-4v-flash 通常有免费额度/免费策略，具体以控制台为准。"
        ),
        ProviderPreset(
            name: "阿里云百炼",
            baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
            model: "qwen-vl-plus",
            hint: "在 bailian.console.aliyun.com 开通并创建 API Key，新用户通常有免费额度。"
        ),
        ProviderPreset(
            name: "OpenAI",
            baseURL: "https://api.openai.com/v1",
            model: "gpt-4o-mini",
            hint: "在 platform.openai.com 创建 Key。需要能访问 OpenAI 的网络环境。"
        ),
        ProviderPreset(
            name: "月之暗面 Kimi",
            baseURL: "https://api.moonshot.cn/v1",
            model: "moonshot-v1-8k-vision-preview",
            hint: "在 platform.moonshot.cn 创建 Key，视觉模型按量计费。"
        ),
        ProviderPreset(
            name: "硅基流动 SiliconFlow",
            baseURL: "https://api.siliconflow.cn/v1",
            model: "Qwen/Qwen2.5-VL-72B-Instruct",
            hint: "在 cloud.siliconflow.cn 创建 Key，可选多种开源视觉模型。"
        ),
        ProviderPreset(
            name: "OpenRouter",
            baseURL: "https://openrouter.ai/api/v1",
            model: "openai/gpt-4o-mini",
            hint: "在 openrouter.ai 创建 Key，一个 Key 可切换很多家模型。"
        ),
        ProviderPreset(
            name: "DeepSeek（仅文字）",
            baseURL: "https://api.deepseek.com/v1",
            model: "deepseek-chat",
            hint: "DeepSeek 目前不支持图片输入，只能文字对话。看图的场景请换上面的视觉模型。"
        )
    ]
}

extension String {
    var trimmed: String {
        trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
