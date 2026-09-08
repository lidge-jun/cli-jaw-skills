import Vision
import AppKit
import Foundation

struct OCRResult: Codable {
    let file: String
    let text: String
    let error: String?
}

// Usage: swift ocr.swift <max_concurrency> <img1> <img2> ...
let args = Array(CommandLine.arguments.dropFirst())

// 인자가 최소 2개 필요 (concurrency + 이미지 1개 이상)
if args.count < 2 {
    print("[]")
    exit(0)
}

// 첫 번째 인자는 병렬 처리 최대 수치 (예: M1 16GB 기준 3~4)
let maxConcurrency = Int(args[0]) ?? 2
let imagePaths = Array(args.dropFirst())

var results = [OCRResult]()
let queue = DispatchQueue(label: "ocr.results")
let semaphore = DispatchSemaphore(value: maxConcurrency)

// 커스텀 큐 사용
let processQueue = DispatchQueue(label: "ocr.process", attributes: .concurrent)
let group = DispatchGroup()

for imagePath in imagePaths {
    group.enter()
    processQueue.async {
        // 동시 실행 수 제한 (세마포어)
        semaphore.wait()
        defer {
            semaphore.signal()
            group.leave()
        }
        
        let url = URL(fileURLWithPath: imagePath)
        guard let image = NSImage(contentsOf: url),
              let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            queue.sync { results.append(OCRResult(file: imagePath, text: "", error: "Could not load image")) }
            return
        }
        
        let request = VNRecognizeTextRequest()
        request.recognitionLanguages = ["ko-KR", "en-US"]
        request.recognitionLevel = .accurate
        // GPU + Neural Engine 활용 (usesCPUOnly 기본값 false)
        // 동시성은 세마포어가 제어하므로 하드웨어 가속 최대한 활용
        
        do {
            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            try handler.perform([request])
            
            let text = request.results?.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n") ?? ""
            queue.sync { results.append(OCRResult(file: imagePath, text: text, error: nil)) }
        } catch {
            queue.sync { results.append(OCRResult(file: imagePath, text: "", error: error.localizedDescription)) }
        }
    }
}

group.wait()

// 파일명 순서로 정렬하여 페이지 순서 보장
results.sort { $0.file < $1.file }

let encoder = JSONEncoder()
encoder.outputFormatting = .prettyPrinted
if let jsonData = try? encoder.encode(results),
   let jsonString = String(data: jsonData, encoding: .utf8) {
    print(jsonString)
} else {
    print("[]")
}
