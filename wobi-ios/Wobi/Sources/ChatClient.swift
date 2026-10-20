import Foundation

struct APIError: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

/// 只做一件事：把 OpenAI Chat Completions 兼容接口返回的内容变成一段段文字。
struct ChatClient: Sendable {
    let baseURL: String
    let apiKey: String
    let model: String
    let streaming: Bool
    let imageDataURL: Bool

    func makeStream(systemPrompt: String, messages: [ChatMessage]) throws -> AsyncThrowingStream<String, Error> {
        guard let url = endpointURL else {
            throw APIError(message: "接口地址无效：请在设置里填写 https:// 开头的 Base URL。")
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 180
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.httpBody = try requestBody(systemPrompt: systemPrompt, messages: messages)

        return Self.perform(request: request, streaming: streaming)
    }

    // MARK: - URL

    private var endpointURL: URL? {
        var text = baseURL.trimmed
        while text.hasSuffix("/") {
            text.removeLast()
        }
        guard !text.isEmpty else { return nil }

        let full: String
        if text.lowercased().hasSuffix("/chat/completions") {
            full = text
        } else {
            full = text + "/chat/completions"
        }

        guard let url = URL(string: full),
              url.scheme?.lowercased() == "https",
              url.host != nil else {
            return nil
        }
        return url
    }

    // MARK: - 请求体

    private func requestBody(systemPrompt: String, messages: [ChatMessage]) throws -> Data {
        var payload: [[String: Any]] = []

        let system = systemPrompt.trimmed
        if !system.isEmpty {
            payload.append(["role": "system", "content": system])
        }

        for message in messages where !message.isError {
            switch message.role {
            case .user:
                if message.images.isEmpty {
                    payload.append(["role": "user", "content": message.text])
                } else {
                    var parts: [[String: Any]] = [
                        ["type": "text", "text": message.text.isEmpty ? "看看这张图片。" : message.text]
                    ]
                    for image in message.images {
                        let value = imageDataURL ? image.dataURL : image.rawBase64
                        parts.append(["type": "image_url", "image_url": ["url": value]])
                    }
                    payload.append(["role": "user", "content": parts])
                }
            case .assistant:
                if !message.text.isEmpty {
                    payload.append(["role": "assistant", "content": message.text])
                }
            }
        }

        let body: [String: Any] = [
            "model": model,
            "messages": payload,
            "stream": streaming
        ]

        do {
            return try JSONSerialization.data(withJSONObject: body)
        } catch {
            throw APIError(message: "请求内容编码失败：\(error.localizedDescription)")
        }
    }

    // MARK: - 网络

    private static func perform(request: URLRequest, streaming: Bool) -> AsyncThrowingStream<String, Error> {
        AsyncThrowingStream { continuation in
            let task = Task {
                do {
                    if streaming {
                        try await streamRequest(request, into: continuation)
                    } else {
                        try await plainRequest(request, into: continuation)
                    }
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
            continuation.onTermination = { _ in
                task.cancel()
            }
        }
    }

    private static func streamRequest(
        _ request: URLRequest,
        into continuation: AsyncThrowingStream<String, Error>.Continuation
    ) async throws {
        let (bytes, response) = try await URLSession.shared.bytes(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError(message: "网络异常：没有收到服务器响应。")
        }
        guard (200..<300).contains(http.statusCode) else {
            var errorBody = Data()
            for try await byte in bytes {
                errorBody.append(byte)
            }
            throw APIError(message: errorMessage(status: http.statusCode, data: errorBody))
        }

        var sawEvent = false
        var plainBody = ""

        for try await line in bytes.lines {
            if line.hasPrefix("data:") {
                sawEvent = true
                let payload = String(line.dropFirst(5)).trimmed
                if payload.isEmpty { continue }
                if payload == "[DONE]" { break }
                if let delta = deltaText(from: Data(payload.utf8)), !delta.isEmpty {
                    continuation.yield(delta)
                }
            } else if line.hasPrefix(":") {
                continue
            } else {
                plainBody += line
            }
        }

        // 有的“兼容”服务商不认 stream=true，会直接返回普通 JSON。
        if !sawEvent, !plainBody.trimmed.isEmpty {
            continuation.yield(try fullText(from: Data(plainBody.utf8)))
        }
    }

    private static func plainRequest(
        _ request: URLRequest,
        into continuation: AsyncThrowingStream<String, Error>.Continuation
    ) async throws {
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError(message: "网络异常：没有收到服务器响应。")
        }
        guard (200..<300).contains(http.statusCode) else {
            throw APIError(message: errorMessage(status: http.statusCode, data: data))
        }
        continuation.yield(try fullText(from: data))
    }

    // MARK: - 解析

    private static func deltaText(from data: Data) -> String? {
        guard
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let choices = object["choices"] as? [[String: Any]],
            let first = choices.first,
            let delta = first["delta"] as? [String: Any]
        else { return nil }
        return delta["content"] as? String
    }

    private static func fullText(from data: Data) throws -> String {
        guard
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let choices = object["choices"] as? [[String: Any]],
            let first = choices.first
        else {
            throw APIError(message: "返回格式无法解析：需要 OpenAI 兼容的 /chat/completions 接口。")
        }
        if let message = first["message"] as? [String: Any],
           let content = message["content"] as? String {
            return content
        }
        if let text = first["text"] as? String {
            return text
        }
        throw APIError(message: "服务商没有返回文本内容。")
    }

    private static func errorMessage(status: Int, data: Data) -> String {
        var text = "请求失败（HTTP \(status)）"
        if let detail = errorText(from: data)?.trimmed, !detail.isEmpty {
            text += "\n\(detail)"
        }
        return text
    }

    private static func errorText(from data: Data) -> String? {
        if let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
            if let error = object["error"] as? [String: Any],
               let message = error["message"] as? String {
                return message
            }
            if let message = object["message"] as? String {
                return message
            }
            if let message = object["msg"] as? String {
                return message
            }
            if let error = object["error"] as? String {
                return error
            }
        }
        return String(data: data, encoding: .utf8)
    }
}
