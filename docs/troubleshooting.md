# Troubleshooting

[Back to visual guide](index.md)

Check the failure at the stage where it appears.

| What you see | Check and fix |
| --- | --- |
| No emulator in `adb devices` | Start the AVD, run `adb wait-for-device`, and make sure `adb` comes from your Android SDK `platform-tools` folder. |
| Gradle cannot start | This sample checkout lacks `gradle-wrapper.jar`. Use installed Gradle 8.13 with JDK 17 as in [chapter 1](01-environment-setup.md). |
| No app request in mitmproxy | Confirm mitmdump listens on Windows `127.0.0.1:8080`. `adb shell settings get global http_proxy` should print `10.0.2.2:8080`. Restart the app and search. |
| Only `CONNECT`, or a TLS trust error | Install the **public** mitmproxy certificate as an Android **CA certificate**, then run the rebuilt debug APK with `debug-overrides`. Release apps usually ignore user CAs; for those, see [chapter 7](07-certificates-and-pinning.md). |
| Unpinned request decrypts, pinned request fails | The route and CA work; the app is pinning. In the pinning demo, system CA trust fixed the unpinned request but neither pinned one. See the Frida step in [chapter 7](07-certificates-and-pinning.md). |
| Product list is blank after HTTPS works | Change `Product.kt` price from `Int` to `Double`; the current API returns decimals. Rebuild and reinstall. |
| Split install says a split is missing | Run `adb shell pm path <package>` on the source and pull every listed APK. Install the set in one `adb install-multiple` call. |
| Split install reports signature or ABI error | Compare signing identities, Android API level, and `adb shell getprop ro.product.cpu.abi` on both devices. Uninstalling a disposable conflicting copy deletes its app data. |
| Magisk app says **Requires additional setup** | Complete its prompt, cold boot with the patched ramdisk, authorize Shell in Magisk, then verify `adb shell su -c id` returns `uid=0`. |
| Magisk module reports **Done**, but the system CA is missing | Check `/data/adb/modules_update/trustusercerts` for staged files, then reboot with the patched ramdisk. Verify the active `service.sh` is nonempty and the CA appears in `/system/etc/security/cacerts`. |
| rootAVD fails unexpectedly on Windows | Run `where.exe find`. If a Unix tool shadows Windows `find.exe`, use a clean `PATH` or fix bare `find` calls in your local rootAVD batch copy. |

The Python exporter runs directly on Windows. It does not need the emulator or mitmproxy after API discovery. If it times out, check access to `https://dummyjson.com` and retry with a small `--max-items` value. The live API count may differ from the screenshots.

When finished, clear Android's proxy with `adb shell settings put global http_proxy :0` and remove the user CA in Android Settings. If you installed the Magisk CA module, reboot to update its system copy. Keep `capture.mitm`, `capture-advanced.mitm`, and `mitmproxy-ca.pem` private; captures may contain account data, and the `.pem` file contains the CA private key.
