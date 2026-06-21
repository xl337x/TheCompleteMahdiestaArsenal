# TheCompleteMahdiestaArsenal

Static browser-based reference for offensive security operations. Set `KALI_IP`, `TARGET`, `USER`, `PASS`, `DOMAIN`, `PORT` once — every command across all 15 modules updates in real time.

[![Live](https://img.shields.io/badge/live-xl337x.github.io-brightgreen)](https://xl337x.github.io/TheCompleteMahdiestaArsenal/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Tools](https://img.shields.io/badge/modules-15-red)]()

---

https://github.com/xl337x/TheCompleteMahdiestaArsenal/raw/main/mahdiesta-arsenal-demo.mp4

---

## Modules

| Module | Coverage |
|---|---|
| **AD Boom** `v5.0` | 325+ commands — NTLM relay, Kerberoasting, AS-REP roasting, RBCD, DCSync, Pass-the-Hash, Pass-the-Ticket, secretsdump |
| **ADCS Arsenal** | ESC1–ESC16 — certipy, PKINIT, shadow credentials, CA/template abuse |
| **NetExec Guide** | SMB / LDAP / RDP / WinRM — credential spray, shares, LSA dump, NTDS, SAM |
| **BloodHound Arsenal** | Attack path methodology + full Cypher query library — shortest paths, owned objects, ACL chains |
| **bloodyAD Arsenal** | DACL/ACL abuse — GenericAll, WriteDACL, GenericWrite, shadow creds, targeted Kerberoast |
| **Rubik's Cube Injector** `v5` | UNION / Blind / Time-based / OOB / Error-based — WAF bypass encodings, sqlmap builder, 1000+ payloads |
| **SQLi → RCE** | `INTO OUTFILE`, `xp_cmdshell`, `LOAD DATA INFILE`, stacked queries |
| **Web Arsenal** | Reverse shells, LFI/RFI, SSRF, file upload bypass, SSTI, path traversal |
| **WebEnum Arsenal** | vhosts, directory brute, tech fingerprinting, API endpoint discovery |
| **AuthBreaker** | JWT manipulation, OAuth abuse, IDOR, session fixation, password reset flaws |
| **Command Injection** | Blind/OOB, filter bypass (space, pipe, semicolon, wildcard) |
| **OSINT Dorks** `v3.0` | Google / Shodan / GitHub / Censys / Fofa — recon, exposed secrets, infra mapping |
| **PrivEsc Toolkit** | Windows: token privs, service hijacking, DLL hijack, unquoted paths, AlwaysInstallElevated, SAM — Linux: SUID, sudo, cron, capabilities |
| **TokenPriv Operator** | SeImpersonate, SeDebug, SeRestore, SeTakeOwnership — GodPotato, PrintSpoofer, RoguePotato |
| **Transfer Arsenal** | File transfer one-liners — HTTP, SMB, FTP, certutil, Base64, PowerShell |

---

## Variable System

Fill once at the top of any module. Every command — certipy, netexec, msfvenom, sqlmap, wget — renders with your values substituted.

```
KALI_IP   TARGET   USER   PASS   DOMAIN   PORT   RPORT   WPATH   LFILE
```

PrivEsc Toolkit adapts per OS — Windows fields (WPATH, SVCBIN) hide on Linux mode, Linux fields (LFILE) hide on Windows mode.

---

## Usage

```bash
git clone https://github.com/xl337x/TheCompleteMahdiestaArsenal
cd TheCompleteMahdiestaArsenal
python3 -m http.server 8000
```

Or open `index.html` directly — no server required.

Live: [xl337x.github.io/TheCompleteMahdiestaArsenal](https://xl337x.github.io/TheCompleteMahdiestaArsenal/)

---

## Screenshots

<table>
<tr>
<td><img src="video_shots/01_intro.png" width="400"/></td>
<td><img src="video_shots/04_filter_ad.png" width="400"/></td>
</tr>
<tr>
<td><img src="video_shots/08_adcs.png" width="400"/></td>
<td><img src="video_shots/09_adcs_light.png" width="400"/></td>
</tr>
<tr>
<td><img src="video_shots/10_sqli_rce.png" width="400"/></td>
<td><img src="video_shots/07_filter_privesc.png" width="400"/></td>
</tr>
</table>

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `/` | Focus search |
| `T` | Toggle dark / light theme |
| `Esc` | Clear / close |

---

## Related

| Repo | Description |
|---|---|
| [uploadpwner](https://github.com/xl337x/uploadpwner) | File upload exploitation framework `v6.0` |
| [AuthFinder](https://github.com/xl337x/AuthFinder) | Multi-protocol access discovery + command execution |
| [ligolo-helper](https://github.com/xl337x/ligolo-helper) | Ligolo-ng tunnel setup |
| [transfer_files](https://github.com/xl337x/transfer_files) | File transfer one-liners |

---

MIT — [@mahdiesta](https://github.com/xl337x)
