import SwiftUI
import PhotosUI
import UIKit
import Foundation

struct ChatView: View {
    @EnvironmentObject private var settings: SettingsStore
    @EnvironmentObject private var chat: ChatStore

    @State private var showingSettings = false
    @State private var pickerItems: [PhotosPickerItem] = []
    @State private var isLoadingImages = false
    @FocusState private var inputFocused: Bool

    private var canSend: Bool {
        !chat.draft.trimmed.isEmpty || !chat.pendingImages.isEmpty
    }

    private var bannerBinding: Binding<Bool> {
        Binding(
            get: { chat.banner != nil },
            set: { newValue in
                if !newValue { chat.banner = nil }
            }
        )
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                transcript
                composer
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("卧笔")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { toolbarItems }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
                    .environmentObject(settings)
            }
            .alert("还没配置好", isPresented: bannerBinding) {
                Button("去设置") {
                    chat.banner = nil
                    showingSettings = true
                }
                Button("取消", role: .cancel) {
                    chat.banner = nil
                }
            } message: {
                Text(chat.banner ?? "")
            }
            .onAppear {
                if !settings.isConfigured {
                    showingSettings = true
                }
            }
            .onChange(of: pickerItems) { _, newItems in
                guard !newItems.isEmpty else { return }
                loadImages(from: newItems)
            }
        }
    }

    // MARK: - 消息列表

    private var transcript: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 18) {
                    if chat.messages.isEmpty {
                        EmptyStateView { suggestion in
                            chat.draft = suggestion
                            inputFocused = true
                        }
                    }

                    ForEach(chat.messages) { message in
                        MessageRow(message: message, isWaiting: isWaiting(for: message))
                            .id(message.id)
                    }

                    Color.clear
                        .frame(height: 1)
                        .id("bottom")
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 20)
            }
            .scrollDismissesKeyboard(.interactively)
            .onChange(of: chat.messages.count) { _, _ in
                withAnimation(.easeOut(duration: 0.2)) {
                    scrollToBottom(proxy)
                }
            }
            .onChange(of: chat.messages.last?.text) { _, _ in
                scrollToBottom(proxy)
            }
        }
    }

    private func isWaiting(for message: ChatMessage) -> Bool {
        chat.isSending
            && message.role == .assistant
            && message.text.isEmpty
            && message.id == chat.messages.last?.id
    }

    private func scrollToBottom(_ proxy: ScrollViewProxy) {
        guard !chat.messages.isEmpty else { return }
        proxy.scrollTo("bottom", anchor: .bottom)
    }

    // MARK: - 输入区

    private var composer: some View {
        VStack(spacing: 10) {
            if !chat.pendingImages.isEmpty {
                pendingImagesStrip
            }
            HStack(alignment: .bottom, spacing: 8) {
                photoButton
                inputField
                sendButton
            }
        }
        .padding(.horizontal, 12)
        .padding(.top, 10)
        .padding(.bottom, 8)
        .background(.regularMaterial)
    }

    private var photoButton: some View {
        PhotosPicker(selection: $pickerItems, maxSelectionCount: 3, matching: .images) {
            Image(systemName: "photo.on.rectangle")
                .font(.system(size: 19, weight: .medium))
                .foregroundStyle(Color.accentColor)
                .frame(width: 40, height: 40)
                .background(Color(uiColor: .secondarySystemGroupedBackground), in: Circle())
        }
        .disabled(chat.isSending || isLoadingImages)
        .accessibilityLabel("选择图片")
    }

    private var inputField: some View {
        TextField("发消息，或点左边选张图…", text: $chat.draft, axis: .vertical)
            .lineLimit(1...5)
            .focused($inputFocused)
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(
                Color(uiColor: .secondarySystemGroupedBackground),
                in: RoundedRectangle(cornerRadius: 20, style: .continuous)
            )
            .submitLabel(.send)
            .onSubmit {
                guard !chat.isSending else { return }
                chat.send(settings: settings)
            }
    }

    private var sendButton: some View {
        Button {
            if chat.isSending {
                chat.stop()
            } else {
                inputFocused = false
                chat.send(settings: settings)
            }
        } label: {
            Image(systemName: chat.isSending ? "stop.fill" : "arrow.up")
                .font(.system(size: 17, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 40, height: 40)
                .background(sendButtonColor, in: Circle())
        }
        .disabled(!chat.isSending && !canSend)
        .accessibilityLabel(chat.isSending ? "停止" : "发送")
    }

    private var sendButtonColor: Color {
        if chat.isSending { return Color.red.opacity(0.85) }
        return canSend ? Color.accentColor : Color(uiColor: .systemGray4)
    }

    private var pendingImagesStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(chat.pendingImages) { image in
                    pendingThumbnail(image)
                }
            }
            .padding(.top, 6)
            .padding(.trailing, 6)
        }
    }

    private func pendingThumbnail(_ image: Attachment) -> some View {
        ZStack(alignment: .topTrailing) {
            AttachmentImage(attachment: image, side: 64, cornerRadius: 12)
            Button {
                chat.pendingImages.removeAll { $0.id == image.id }
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 18))
                    .symbolRenderingMode(.palette)
                    .foregroundStyle(.white, .black.opacity(0.55))
            }
            .offset(x: 5, y: -5)
            .accessibilityLabel("移除图片")
        }
    }

    // MARK: - 导航栏

    @ToolbarContentBuilder
    private var toolbarItems: some ToolbarContent {
        ToolbarItem(placement: .topBarLeading) {
            Button {
                chat.newChat()
            } label: {
                Image(systemName: "square.and.pencil")
            }
            .disabled(chat.messages.isEmpty || chat.isSending)
            .accessibilityLabel("新对话")
        }

        ToolbarItem(placement: .topBarTrailing) {
            Button {
                showingSettings = true
            } label: {
                Image(systemName: "gearshape")
            }
            .accessibilityLabel("设置")
        }
    }

    // MARK: - 选图

    private func loadImages(from items: [PhotosPickerItem]) {
        isLoadingImages = true
        Task { @MainActor in
            var loaded: [Attachment] = []
            for item in items {
                guard let data = try? await item.loadTransferable(type: Data.self) else { continue }
                let attachment = await Task.detached(priority: .userInitiated) {
                    ImageTool.attachment(from: data)
                }.value
                if let attachment {
                    loaded.append(attachment)
                }
                if loaded.count >= 3 { break }
            }

            let room = max(0, 3 - chat.pendingImages.count)
            if room > 0 {
                chat.pendingImages.append(contentsOf: loaded.prefix(room))
            }
            pickerItems = []
            isLoadingImages = false
        }
    }
}

// MARK: - 单条消息

struct MessageRow: View {
    let message: ChatMessage
    let isWaiting: Bool

    private var isUser: Bool { message.role == .user }

    var body: some View {
        HStack(alignment: .top, spacing: 0) {
            if isUser {
                Spacer(minLength: 44)
            }

            VStack(alignment: isUser ? .trailing : .leading, spacing: 8) {
                if !message.images.isEmpty {
                    messageImages
                }
                if isWaiting {
                    waitingBubble
                } else if !message.text.isEmpty {
                    textBubble
                }
            }

            if !isUser {
                Spacer(minLength: 44)
            }
        }
        .frame(maxWidth: .infinity, alignment: isUser ? .trailing : .leading)
    }

    private var messageImages: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(message.images) { image in
                    AttachmentImage(attachment: image, side: 112, cornerRadius: 14)
                }
            }
        }
    }

    private var textBubble: some View {
        Text(markdownText)
            .font(.system(size: 16))
            .lineSpacing(4)
            .foregroundStyle(message.isError ? Color.red : Color.primary)
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(bubbleBackground)
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .textSelection(.enabled)
            .contextMenu {
                Button {
                    UIPasteboard.general.string = message.text
                } label: {
                    Label("复制", systemImage: "doc.on.doc")
                }
            }
    }

    private var waitingBubble: some View {
        HStack(spacing: 8) {
            ProgressView()
                .controlSize(.small)
            Text("正在思考…")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 11)
        .background(
            Color(uiColor: .secondarySystemGroupedBackground),
            in: RoundedRectangle(cornerRadius: 18, style: .continuous)
        )
    }

    @ViewBuilder
    private var bubbleBackground: some View {
        if isUser {
            Color.accentColor.opacity(0.15)
        } else {
            Color(uiColor: .secondarySystemGroupedBackground)
        }
    }

    private var markdownText: AttributedString {
        let options = AttributedString.MarkdownParsingOptions(interpretedSyntax: .inlineOnlyPreservingWhitespace)
        return (try? AttributedString(markdown: message.text, options: options)) ?? AttributedString(message.text)
    }
}

// MARK: - 缩略图

struct AttachmentImage: View {
    let attachment: Attachment
    let side: CGFloat
    let cornerRadius: CGFloat

    @State private var image: UIImage?

    var body: some View {
        Group {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                Color(uiColor: .secondarySystemGroupedBackground)
            }
        }
        .frame(width: side, height: side)
        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
        .task(id: attachment.id) {
            image = ImageTool.thumbnail(from: attachment, maxPixel: side * 3)
        }
    }
}

// MARK: - 空状态

struct EmptyStateView: View {
    var onSuggestion: (String) -> Void

    private let suggestions = [
        "这张图里写了什么？",
        "把图里的英文翻译成中文",
        "看看这道菜用了什么食材",
        "用三句话帮我总结这张截图"
    ]

    var body: some View {
        VStack(spacing: 14) {
            brandMark

            Text("卧笔")
                .font(.system(size: 28, weight: .bold, design: .serif))

            Text("极简 AI 对话 · 支持看图\n接口和 Key 由你自己配置")
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)

            VStack(spacing: 8) {
                ForEach(suggestions, id: \.self) { suggestion in
                    Button {
                        onSuggestion(suggestion)
                    } label: {
                        HStack(spacing: 8) {
                            Text(suggestion)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                            Spacer(minLength: 0)
                            Image(systemName: "arrow.up.left")
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 11)
                        .background(
                            Color(uiColor: .secondarySystemGroupedBackground),
                            in: RoundedRectangle(cornerRadius: 14, style: .continuous)
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.top, 8)
        }
        .padding(.top, 36)
        .padding(.horizontal, 2)
    }

    private var brandMark: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color(red: 0.13, green: 0.14, blue: 0.17),
                                 Color(red: 0.29, green: 0.31, blue: 0.34)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 84, height: 84)

            Text("卧")
                .font(.system(size: 40, weight: .bold, design: .serif))
                .foregroundStyle(.white)
        }
        .overlay(alignment: .bottomTrailing) {
            Circle()
                .fill(Color(red: 0.70, green: 0.20, blue: 0.15))
                .frame(width: 14, height: 14)
                .offset(x: 3, y: 3)
        }
    }
}
