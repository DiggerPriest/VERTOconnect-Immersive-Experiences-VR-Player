// macOS preview encoder. Inputs are actual Godot renders, not AI artwork.
// swift frames_to_movie.swift FRAME_DIRECTORY OUTPUT.mp4
import AVFoundation
import AppKit

let args = CommandLine.arguments
guard args.count == 3 else { fatalError("Expected frame directory and output.mp4") }
let directory = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2])
let files = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
guard let first = files.first, let firstImage = NSImage(contentsOf: first),
      let cg = firstImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fatalError("No rendered frames")
}
if FileManager.default.fileExists(atPath: output.path) {
    try FileManager.default.removeItem(at: output)
}
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: cg.width, AVVideoHeightKey: cg.height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 4_000_000]])
let attributes: [String: Any] = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: cg.width, kCVPixelBufferHeightKey as String: cg.height,
    kCVPixelBufferCGImageCompatibilityKey as String: true,
    kCVPixelBufferCGBitmapContextCompatibilityKey as String: true]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attributes)
writer.add(input)
guard writer.startWriting() else { fatalError("Writer failed: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)
for (index, url) in files.enumerated() {
    while !input.isReadyForMoreMediaData && writer.status == .writing { Thread.sleep(forTimeInterval: 0.005) }
    guard writer.status == .writing else { fatalError("Writer stopped: \(String(describing: writer.error))") }
    try autoreleasepool {
        guard let image = NSImage(contentsOf: url)?.cgImage(forProposedRect: nil, context: nil, hints: nil),
              let pool = adaptor.pixelBufferPool else { fatalError("Frame or pixel buffer pool missing") }
        var optionalBuffer: CVPixelBuffer?
        guard CVPixelBufferPoolCreatePixelBuffer(nil, pool, &optionalBuffer) == kCVReturnSuccess,
              let buffer = optionalBuffer else { fatalError("Pixel buffer allocation failed") }
        CVPixelBufferLockBaseAddress(buffer, [])
        let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer), width: cg.width, height: cg.height,
            bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
            space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
        context.draw(image, in: CGRect(x: 0, y: 0, width: cg.width, height: cg.height))
        CVPixelBufferUnlockBaseAddress(buffer, [])
        guard adaptor.append(buffer, withPresentationTime: CMTime(value: Int64(index), timescale: 10)) else {
            throw writer.error ?? NSError(domain: "Preview", code: 1)
        }
    }
}
input.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
guard done.wait(timeout: .now() + 30) == .success, writer.status == .completed else {
    fatalError("Encoding did not complete: \(String(describing: writer.error))")
}
print("Encoded \(files.count) Godot frames at 10 fps: \(output.path)")
