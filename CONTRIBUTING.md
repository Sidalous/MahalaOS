# Contributing

We need help from people at every skill level. You don't need to write kernel code to make a difference.

---

## Ways to Contribute

### No Code Required

**Testing** — The single most valuable contribution. Use the phone, report what breaks. Good bug reports include: what you did, what you expected, what actually happened, and device/OS version. Screenshots and logs help enormously.

**Documentation** — Write guides, improve existing docs, translate into other languages. If you had to figure something out the hard way, write it down so the next person doesn't have to.

**Design** — Icons, wallpapers, boot splash, UI mockups. We need to look as good as iOS and Android or people won't take us seriously.

**User Research** — Hand the phone to someone non-technical. Watch them use it. Write down where they struggle. This is worth more than a hundred lines of code.

### Code Contributions

We work across multiple languages depending on the layer:

| Layer | Language | Examples |
|-------|----------|----------|
| Kernel / Drivers | C | Camera, fingerprint, power management |
| System Services | C, Rust | Audio, Bluetooth, telephony |
| OS Tooling / Build | Python | Image build scripts, automation, packaging |
| UI / Apps | Vala, Python | Phosh improvements, native mobile apps |
| Web / Tooling | JavaScript | Website, flasher tool |

**If you're not sure where to start:** Look for issues tagged `good-first-issue`. These are scoped, documented, and achievable in a weekend.

### Community

**Spread the word** — Blog about us, share on social media, tell your privacy-conscious friends. Early visibility attracts contributors.

**Help others** — Answer questions in Matrix/Discord, help new testers with setup issues.

---

## How We Work

- **One device focus.** We support the OnePlus 6T until it's excellent. Resist the urge to add devices early.
- **User-first decisions.** Every change should make the phone more usable for a non-technical person. Cool technical achievements that don't improve daily use get deprioritised.
- **Small PRs.** One fix per PR. Describe what it changes and how to test it.
- **Test before submitting.** Flash the image, verify your change works on the actual device.
- **Be kind.** We're building something together. Respectful disagreement is welcome. Hostility isn't.

---

## Setting Up a Development Environment

[TBD — will be documented once the build system is established in Phase 0]

---

## Reporting Bugs

Use the issue tracker. One issue per bug. Include:

1. **What you did** — Steps to reproduce
2. **What you expected** — The correct behaviour
3. **What happened** — The actual behaviour
4. **Environment** — OS version, image version, any modifications
5. **Logs** — If applicable, include `dmesg` or `journalctl` output
6. **Screenshots / video** — If it's a UI issue

---

## Code of Conduct

Be respectful. Be constructive. Remember that many contributors are volunteering their time. We're here to build something good, not to argue about distro wars.

Harassment, discrimination, and personal attacks will result in removal from the project. No warnings, no debates.
