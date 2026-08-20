import AppKit
import CoreImage
import Foundation

let destination = URL(string: "https://harmonica.nycu.club/p/")!
let output = URL(fileURLWithPath: "static/images/portal-qr.png")

let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(destination.absoluteString.data(using: .utf8), forKey: "inputMessage")
filter.setValue("M", forKey: "inputCorrectionLevel")

guard let qr = filter.outputImage else {
    fatalError("Unable to generate the Portal QR Code")
}

let scaled = qr.transformed(by: CGAffineTransform(scaleX: 24, y: 24))
let white = CIImage(color: CIColor.white).cropped(to: scaled.extent.insetBy(dx: -96, dy: -96))
let composed = scaled.composited(over: white)
let representation = NSCIImageRep(ciImage: composed)
let image = NSImage(size: representation.size)
image.addRepresentation(representation)

guard
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let png = bitmap.representation(using: .png, properties: [:])
else {
    fatalError("Unable to encode the Portal QR Code")
}

try png.write(to: output)
print("Generated \(output.path) for \(destination.absoluteString)")
