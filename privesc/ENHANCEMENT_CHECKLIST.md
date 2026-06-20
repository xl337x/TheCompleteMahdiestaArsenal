# windows-token-privileges.html Enhancement Checklist — v2.1
Generated: 2026-05-05 | Target: windows-token-privileges.html (4857 → 5582 lines, 281KB → 334KB)

## ✅ IMPLEMENTED

### Varbar
- [x] Added DOMAIN variable input
- [x] Added SVCNAME variable input
- [x] Wired both to applyVars() JS function (localStorage persistence)
- [x] Added SVCNAME to VAR_MAP for {{SVCNAME}} substitution in code blocks

### Sidebar Navigation (3 new pages added)
- [x] Quick Wins (<60s) — under Overview section
- [x] SeSystemtimePrivilege — under Rare / Situational section
- [x] Shell Troubleshooting — under Reference section

### Server Operators Page — COMPLETE REWRITE
- [x] Shell compatibility header (cmd/PS/evil-winrm/web shell/fully-qualified paths)
- [x] MANDATORY SPACE alert (binPath= must have space before value)
- [x] Error 1053 = EXPECTED/NORMAL explanation prominently placed
- [x] Method A: Add self to Administrators (no listener needed)
  - [x] CMD / web shell variant
  - [x] PowerShell / evil-winrm variant (sc.exe)
  - [x] Evil-winrm one-liner (semicolons — no multi-line)
  - [x] Maximum compatibility — fully qualified C:\Windows\System32\sc.exe paths
  - [x] Verify step: net localgroup
  - [x] Re-auth step: evil-winrm / impacket-psexec
  - [x] REVERT step with original VSS binPath
- [x] Method B: Reverse shell via nc64.exe
  - [x] Upload: evil-winrm, iwr, certutil, bitsadmin (all 4 methods)
  - [x] CMD / web shell variant
  - [x] PowerShell / evil-winrm variant (sc.exe mandatory)
  - [x] PS reverse shell base64 variant (no nc64 needed)
  - [x] REVERT step
- [x] Service Target Reference Table (ranked by safety)
  - [x] VSS — original binPath: C:\Windows\System32\vssvc.exe
  - [x] AppMgmt — original binPath: dllhost.exe /ProcessID:...
  - [x] wbengine — original binPath: C:\Windows\system32\wbengine.exe
  - [x] SNMPTRAP — original binPath: C:\Windows\System32\snmptrap.exe
  - [x] RasMan — original binPath: svchost.exe -k netsvcs -p
  - [x] AVOID list: LanmanServer, WinRM, Netlogon
- [x] Alternative Payloads section
  - [x] A: Add backdoor user + admins
  - [x] B: Enable RDP via reg add
  - [x] C: Disable Windows Firewall
  - [x] D: PowerShell base64 reverse shell (Kali generation command)
  - [x] E: msfvenom EXE approach
- [x] Service Enumeration (all shell types)
  - [x] PowerShell one-liner (evil-winrm safe)
  - [x] cmd.exe for-loop (web shell safe)
  - [x] WMIC alternative (when Get-Service / sc query fails SCM)
  - [x] Registry approach (when sc.exe blocked)
- [x] Error Reference Table
  - [x] Error 1053 explanation
  - [x] ChangeServiceConfig SUCCESS
  - [x] OpenService FAILED 5 (access denied)
  - [x] Cannot open Service Control Manager
  - [x] Missing closing '}' (multi-line PS in evil-winrm)
  - [x] sc not recognized / Set-Content error

### New Pages

#### Quick Wins Page (page-quickwins)
- [x] 8 ordered checks all under 60 seconds
- [x] whoami /all (privs AND groups in one command)
- [x] Filtered priv check (only high-value tokens)
- [x] Already admin check
- [x] OS build / CVE applicability
- [x] Missing patches (wmic qfe)
- [x] Spooler running (PrintSpoofer eligibility)
- [x] HiveNightmare check (icacls SAM)
- [x] Other user home dirs
- [x] Decision tree table: what you see → which page → expected result

#### SeSystemtimePrivilege Page (page-sesystemtime)
- [x] Info cards: who has it, primary/secondary attack, mandatory revert warning
- [x] Verify privilege step
- [x] Check current + DC time for reference
- [x] Method A: PowerShell (Set-Date)
- [x] Method B: cmd.exe (time / date)
- [x] Method C: w32tm (fake NTP server)
- [x] Kerberos verification step
- [x] REVERT step (w32tm domhier + net time)
- [x] Kerberos 5-minute tolerance explanation
- [x] Detection: Event 4616
- [x] Added to allprivs table as MEDIUM threat

#### Shell Troubleshooting Page (page-shellcompat)
- [x] Shell identification quick reference table (6 shell types)
- [x] Evil-WinRM multi-line fix (broken example vs fixed one-liner vs upload .ps1)
- [x] File Download master table (7 methods: iwr, certutil, bitsadmin, curl.exe, SMB, WebClient, evil-winrm upload)
- [x] SMB server setup note (-smb2support required for Win10/Server 2019+)
- [x] Constrained Language Mode detection + restrictions + workarounds
- [x] cmd.exe only cheat sheet (download, add user, service hijack, groups, RDP, spawn PS)

### CVE Section — 3 New CVEs Added
- [x] PrintNightmare CVE-2021-1675 / CVE-2021-34527
  - [x] Spooler check + patch KB check
  - [x] msfvenom DLL + impacket-smbserver
  - [x] SharpPrintNightmare LPE variant
  - [x] PowerShell PoC (calebstewart) with Invoke-Nightmare
- [x] Certifried CVE-2022-26923
  - [x] certipy find check
  - [x] Full exploit chain (account update + req + auth)
- [x] CVE-2023-28252 CLFS LPE
  - [x] Patch KB check
  - [x] PoC transfer and run

### All Privileges Table — 4 New Rows Added
- [x] SeSystemtimePrivilege — MEDIUM — break Kerberos
- [x] SeSystemProfilePrivilege — LOW — ETW profiling (note: investigate with SeDebug)
- [x] SeCreatePagefilePrivilege — LOW — pagefile + SeBackup chain
- [x] SeCreatePermanentPrivilege — LOW — rootkit persistence primitive
- [x] SeDelegateSessionUserImpersonatePrivilege — updated note (cross-session token theft research)

### SeDebug Page — Enhancements
- [x] Vector 1 Step 3: evil-winrm download command (download WPATH\lsass.dmp /home/kali/)
- [x] Vector 1 Step 3: SMB exfil alternative
- [x] Vector 1 Step 4: pypykatz parse (pip3 install pypykatz && pypykatz lsa minidump)
- [x] Vector 1 Step 4: mimikatz offline parse
- [x] Alert updated to mention pypykatz as Kali-side parser

### Writeups Section — 5 New HTB Writeups
- [x] Return (HTB) — Server Operators → VSS binPath → Error 1053 lesson
- [x] Forest (HTB) — Account Operators → Exchange Windows Permissions → DCSync
- [x] Blackfield (HTB) — Backup Operators → evil-winrm strips privs → PSRemoting fix
- [x] Fuse (HTB) — Print Operators → SeLoadDriver → Capcom → SYSTEM
- [x] Monteverde (HTB) — reg save on non-DC → secretsdump

### JSON Prompt — Updated
- [x] Version bumped to 2.1
- [x] universal_sc_exe_rules section added (4 rules)
- [x] implemented_in_token_html field documents completion state
- [x] allprivs_missing_privileges section fully documented (from prior session)

## ⚠️ NOT YET IMPLEMENTED (Future Sessions)

- [ ] SeManageVolume: wbemcomn trigger fix (wmiprvse vs iphlpsvc correction)
- [ ] SeManageVolume: AV-bypassing custom mingw DLL workflow
- [ ] SeBackupPrivilege: wbadmin alternative when diskshadow unavailable (older Server)
- [ ] SeImpersonate: .NET version check for correct GodPotato variant
- [ ] SeImpersonate: SigmaPotato fileless PS reflection one-liner
- [ ] SeImpersonate: Full JuicyPotato CLSID list with OS filter
- [ ] DnsAdmins: find DC hostname commands (nltest / net group)
- [ ] DnsAdmins: verify DNS restart with nslookup
- [ ] Backup Operators: DC vs non-DC validation flow
- [ ] All sections: shell compat header for every page (currently only serverops has it explicitly)

## 📦 Files Modified
- windows-token-privileges.html (281KB → 334KB, 4857 → 5582 lines)
- token_enhancement_prompt.json (v2.0 → v2.1)
- ENHANCEMENT_CHECKLIST.md (this file — new)
