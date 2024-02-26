# Precisely locate your lost MacBook via Offline Find

[Read the original story](https://hajekj.net/2024/02/26/searching-for-a-lost-macbook/)

## Prerequisites
* Access to your Apple ID
* MacBook or Hackintosh
    * `/usr/bin/swift` installed
    * Python 3 installed with PIP
    * VS Code or any other editor you prefer
* A little bit of technical skills
* Lost MacBook showing up in iCloud's Find My as offline, but location being updated from time to time via [Offline Find](https://support.apple.com/en-gb/guide/security/sece994d0126/web)

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
1. From the output, copy the value of `gena` value (it starts with `0x`, copy only the part before the quotes on the line, so from the example below the value is `0x0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF`):
    ```
    hajekj@Jan-MacBook-Air bleak % security find-generic-password -l 'BeaconStore' -g
    keychain: "/Users/hajekj/Library/Keychains/login.keychain-db"
    version: 512
    class: "genp"
    attributes:
        0x00000007 <blob>="BeaconStore"
        0x00000008 <blob>=<NULL>
        "acct"<blob>="BeaconStoreKey"
        "cdat"<timedate>=0x32303234303231383132313435365A00  "20240218121456Z\000"
        "crtr"<uint32>=<NULL>
        "cusi"<sint32>=<NULL>
        "desc"<blob>=<NULL>
        "gena"<blob>=0x0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF  "<...>"
        "icmt"<blob>=<NULL>
        "invi"<sint32>=<NULL>
        "mdat"<timedate>=0x32303234303231383132313435365A00  "20240218121456Z\000"
        "nega"<sint32>=<NULL>
        "prot"<blob>=<NULL>
        "scrp"<sint32>=<NULL>
        "svce"<blob>="BeaconStore"
        "type"<uint32>=<NULL>
    ```
1. Download the following [script](/src/swift/findmy-decryptor.swift) and put the obtained value from above into the variable called `hexKey`. Modify the path to the file in `fileURL` property to match your username and the `baUUID` (which you obtained earlier) of the device you want to track.
1. Enable the script to be executed via `chmod +x ./airtag_decryptor.swift`
1. Execute the script via `./airtag_decryptor.swift`
1. The result should be a file called `decrypted.plist` in the same folder as the script. Try to open the file with your editor, it should be an XML file.

### 2. Generating the broadcast keys
Now you need the generate the keypairs which are being actually broadcasted by the device, this is important, so that you can find your device in all the devices around you. The keys are generated since the pairing date to up to 48 hours ahead. If you need keys for the future, you can modify the script, or just run it again.

> Only `KeyType.PRIMARY` is relevant when searching for a MacBook.

1. Download the [script](/src/python/findmy-keygeneration.py) and place it in the same folder like `decrypted.plist` file.
1. In the same folder install [FindMy.py](https://github.com/malmeloo/FindMy.py) via:
    ```bash
    pip3 install findmy
    ```
1. Run the script (it is going to run for couple of minutes and the result will be file called `discovery-keys.csv`)
    ```bash
    python3 findmy-keygeneration.py
    ```

### 3. Searching for the device
The last thing to do is to take the keys and load them into the discovery tool, which will search for Bluetooth Low Energy beacons, calculate their key and compare it with the list of keys.

> At the moment, it is necessary to manually modify [FindMy.py's code](https://github.com/malmeloo/FindMy.py/pull/10) until the PR is merged in order for the search to work on MacOS.

1. Download the [script](/src/python/findmy-discover.py) and place it in the same folder like `discovery-keys.csv` file.
1. Run the script
    ```bash
    python3 findmy-discover.py
    ```
1. Walk around with the device and observe the pings, the closer you get, the lower [RSSI](https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/) (distance displayed is not an indicator of an actual distance).
1. The script will produce `discovery-output.csv` file containing all the discovered devices around, but the command-line will output only if the targeted device is found

#### Actual search
Go to the last location of your device from Find My map. The sooner the better, the Bluetooth Low Energy broadcast works when your device is not connected to the internet, but it also drains battery. Start walking around slowly. From our tests, the beacon can be picked up every 2 seconds up to 5 minutes, depending on your distance and the surrounding area. Once you pick up the beacon's signal, try to find a bearing by walking around and comparing signal strength. The lower the RSSI, the closer you are. Remember that the signal can bounce around objects etc.

### BONUS: 4. Location history
You can retrieve up to 7 days of location history via Offline Find. This is useful if you want to figure out where was the device moving. This is an advanced thing process, so do this only when you are confident with your technical skills.

> This tutorial is dependent on running `findmy` library [version with support for MFA](https://github.com/malmeloo/FindMy.py/pull/9)

1. Install [Docker](https://www.docker.com/products/docker-desktop/)
1. Run [Anisette server](https://github.com/Dadoum/anisette-v3-server) image
    ```bash
    docker run -d --restart always --name anisette-v3 -p 6969:6969 dadoum/anisette-v3-server
    ```
1. Download this [script](/src/python/findmy-historicallocations.py)
1. Fill out `ACCOUNT_EMAIL` and `ACCOUNT_PASS` variables with your Apple ID
    > You can just use any Apple ID, since the Offline Find data is not tied to any specific ID (due to the privacy provided by public key and encryption)
1. Filter out the `discovery-keys.csv` to include only keys for the time you want to retrieve the location history for
1. The script will produce `location_history.json` file, which can then be loaded to Excel (`Data` > `Get Data` > `From File` > `From JSON`)
1. Once you load the JSON to Excel, you will get following columns:
    * `time` - the time the device was detected
        * Use the following formula to convert it to proper date time field ([source](https://stackoverflow.com/questions/4896116/parsing-an-iso8601-date-time-including-timezone-in-excel)):
            ```
            =DATEVALUE(MID(A2,1,10))+TIMEVALUE(MID(A2,12,5))+(IF(MID(A2,17,1)="+",-1,1)*IFERROR(TIMEVALUE(MID(D2,18,5)),0))
            ```
    * `lat`, `lon` - latitude and longitude
    * `published_at` - when the data was uploaded to Find My network, please note that the data is usually delayed by ~30 minutes, but it can be much longer
    * `confidence` - no idea what this actually means, but probably based on RSSI, and seems like the higher the number, the closer the finder device was
    * `key` - public key at the time of finding
1. You can then create the [3D Map](https://support.microsoft.com/en-gb/office/get-started-with-3d-maps-6b56a50d-3c3e-4a9e-a527-eea62a387030) from the coordinates, confidence and time, to get an actual movement timeline

## Donations
If this helped you, please **[consider donating](https://github.com/sponsors/hajekj)** some little money to this effort. We have some plans to make an actual application with UI, so these steps are easier, and will also share some of the funds with authors of the used code.

## Support
This project is released as free and open source. If you need any help, feel free to [reach out](https://github.com/hajekj), will do my best to help.

## Future
I would like to turn this code into an actual end-to-end application, so anyone can easily (except for pulling the beacon keys) search for their lost device.

## Credits
None of this would be possible without the incredible work and effort of the following:

* [OpenHaystack's research](https://doi.org/10.2478/popets-2021-0045)
* [FindMy.py](https://github.com/malmeloo/FindMy.py)
* [YeapGuy's decryptor](https://gist.github.com/YeapGuy/f473de53c2a4e8978bc63217359ca1e4)
* Martin and Karel - for letting me borrow their MacBooks for testing
* Vlada - for giving me this idea by having his MacBook stolen

## Disclaimer
This project is not associated with Apple Inc.