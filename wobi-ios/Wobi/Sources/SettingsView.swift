import SwiftUI
import Foundation

struct SettingsView: View {
    @EnvironmentObject private var settings: SettingsStore
    @Environment(\.dismiss) private var dismiss

    @State private var baseURL = ""
    @State private var apiKey = ""
    @State private var model = ""
    @State private var systemPrompt = ""
    @State private var streaming = true
    @State private var imageDataURL = true
    @State private var presetID = ""
    @State private var revealKey = false
    @State private var errorMessage: String?
    @State private var didLoad = false

    private var matchedPreset: ProviderPreset? {
        ProviderPreset.all.first { $0.baseURL == baseURL.trimmed && $0.model == model.trimmed }
    }

    private var errorBinding: Binding<Bool> {
        Binding(
            get: { errorMessage != nil },
            set: { newValue in
                if !newValue { errorMessage = nil }
            }
        )
    }

    private var versionText: String {
        let info = Bundle.main.infoDictionary
        let version = info?["CFBundleShortVersionString"] as? String ?? "1.0"
        let build = info?["CFBundleVersion"] as? String ?? "1"
        return "\(version) (\(build))"
    }

    var body: some View {
        NavigationStack {
            Form {
                providerSection
                apiSection
                chatSection
                aboutSection
            }
            .navigationTitle("设置")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }
                        .fontWeight(.semibold)
                        .disabled(baseURL.trimmed.isEmpty || model.trimmed.isEmpty || apiKey.trimmed.isEmpty)
                }
            }
            .onAppear(perform: load)
            .alert("无法保存", isPresented: errorBinding) {
                Button("好", role: .cancel) {}
            } message: {
                Text(errorMessage ?? "")
            }
        }
    }

    // MARK: - 服务商

    private var providerSection: some View {
        Section {
            Picker("预设", selection: $presetID) {
                Text("自定义").tag("")
                ForEach(ProviderPreset.all) { preset in
                    Text(preset.name).tag(preset.id)
                }
            }
            .onChange(of: presetID) { _, newValue in
                guard let preset = ProviderPreset.all.first(where: { $0.id == newValue }) else { return }
                baseURL = preset.baseURL
                model = preset.model
            }

            if let matchedPreset {
                Text(matchedPreset.hint)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            } else {
                Text("选一个预设，或自己填任何兼容 OpenAI Chat Completions 的接口。")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        } header: {
            Text("服务商")
        }
    }

    // MARK: - 接口

    private var apiSection: some View {
        Section {
            TextField("Base URL，例如 https://api.openai.com/v1", text: $baseURL)
                .keyboardType(.URL)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()

            HStack {
                Group {
                    if revealKey {
                        TextField("API Key", text: $apiKey)
                    } else {
                        SecureField("API Key", text: $apiKey)
                    }
                }
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()

                Button {
                    revealKey.toggle()
                } label: {
                    Image(systemName: revealKey ? "eye.slash" : "eye")
                        .foregroundStyle(.secondary)
                }
                .buttonStyle(.plain)
            }

            TextField("模型名，例如 gpt-4o-mini", text: $model)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
        } header: {
            Text("接口")
        } footer: {
            Text("只支持 https:// 地址。Key 只保存在这台设备上；卧笔没有服务器，请求会直接发给你填的服务商。")
        }
    }

    // MARK: - 对话

    private var chatSection: some View {
        Section {
            TextEditor(text: $systemPrompt)
                .frame(minHeight: 92)

            Toggle("流式输出（逐字出现）", isOn: $streaming)
            Toggle("图片以 Data URL 发送", isOn: $imageDataURL)
        } header: {
            Text("对话")
        } footer: {
            Text("看图需要视觉模型，例如 gpt-4o-mini、qwen-vl-plus、glm-4v-flash。若某个服务商不认图片，先把“Data URL”开关关掉再试。")
        }
    }

    // MARK: - 关于

    private var aboutSection: some View {
        Section {
            Button("恢复默认接口") {
                let preset = ProviderPreset.all[0]
                presetID = preset.id
                baseURL = preset.baseURL
                model = preset.model
            }

            HStack {
                Text("版本")
                Spacer()
                Text(versionText)
                    .foregroundStyle(.secondary)
            }
        } footer: {
            Text("卧笔 · 把模型选择权交还给你。TestFlight 测试版。")
        }
    }

    // MARK: - 读写

    private func load() {
        guard !didLoad else { return }
        didLoad = true

        baseURL = settings.baseURL
        apiKey = settings.apiKey
        model = settings.model
        systemPrompt = settings.systemPrompt
        streaming = settings.streaming
        imageDataURL = settings.imageDataURL
        presetID = ProviderPreset.all.first {
            $0.baseURL == settings.trimmedBaseURL && $0.model == settings.trimmedModel
        }?.id ?? ""
    }

    private func save() {
        let urlText = baseURL.trimmed
        guard let url = URL(string: urlText),
              url.scheme?.lowercased() == "https",
              url.host != nil else {
            errorMessage = "Base URL 必须是 https:// 开头的完整地址，例如 https://api.openai.com/v1"
            return
        }

        settings.baseURL = urlText
        settings.apiKey = apiKey.trimmed
        settings.model = model.trimmed
        settings.systemPrompt = systemPrompt
        settings.streaming = streaming
        settings.imageDataURL = imageDataURL
        dismiss()
    }
}
