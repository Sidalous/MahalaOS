# Good Enough Definition

This document defines what "good enough" means for v1. Every feature is measured against a clear pass/fail criteria. When every Must Have row is green, we ship.

The goal is not perfection. The goal is that a non-technical person can use this phone as their only phone without wanting to switch back within a week.

---

## Must Haves

These are non-negotiable for v1. If any of these fail, it's not ready.

| # | Function | Good Enough | Not Acceptable |
|---|----------|-------------|----------------|
| 1 | Phone Calls | Reliable on 4G/5G, clear audio both ways, no echo, call history works | Dropped calls, robotic audio, needs restart to receive calls |
| 2 | SMS / MMS | Send and receive reliably including group MMS, delivery confirmation | Messages failing silently, group MMS broken, messages arriving out of order |
| 3 | WhatsApp (via Waydroid) | Send/receive text and media, voice and video calls work, notifications arrive within 30 seconds | Manual checking required, no notifications, calls failing |
| 4 | Facebook Messenger (via Waydroid) | Send/receive text and media, notifications arrive | Non-functional or requires constant manual checking |
| 5 | Web Browser | Firefox loads sites smoothly, video playback works, no frequent crashes | Constant crashes, broken rendering, unusably slow |
| 6 | Mobile Data | 4G/5G works reliably, option to disable 5G for battery saving | No data connection, frequent drops, no network switching control |
| 7 | Wi-Fi | Connects automatically to saved networks, stable connection, no drops | Fails to reconnect, frequent disconnections, needs manual intervention |
| 8 | Bluetooth | Pairs and maintains connection with headphones and speakers, audio doesn't cut out | Pairing failures, audio dropouts every few minutes, can't reconnect |
| 9 | Camera | Usable for social media — shutter lag under 2 seconds, acceptable colour/exposure in daylight | 10 second shutter lag, green/purple tint, blurry in normal conditions |
| 10 | Notifications | All app notifications arrive within 30 seconds, visible on lock screen, sounds/vibration work | Minutes late, silent, missing entirely |
| 11 | Battery Life | 12+ hours moderate use (calls, messaging, browsing, camera) | Dead by early afternoon under normal use |
| 12 | GPS / Navigation | Accurate positioning, works with OsmAnd or web-based maps, locks within 30 seconds | Can't get a fix, drifts by hundreds of metres, takes minutes to lock |
| 13 | Fingerprint / Screen Lock | Biometric works 8/10 times, PIN/pattern as fallback, lock screen is secure | Unreliable enough that user disables it, no security options |
| 14 | Notes App | Simple note-taking app preinstalled, option for local encryption | No way to take quick notes |
| 15 | UI / UX | Clean, intuitive, doesn't require Linux knowledge. Settings are discoverable. App launcher makes sense. | Requires terminal for basic tasks, confusing layout, ugly or broken UI |
| 16 | Thermals | Phone stays comfortable during normal use (calls, browsing, messaging) | Noticeably hot during basic tasks |
| 17 | Music / Podcasts | Spotify web or native audio player works, Bluetooth audio is stable | Audio cuts out, no way to play music, BT audio unusable |
| 18 | Setup / Install | Flash image and follow a guide in under 30 minutes, first-boot wizard handles basics | Requires build environment, compiling, or deep Linux knowledge |

---

## Nice To Haves

These improve the experience but are not blockers for v1. They become priorities for v2.

| # | Function | Notes |
|---|----------|-------|
| 1 | FinTech Apps (Revolut, Monzo) | Dependent on Play Integrity — may work via Waydroid but can't guarantee. Web banking is the v1 fallback. |
| 2 | Traditional Banking Apps (Barclays, Lloyds, HSBC) | Harder than FinTech due to stricter attestation checks. Web banking is the v1 fallback. |
| 3 | Seamless Android App Experience | Waydroid running smoothly enough that Android apps feel native — no visible container switching. |
| 4 | RCS Messaging | Dependent on carrier and Google's gatekeeping. SMS/MMS is the v1 baseline. |
| 5 | Social Media (Instagram, TikTok, Facebook) | Via Waydroid. Functional but not a v1 priority. Web versions are fallback. |
| 6 | Contactless Payments | Requires NFC and attestation. Almost certainly not achievable for v1. |
| 7 | OTA Updates | Seamless background updates without reflashing. Important for v2 but manual updates are acceptable for v1. |
| 8 | App Store / Curated App List | GUI-based app discovery and install. For v1, a documented list with install instructions is sufficient. |

---

## How We Test

- Every Must Have is tested weekly against a real-world checklist
- Testing is done by non-technical users where possible — if they can't figure it out, it's not good enough
- Each item is marked: ✅ Pass / ⚠️ Partial / ❌ Fail
- v1 ships when all Must Haves are ✅ Pass
