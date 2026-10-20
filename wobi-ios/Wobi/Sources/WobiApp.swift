import SwiftUI

@main
struct WobiApp: App {
    @StateObject private var settings = SettingsStore()
    @StateObject private var chat = ChatStore()

    var body: some Scene {
        WindowGroup {
            ChatView()
                .environmentObject(settings)
                .environmentObject(chat)
        }
    }
}
