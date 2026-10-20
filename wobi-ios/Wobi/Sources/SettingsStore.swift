import Foundation
import Combine

/// 用户自己配置的接口信息。全部只保存在本机 UserDefaults 里。
@MainActor
final class SettingsStore: ObservableObject {
    @Published var baseURL: String { didSet { defaults.set(baseURL, forKey: Key.baseURL.rawValue) } }
    @Published var apiKey: String { didSet { defaults.set(apiKey, forKey: Key.apiKey.rawValue) } }
    @Published var model: String { didSet { defaults.set(model, forKey: Key.model.rawValue) } }
    @Published var systemPrompt: String { didSet { defaults.set(systemPrompt, forKey: Key.systemPrompt.rawValue) } }
    @Published var streaming: Bool { didSet { defaults.set(streaming, forKey: Key.streaming.rawValue) } }
    @Published var imageDataURL: Bool { didSet { defaults.set(imageDataURL, forKey: Key.imageDataURL.rawValue) } }

    private let defaults: UserDefaults

    private enum Key: String {
        case baseURL
        case apiKey
        case model
        case systemPrompt
        case streaming
        case imageDataURL
    }

    static let defaultSystemPrompt = "你是「卧笔」，一个简洁、可靠的中文 AI 助手。回答尽量直接，少客套。遇到图片时，先说出画面里的关键信息，再回答用户的问题。"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        let preset = ProviderPreset.all[0]

        baseURL = defaults.string(forKey: Key.baseURL.rawValue) ?? preset.baseURL
        apiKey = defaults.string(forKey: Key.apiKey.rawValue) ?? ""
        model = defaults.string(forKey: Key.model.rawValue) ?? preset.model
        systemPrompt = defaults.string(forKey: Key.systemPrompt.rawValue) ?? SettingsStore.defaultSystemPrompt

        if defaults.object(forKey: Key.streaming.rawValue) == nil {
            streaming = true
        } else {
            streaming = defaults.bool(forKey: Key.streaming.rawValue)
        }

        if defaults.object(forKey: Key.imageDataURL.rawValue) == nil {
            imageDataURL = true
        } else {
            imageDataURL = defaults.bool(forKey: Key.imageDataURL.rawValue)
        }
    }

    // MARK: - 派生值

    var trimmedBaseURL: String { baseURL.trimmed }
    var trimmedAPIKey: String { apiKey.trimmed }
    var trimmedModel: String { model.trimmed }

    var isConfigured: Bool {
        guard !trimmedAPIKey.isEmpty, !trimmedModel.isEmpty else { return false }
        guard let url = URL(string: trimmedBaseURL),
              url.scheme?.lowercased() == "https",
              url.host != nil else { return false }
        return true
    }

    // MARK: - 操作

    func apply(_ preset: ProviderPreset) {
        baseURL = preset.baseURL
        model = preset.model
    }

    func resetEndpointToDefault() {
        apply(ProviderPreset.all[0])
    }
}
