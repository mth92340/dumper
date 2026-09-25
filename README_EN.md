# 🛠️ FiveCFX - Dumper

Tool to extract and decrypt resources from FiveM servers.

## ⚠️ WARNING

**Risks:** FiveM ToS violation, bans, legal risks.  
**Legitimate use only:** YOUR servers, security audit, educational research.  
**You are responsible for your actions.**

---

## 🚀 Quick Installation

```batch
1. Install Python 3.x (check "Add to PATH")
   → https://www.python.org/downloads/

2. Install Java
   → https://www.java.com/download/

3. Double-click install.bat → IMPORTANT

4. Verify:
   python --version
   java -version
```

---

## 📖 Usage

### Simple Method

```batch
1. Connect to the FiveM server
2. Double-click d.bat
3. Enter the link: cfx.re/join/abc123
4. Type "all" or resource numbers: 0,2,5
5. Results in Output/
```

### Find the cfx.re link
- F8 in FiveM → link displayed
- https://5metrics.dev/resources → search for your server

---

## 📂 Results

Extracted files are located in `Output/`:
- `.lua` → Decompiled scripts
- `.js/.html/.css` → NUI interface
- `.yft/.ytd/.ydr` → 3D models (stream)
- `.meta` → GTA configurations

### Fix stream files (optional)
If `.yft/.ytd` files don't open in OpenIV:
1. Launch `FIXER/FivemDecryptFixer.exe`
2. Input: `Output/resource/stream`
3. Output: `Fix/`
4. Click "Fix Files"

---

## 🐛 Common Issues

| Error | Solution |
|--------|----------|
| "Python not found" | Reinstall Python with "Add to PATH" |
| "FiveM process not found" | Connect to FiveM server before running |
| "Token not found" | Run as Administrator |
| "unluac failed" | Install Java JRE |
| Corrupted .yft files | Use FivemDecryptFixer.exe |

---

## ⚙️ Advanced Options

**Modify speed**: In `auto.py` line 173
```python
dumper = FiveMDumper(base_url, token, max_workers=15)  # 15 = thread count
```

**Disable cleanup**: Comment lines 178-186 in `auto.py`

**Extract without decryption**: Comment `decryptor.start()` line 176

---

## 🔒 Security

**Best practices:**
- Scan extracted files with antivirus
- Don't redistribute obtained resources
- Look for backdoors in Lua/JS scripts:
  ```lua
  load(), loadstring(), os.execute(), io.popen()  -- ❌ SUSPICIOUS
  ```

---

## 📊 Technical Information

**Compatibility:**
- Windows 10/11 (64-bit)
- Python 3.8-3.12
- FiveM b2802+
- Lua 5.4

**How it works:**
1. FiveM memory scan → Authentication token extraction
2. Download encrypted resources
3. ChaCha20 + AES-256-CBC decryption
4. Lua decompilation with unluac54.jar
5. RPF archive extraction (vehicles, maps)

---

## 📞 Support

- Resources: https://5metrics.dev/resources

---

*Educational tool - Use at your own risk*
