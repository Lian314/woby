import Foundation
import SwiftUI

@MainActor
final class ChatStore: ObservableObject {
    @Published private(set) var messages: [ChatMessage] = []
    @Published var draft: String = ""
    @Published var pendingImages: [Attachment] = []
    @Published private(set) var isSending = false
    @Published var banner: String?

    private var task: Task<Void, Never>?
    private var activeRequestID: UUID?
    private var activePlaceholderID: UUID?

    init() {
        load()
    }

    // MARK: - 发送

    func send(settings: SettingsStore) {
        guard !isSending else { return }

        let text = draft.trimmed
        guard !text.isEmpty || !pendingImages.isEmpty else { return }

        guard settings.isConfigured else {
            banner = "先点右上角的齿轮，填好接口地址、API Key 和模型名，再开始对话。"
            return
        }

        let userMessage = ChatMessage(role: .user, text: text, images: pendingImages)
        messages.append(userMessage)
        draft = ""
        pendingImages = []

        let placeholder = ChatMessage(role: .assistant, text: "")
        messages.append(placeholder)
        let placeholderID = placeholder.id
        let history = Array(messages.dropLast())
        let requestID = UUID()
        activeRequestID = requestID
        activePlaceholderID = placeholderID
        isSending = true
        save()

        let client = ChatClient(
            baseURL: settings.trimmedBaseURL,
            apiKey: settings.trimmedAPIKey,
            model: settings.trimmedModel,
            streaming: settings.streaming,
            imageDataURL: settings.imageDataURL
        )
        let systemPrompt = settings.systemPrompt

        task = Task { [weak self] in
            guard let self else { return }
            do {
                let stream = try client.makeStream(systemPrompt: systemPrompt, messages: history)
                for try await delta in stream {
                    if Task.isCancelled { break }
                    self.append(delta, to: placeholderID, requestID: requestID)
                }
                self.finish(placeholderID: placeholderID, requestID: requestID, cancelled: false)
            } catch is CancellationError {
                self.finish(placeholderID: placeholderID, requestID: requestID, cancelled: true)
            } catch let error as URLError where error.code == .cancelled {
                self.finish(placeholderID: placeholderID, requestID: requestID, cancelled: true)
            } catch {
                self.fail(placeholderID: placeholderID, requestID: requestID, error: error)
            }
        }
    }

    func stop() {
        guard isSending else { return }
        task?.cancel()
        task = nil
        activeRequestID = nil
        isSending = false

        if let placeholderID = activePlaceholderID,
           let index = messages.firstIndex(where: { $0.id == placeholderID }) {
            if messages[index].text.isEmpty {
                messages[index].text = "（已停止）"
                messages[index].isError = true
            } else {
                messages[index].text += "\n\n（已停止）"
            }
        }
        activePlaceholderID = nil
        save()
    }

    func newChat() {
        guard !isSending else { return }
        messages = []
        draft = ""
        pendingImages = []
        save()
    }

    // MARK: - 流式更新

    private func append(_ delta: String, to messageID: UUID, requestID: UUID) {
        guard activeRequestID == requestID else { return }
        guard let index = messages.firstIndex(where: { $0.id == messageID }) else { return }
        messages[index].text += delta
    }

    private func finish(placeholderID: UUID, requestID: UUID, cancelled: Bool) {
        guard activeRequestID == requestID else {
            save()
            return
        }
        activeRequestID = nil
        activePlaceholderID = nil
        isSending = false
        task = nil

        guard let index = messages.firstIndex(where: { $0.id == placeholderID }) else {
            save()
            return
        }
        if messages[index].text.isEmpty {
            messages[index].text = cancelled ? "（已停止）" : "（没有返回内容，检查一下模型和接口是否匹配）"
            messages[index].isError = true
        }
        save()
    }

    private func fail(placeholderID: UUID, requestID: UUID, error: Error) {
        guard activeRequestID == requestID else {
            save()
            return
        }
        activeRequestID = nil
        activePlaceholderID = nil
        isSending = false
        task = nil

        let detail = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        guard let index = messages.firstIndex(where: { $0.id == placeholderID }) else {
            save()
            return
        }
        if messages[index].text.isEmpty {
            messages[index].text = "⚠️ \(detail)"
        } else {
            messages[index].text += "\n\n⚠️ \(detail)"
        }
        messages[index].isError = true
        save()
    }

    // MARK: - 本地持久化

    private var saveURL: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        return base.appendingPathComponent("wobi-chat.json")
    }

    private func save() {
        let url = saveURL
        do {
            try FileManager.default.createDirectory(
                at: url.deletingLastPathComponent(),
                withIntermediateDirectories: true
            )
            let data = try JSONEncoder().encode(messages)
            try data.write(to: url, options: .atomic)
        } catch {
            // 本地缓存失败不影响对话本身。
        }
    }

    private func load() {
        let url = saveURL
        guard
            let data = try? Data(contentsOf: url),
            let saved = try? JSONDecoder().decode([ChatMessage].self, from: data)
        else { return }
        messages = saved.filter { !($0.role == .assistant && $0.text.isEmpty) }
    }
}
