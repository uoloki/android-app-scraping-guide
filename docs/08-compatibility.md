# 8. Emulator setups used in this guide

[Previous: certificates](07-certificates-and-pinning.md) · [Troubleshooting](troubleshooting.md) · [Back to overview](index.md)

I used Windows 11, Android Emulator `36.2.12`, platform tools `36.0.0`, and mitmproxy `12.1.2`. These are the emulator setups behind the screenshots and commands.

| Android / AVD | Image | What I verified |
| --- | --- | --- |
| 12 / API 31 `Tutorial_API31_Play` | Google Play, x86_64 | rootAVD `613caa4` and Magisk `30.6` gave me `uid=0` after setup and reboot. With AlwaysTrustUserCerts `1.3`, mitmproxy decrypted the demo's unpinned request. The demo's two pinned requests still failed; a targeted Frida `17.27.4` hook passed its OkHttp case. |
| 12 / API 31 `Tutorial_API31_Root` | AOSP `default`, x86_64 | Built-in `su` worked. I installed all three sample APK splits together and opened the product list. |
| 13 / API 33 `Pixel_6` | Google APIs, x86_64 | The rebuilt debug app trusted the user CA, and mitmproxy decrypted its product requests. |

For the split transfer in [chapter 5](05-dual-emulator-apks.md), I installed a locally built bundle on the Play emulator, copied its three APK files, and used `adb install-multiple` on AOSP. SAI 4.5 exported the installed AOSP app as an `.apks` archive.

The API 31 Play setup ([Magisk](06-rootavd-magisk.md), then [certificates and pinning](07-certificates-and-pinning.md)) is only worth the effort for apps that ignore user CAs. If you can rebuild the app, `debug-overrides` on API 33 is much simpler. Either way, a system CA gets you past trust checks but not past certificate pinning.
