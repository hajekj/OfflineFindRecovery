# Precisely locate your lost MacBook via Offline Find

[Read the original story](TBD)

## Prerequisites
* Access to your Apple ID
* MacBook or Hackintosh
    * `/usr/bin/swift` installed
    * Python 3 installed
    * VS Code or any other editor you prefer
* A little bit of technical skills

## Steps

### 1. Obtaining beacon keys
First, you need to obtain the keypair which is being used to generate the broadcasting public key, along with a shared secret. This has to be done via acessing some files within MacOS. If you lost your MacBook, you can just sign-in to another one (your friend's for example) with your Apple ID and the files will sync there from iCloud. The files are encrypted, so you also need to access the decryption key from your Keychain.

> [!WARNING]
> Please note, that sharing this will allow the person holding your initial keypair to track your devices, even when you are offline, with a very good precision. Don't share the keys with anyone you don't trust.

1. Start by signing into [iCloud.com](https://www.icloud.com) and accessing Find My from there.
1. Open [F12 Developer Tools](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/Web_Inspector_Tutorial/EnableWebInspector/EnableWebInspector.html), switch to Network tab, and find the request ending with `refreshClient`
1. Next view the response, and find the device you are going to search for, you are interested in `baUUID`, note it down, you will need it later.
1. Open Terminal on your MacBook, and execute the following command:
    ```bash
    security find-generic-password -l "BeaconStore" -g
    ```
1. From the output, copy the value of `gena` value (it starts with `0x`):
    ```

    ```
1. Download the following [script](TBD) and put the obtained value from above into the variable called `hexKey`. Modify the path to the file in `fileURL` property to match your username and the `baUUID` (which you obtained earlier) of the device you want to track.
1. Enable the script to be executed via `chmod +x ./airtag_decryptor.swift`
1. Execute the script via `./airtag_decryptor.swift`
1. The result should be a file called `decrypted.plist` in the same folder as the script. Try to open the file with your editor, it should be an XML file.

### 2. Generating the broadcast keys

### 3. Searching for the device

### BONUS: 4. Location history


## Donations
If this helped you, please **[consider donating](https://github.com/sponsors/hajekj)** some little money to this effort. We have some plans to make an actual application with UI, so these steps are easier, and will also share some of the funds with authors of the used code.

## Credits
None of this would be possible without the incredible work and effort of the following:

* [FindMy.py](https://github.com/malmeloo/FindMy.py)
* [OpenHaystack's research](https://doi.org/10.2478/popets-2021-0045)
* Martin and Karel - for borrowing me their MacBooks for testing
* Vlada - for giving me this idea by having his MacBook stolen
