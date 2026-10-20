import UIKit
import ImageIO

enum ImageTool {
    /// 用 ImageIO 直接生成缩略图，避免把整张 48MP 原图解码进内存。
    /// 最长边压到 maxEdge，并按 EXIF 方向摆正，统一转成 JPEG。
    static func attachment(from data: Data, maxEdge: CGFloat = 1400) -> Attachment? {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil) else { return nil }

        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceShouldCacheImmediately: true,
            kCGImageSourceThumbnailMaxPixelSize: maxEdge
        ]

        guard let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
            return nil
        }
        guard let jpeg = UIImage(cgImage: cgImage).jpegData(compressionQuality: 0.8) else {
            return nil
        }
        return Attachment(jpegData: jpeg)
    }

    /// 给界面显示用的小图，避免在 SwiftUI body 里反复解码大图。
    static func thumbnail(from attachment: Attachment, maxPixel: CGFloat) -> UIImage? {
        guard let source = CGImageSourceCreateWithData(attachment.jpegData as CFData, nil) else {
            return nil
        }
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceShouldCacheImmediately: true,
            kCGImageSourceThumbnailMaxPixelSize: maxPixel
        ]
        guard let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
            return nil
        }
        return UIImage(cgImage: cgImage)
    }
}
