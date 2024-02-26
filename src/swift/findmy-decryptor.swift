#!/usr/bin/swift

//
//  airtag-decryptor.swift
//  
//
//  Created by Matus on 28/01/2024.
//  https://gist.github.com/YeapGuy/f473de53c2a4e8978bc63217359ca1e4
//
import Foundation
import CryptoKit

// Function to decrypt using AES-GCM
func decryptRecordFile(fileURL: URL, key: SymmetricKey) throws -> [String: Any] {
    // Read data from the file
    let data = try Data(contentsOf: fileURL)

    // Convert data to a property list (plist)
    guard let plist = try PropertyListSerialization.propertyList(from: data, options: [], format: nil) as? [Any] else {
        throw MyError.invalidFileFormat
    }

    // Extract nonce, tag, and ciphertext
    guard plist.count >= 3,
          let nonceData = plist[0] as? Data,
          let tagData = plist[1] as? Data,
          let ciphertextData = plist[2] as? Data else {
        throw MyError.invalidPlistFormat
    }

    let sealedBox = try AES.GCM.SealedBox(nonce: AES.GCM.Nonce(data: nonceData), ciphertext: ciphertextData, tag: tagData)

    // Decrypt using AES-GCM
    let decryptedData = try AES.GCM.open(sealedBox, using: key)

    // Convert decrypted data to a property list
    guard let decryptedPlist = try PropertyListSerialization.propertyList(from: decryptedData, options: [], format: nil) as? [String: Any] else {
        throw MyError.invalidDecryptedData
    }

    return decryptedPlist
}

// Function to convert hex string to Data
func data(fromHex hex: String) -> Data {
    var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
    hexSanitized = hexSanitized.replacingOccurrences(of: "0x", with: "")

    var data = Data(capacity: hexSanitized.count / 2)
    var index = hexSanitized.startIndex

    while index < hexSanitized.endIndex {
        let byteString = hexSanitized[index ..< hexSanitized.index(index, offsetBy: 2)]
        let byte = UInt8(byteString, radix: 16)!
        data.append(byte)
        index = hexSanitized.index(index, offsetBy: 2)
    }

    return data
}

// -> Hex format key from `security find-generic-password -l 'BeaconStore' -g` "gena" attribute value
let hexKey = "<YOUR_KEY>"
// -> Path to the .record file
let fileURL = URL(fileURLWithPath: "/Users/<USERNAME>/Downloads/<baUUID>.record")

// Convert hex key to Data
let keyData = data(fromHex: hexKey)

// Usage
let key = SymmetricKey(data: keyData)

do {
    let decryptedPlist = try decryptRecordFile(fileURL: fileURL, key: key)
    // Save decrypted plist as a file in the current directory
    let outputURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("decrypted.plist")
    try PropertyListSerialization.data(fromPropertyList: decryptedPlist, format: .xml, options: 0).write(to: outputURL)
    print("Decrypted plist saved at:", outputURL.path)
} catch {
    print("Error:", error)
}

enum MyError: Error {
    case invalidFileFormat 
    case invalidPlistFormat
    case invalidDecryptedData
}