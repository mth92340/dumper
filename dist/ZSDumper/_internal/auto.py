# fivem_full_dumper_decryptor.py
import sys
import os
import re
import psutil
import ctypes
import ctypes.wintypes as wintypes
import requests
import base64
import hmac
import hashlib
import subprocess
import json
from Crypto.Cipher import ChaCha20, AES
from Crypto.Util.Padding import unpad
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote


import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from pathlib import Path

# Handle PyInstaller bundled files
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============== TOKEN SCANNER ===============
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_READONLY = 0x02
PAGE_GUARD = 0x100

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
SIZE_T = ctypes.c_size_t

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress',       wintypes.LPVOID),
        ('AllocationBase',    wintypes.LPVOID),
        ('AllocationProtect', wintypes.DWORD),
        ('RegionSize',        SIZE_T),
        ('State',             wintypes.DWORD),
        ('Protect',           wintypes.DWORD),
        ('Type',              wintypes.DWORD),
    ]

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.restype = SIZE_T
VirtualQueryEx.argtypes = [wintypes.HANDLE, wintypes.LPCVOID,
                           ctypes.POINTER(MEMORY_BASIC_INFORMATION), SIZE_T]

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.restype = wintypes.BOOL
ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID,
                              wintypes.LPVOID, SIZE_T, ctypes.POINTER(SIZE_T)]

def find_fivem_process():
    pattern = re.compile(r"FiveM(_b\d+)?_GTAProcess", re.IGNORECASE)
    for proc in psutil.process_iter(attrs=['pid','name']):
        try:
            if pattern.match(proc.info['name']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_token():
    proc = find_fivem_process()
    if not proc:
        raise RuntimeError("FiveM process not found")

    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, proc.pid)
    if not handle:
        raise RuntimeError("Failed to open FiveM process")

    token_marker = b"X-CitizenFX-Token: "
    address = 0
    mbi = MEMORY_BASIC_INFORMATION()

    while VirtualQueryEx(handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if (mbi.State == MEM_COMMIT
            and (mbi.Protect & (PAGE_READWRITE | PAGE_READONLY))
            and not (mbi.Protect & PAGE_GUARD)):

            if mbi.RegionSize > 64 * 1024 * 1024:  # skip >64MB regions
                address += mbi.RegionSize
                continue

            buffer = (ctypes.c_char * mbi.RegionSize)()
            bytesRead = SIZE_T()

            if ReadProcessMemory(handle, mbi.BaseAddress, buffer, mbi.RegionSize, ctypes.byref(bytesRead)):
                data = bytes(buffer)[:bytesRead.value]
                idx = data.find(token_marker)
                if idx != -1:
                    end = data.find(b"\x00", idx)
                    if end == -1: end = idx + 100
                    token = data[idx:end].decode("ascii", errors="ignore")
                    return token.replace("X-CitizenFX-Token:", "").strip()

        address += mbi.RegionSize
    return None

# =============== IP FINDER ===============
def get_ip_from_cfx(link):
    if not link.startswith("http"):
        link = "https://" + link
    res = requests.get(link, timeout=15)
    res.raise_for_status()
    ip = res.headers.get("x-citizenfx-url")
    if not ip:
        raise RuntimeError("No X-CitizenFX-Url header")
    return ip.replace("http://","").replace("/","")

# =============== HELPERS ===============
def safe_name(name: str) -> str:
    """Sanitize folder/file names for Windows (remove : * ? etc)."""
    return re.sub(r'[<>:"/\\|?*]', "_", name)

# =============== DUMPER ===============
class FiveMDumper:
    def __init__(self, base_url, token, max_workers=10):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"X-CitizenFX-Token": token, "User-Agent": "CitizenFX/1"})
        self.max_workers = max_workers

    def xor_bytes(self, data: bytes) -> bytes:
        key = bytes([0x69] * 16)
        return bytes(b ^ key[i % 16] for i, b in enumerate(data[:32]))

    def get_configuration(self):
        url = f"{self.base_url}/client"
        data = {"method": "getConfiguration"}
        resp = self.session.post(url, data=data, timeout=30)
        resp.raise_for_status()
        js = resp.json()

        os.makedirs("Resources", exist_ok=True)
        with open("Resources/Grants.txt", "w", encoding="utf-8") as f:
            f.write(js.get("grants_token",""))
        return js.get("resources", [])

    def download_and_decrypt(self, url, key, iv, out_path):
        resp = self.session.get(url, timeout=60)
        resp.raise_for_status()

        # Try IETF 12-byte nonce first; fall back to 8-byte if needed
        dec = None
        try:
            cipher = ChaCha20.new(key=key, nonce=iv)  # try 12 byte nonce
            dec = cipher.decrypt(resp.content)
        except Exception:
            try:
                cipher = ChaCha20.new(key=key, nonce=iv[:8])
                dec = cipher.decrypt(resp.content)
            except Exception as e:
                raise RuntimeError(f"ChaCha20 decrypt failed: {e}")

        # Validation: check if RPF looks correct
        if out_path.lower().endswith(".rpf") and not dec.startswith(b"RPF"):
            raise ValueError(f"Invalid RPF header for {out_path}")

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f: f.write(dec)
        return out_path

    def unpack_rpf(self, rpf_path, out_dir):
        unpacker = os.path.join(BASE_DIR, "Bin", "Unpacker.exe")
        rpf_path = os.path.abspath(rpf_path)
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)

        try:
            proc = subprocess.run(
                f'"{unpacker}" "{rpf_path}" "{out_dir}"',
                shell=True, capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            if proc.stdout.strip():
                print(proc.stdout.strip())
            if proc.stderr.strip():
                print("stderr:", proc.stderr.strip())
            if "Extraído:" in proc.stdout or "Extracted:" in proc.stdout:
                print(f"✔ Unpacked {os.path.basename(rpf_path)} → {out_dir}")
            else:
                raise RuntimeError(f"Unpacker failed (code {proc.returncode})")

            manifest_path = os.path.join(out_dir, "fxmanifest.lua")
            stream_dir = os.path.join(out_dir, "stream")
            print("\n📦 Resource summary:")
            print("Path:", out_dir)

            if os.path.exists(manifest_path):
                print(" • fxmanifest.lua ✅")
            if os.path.isdir(stream_dir):
                stream_files = os.listdir(stream_dir)
                print(" • Stream files:", ", ".join(stream_files) if stream_files else "none")
            for fname in os.listdir(out_dir):
                if fname != "stream":
                    print(" •", fname)
        except Exception as e:
            print(f"❌ Error unpacking {rpf_path}: {e}")

    def fetch_resource(self, res):
        uri = base64.b64decode(res["uri"].split("#")[1])
        xored_key = uri[19:]
        iv = uri[53:61]
        hmac_key = self.xor_bytes(xored_key)[:32]

        res_name = safe_name(res["name"])
        temp_dir = os.path.join("Temp", res_name)
        unpacked_dir = os.path.join("Unpacked", res_name)

        tasks = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as exe:
            # normal files
            for fname,hsh in (res.get("files") or {}).items():
                url = f"{res.get('fileServer') or self.base_url+'/files'}/{res['name']}/{quote(fname)}?hash={hsh}"
                rpf_key = hmac.new(hmac_key, fname.encode(), hashlib.sha256).digest()
                out_path = os.path.join(temp_dir if fname.endswith(".rpf") else unpacked_dir, fname)
                fut = exe.submit(self.download_and_decrypt, url, rpf_key, iv, out_path)
                tasks.append((fut,fname,out_path))

            # stream files
            for fname,body in (res.get("streamFiles") or {}).items():
                url = f"{res.get('fileServer') or self.base_url+'/files'}/{res['name']}/{quote(fname)}?hash={body['hash']}"
                s_key = hmac.new(hmac_key, fname.encode(), hashlib.sha256).digest()
                out_path = os.path.join(unpacked_dir,"stream",fname)
                fut = exe.submit(self.download_and_decrypt, url, s_key, iv, out_path)
                tasks.append((fut,fname,out_path))

            # wait for all downloads
            rpf_files = []
            for fut,fname,out_path in tasks:
                try:
                    path = fut.result()
                    print("✔",fname)
                    if fname.endswith(".rpf"):
                        rpf_files.append(path)
                except Exception as e:
                    print("❌",fname,":",e)

        # unpack .rpf files after downloads are done
        for rpf_path in rpf_files:
            self.unpack_rpf(rpf_path, unpacked_dir)

    def run(self):
        resources = self.get_configuration()
        print("📦 Resources:")
        for i,res in enumerate(resources):
            print(i,res["name"])
        choice = input("Select indices or all: ").strip()
        chosen = resources if choice.lower()=="all" else [resources[int(x)] for x in choice.split(",") if x.strip().isdigit()]
        for res in chosen:
            self.fetch_resource(res)

# =============== DECRYPTOR (ported from your Node.js code) ===============
class FiveMDecryptor:
    def __init__(self):
        # Default constants copied from your Node script
        self.DefaultKey = bytes([
            0xb3, 0xcb, 0x2e, 0x04, 0x87, 0x94, 0xd6, 0x73, 0x08, 0x23, 0xc4, 0x93, 0x7a, 0xbd, 0x18, 0xad,
            0x6b, 0xe6, 0xdc, 0xb3, 0x91, 0x43, 0x0d, 0x28, 0xf9, 0x40, 0x9d, 0x48, 0x37, 0xb9, 0x38, 0xfb
        ])
        self.HeaderToVerify = b"FXAP"  # 0x46,0x58,0x41,0x50
        self.AesKey = bytes([
            0x7a, 0xba, 0x8d, 0x53, 0x25, 0x5b, 0x0e, 0xfd, 0x16, 0xbd, 0x35, 0x22, 0xa0, 0xb9, 0x26, 0xa5,
            0x61, 0x83, 0x2e, 0xec, 0xa2, 0x4b, 0xfd, 0x56, 0x9e, 0xc0, 0x1d, 0x8f, 0x38, 0x40, 0x54, 0x6d
        ])
        self.LuaHeaderHex = "1b4c7561540019930d0a1a0a040808785"  # string used for detection
        self.OutputDir = "Output"
        self.TempDir = "TempCompiled"
        self.KeymasterUrl = "https://keymaster.fivem.net/api/validate"

    def file_to_bytes(self, fp):
        with open(fp, "rb") as f:
            return f.read()

    def scan_for_id(self, buf: bytes):
        # Node used slice 74:78 and parsed hex -> uint32
        return int(buf[74:78].hex(), 16)

    def verify_encrypted(self, path):
        buf = self.file_to_bytes(path)
        return buf[:4] == self.HeaderToVerify

    def decrypt_file(self, path, key: bytes):
        """
        Equivalent of Node DecryptFile:
          iv = buffer.slice(74,86);
          encrypted = buffer.slice(86);
        """
        buf = self.file_to_bytes(path)
        if buf[:4] != self.HeaderToVerify:
            return None
        iv = buf[74:86]
        enc = buf[86:]
        return self._chacha_decrypt(enc, key, iv)

    def decrypt_buffer(self, hexdata: bytes, key: bytes, bufferPtr=None, ivPtr=None):
        """
        Equivalent of Node DecryptBuffer:
          default: iv = hexData.slice(80,92); encrypted = hexData.slice(92);
          alt: iv = hexData.slice(ivPtr, ivPtr + 12); encrypted = hexData.slice(bufferPtr);
        """
        if not hexdata:
            return None
        if bufferPtr is not None and ivPtr is not None:
            iv = hexdata[ivPtr:ivPtr+12]
            enc = hexdata[bufferPtr:]
            return self._chacha_decrypt(enc, key, iv)
        iv = hexdata[80:92]
        enc = hexdata[92:]
        return self._chacha_decrypt(enc, key, iv)

    def _chacha_decrypt(self, enc: bytes, key: bytes, iv: bytes):
        # Node uses chacha20.decrypt(key, iv, encrypted) with iv typically 12 bytes.
        # PyCryptodome supports ChaCha20 with 8 or 12 byte nonce depending on version.
        # Try 12 byte first, then fallback to 8-byte (iv[:8]).
        try:
            cipher = ChaCha20.new(key=key, nonce=iv)
            return cipher.decrypt(enc)
        except Exception:
            try:
                cipher = ChaCha20.new(key=key, nonce=iv[:8])
                return cipher.decrypt(enc)
            except Exception as e:
                raise RuntimeError(f"ChaCha20 decrypt failed: {e}")

    def calculate_client_key(self, grants_clk: bytes):
        # Node: iv = grantsClk.slice(0,16); encrypted=grantsClk.slice(16)
        iv = grants_clk[:16]
        enc = grants_clk[16:]
        # AES-256-CBC decrypt using AesKey and iv
        cipher = AES.new(self.AesKey, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc)
        # Node used crypto.createDecipheriv + final(); that expects PKCS#7 padding, so unpad
        # But to be safe, try unpad; if fails, return raw decrypted
        try:
            return unpad(decrypted, AES.block_size)
        except ValueError:
            return decrypted

    def process_lua_file(self, decrypted_buffer: bytes, output_path: str, resourceName: str, file_rel: str):
        tmp_path = os.path.join(self.TempDir, f"{resourceName}/{file_rel}c")
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(decrypted_buffer)
        final_path = output_path
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        # run unluac jar
        try:
            unluac_path = os.path.join(BASE_DIR, "Tools", "Decompile", "unluac54.jar")
            cmd = f'java -jar "{unluac_path}" "{tmp_path}"'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if proc.returncode != 0:
                # write error file
                fname = os.path.basename(final_path)
                name_only = os.path.splitext(fname)[0]
                errfile = os.path.join(os.path.dirname(final_path), f"error_{name_only}_unluac.txt")
                with open(errfile, "w", encoding="utf-8", errors="ignore") as ef:
                    ef.write(proc.stderr or proc.stdout or "Unknown unluac error")
            else:
                # write stdout to final_path
                with open(final_path, "w", encoding="utf-8", errors="ignore") as out:
                    out.write(proc.stdout)
        except Exception as e:
            # log and continue
            with open(final_path, "wb") as out:
                out.write(decrypted_buffer)
            print(f"unluac failed for {final_path}: {e}")

    def get_all_files(self, dirpath):
        results = []
        for root, _, files in os.walk(dirpath):
            for f in files:
                results.append(os.path.join(root, f))
        return results

    def decrypt_resource_file(self, resourcePath, relativeFile, decryptKey, resourceName, grantsClk):
        full_path = os.path.join(resourcePath, relativeFile)
        output_path = os.path.join(self.OutputDir, resourceName, relativeFile)

        if not os.path.exists(full_path):
            return

        # If not FXAP, just copy the file
        if not self.verify_encrypted(full_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(full_path, "rb") as inf, open(output_path, "wb") as outf:
                outf.write(inf.read())
            return

        # decrypt fxap with DefaultKey to get wrapped data
        decrypted_file = self.decrypt_file(full_path, self.DefaultKey)
        if not decrypted_file:
            return

        # primary attempt with decryptKey
        decrypted_buffer = self.decrypt_buffer(decrypted_file, decryptKey)
        # alternative key derived from grants_clk
        alternative_key = self.calculate_client_key(grantsClk)

        if decrypted_buffer is None:
            return

        # if lua file - follow detection & fallback attempts to match Node logic
        if relativeFile.lower().endswith(".lua"):
            is_lua = decrypted_buffer.hex().startswith(self.LuaHeaderHex)
            if is_lua:
                self.process_lua_file(decrypted_buffer, output_path, resourceName, relativeFile)
            else:
                # try the alternate offsets attempt (bufferPtr=90, ivPtr=78 per Node fallback)
                decrypted_alt = None
                try:
                    decrypted_alt = self.decrypt_buffer(decrypted_file, decryptKey, bufferPtr=90, ivPtr=78)
                except Exception:
                    decrypted_alt = None

                if decrypted_alt and decrypted_alt.hex().startswith(self.LuaHeaderHex):
                    self.process_lua_file(decrypted_alt, output_path, resourceName, relativeFile)
                else:
                    # try alternative key
                    try:
                        decrypted_alt2 = self.decrypt_buffer(decrypted_file, alternative_key)
                        if decrypted_alt2:
                            self.process_lua_file(decrypted_alt2, output_path, resourceName, relativeFile)
                        else:
                            # fallback: write raw decrypted_buffer as file (best-effort)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, "wb") as out:
                                out.write(decrypted_buffer)
                    except Exception as e:
                        print(f"Error decrypting lua {relativeFile}: {e}")
        else:
            # non-lua: write bytes
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as out:
                out.write(decrypted_buffer)

    def get_directories(self, source):
        return [os.path.join(source, d) for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]

    def validate_key_from_file(self, grants_path):
        # read grants token from file (Resources/Grants.txt)
        with open(grants_path, "r", encoding="utf-8") as f:
            grants_token = f.read().strip()
        # same shape as keymaster response payload: we only need payload grants and grants_clk
        # Node's ValidateKey when provided a file returned {"success": true, "grants_token": <token>}
        return {"success": True, "grants_token": grants_token}

    def decrypt_resource(self, resourcePath, resourceName, grants_token=None):
        fxap_file = os.path.join(resourcePath, ".fxap")
        if not os.path.exists(fxap_file):
            # No fxap means not encrypted → just copy everything over
            for file_full in self.get_all_files(resourcePath):
                relative = os.path.relpath(file_full, resourcePath).replace("\\", "/")
                output_path = os.path.join(self.OutputDir, resourceName, relative)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(file_full, "rb") as inf, open(output_path, "wb") as outf:
                    outf.write(inf.read())
            print(f"[+] Copied unencrypted resource: {resourceName}")
            return


        fxap_buffer = self.decrypt_file(fxap_file, self.DefaultKey)
        if not fxap_buffer:
            return

        resource_id = self.scan_for_id(fxap_buffer)

        # obtain grants payload from Resources/Grants.txt or parameter
        if grants_token is None:
            grants_path = os.path.join("Resources", "Grants.txt")
            if not os.path.exists(grants_path):
                print("No Grants.txt found; cannot decrypt resource", resourceName)
                return
            data = self.validate_key_from_file(grants_path)
        else:
            # if grants_token string is passed directly, mimic validate response
            data = {"success": True, "grants_token": grants_token}

        if not data.get("success"):
            print("Key validation failed for", resourceName)
            return

        # parse the grants token JWT-like structure (payload is second segment, base64)
        try:
            payload_part = data["grants_token"].split(".")[1]
            # padding
            payload_part += "=" * (-len(payload_part) % 4)
            payload = json.loads(base64.b64decode(payload_part).decode('utf-8'))
        except Exception as e:
            print("Failed to parse grants token payload:", e)
            return

        if str(resource_id) not in payload.get("grants", {}):
            print(f"Unauthorized resource {resourceName} (ID {resource_id})")
            return

        decrypt_key = bytes.fromhex(payload["grants"][str(resource_id)])
        grants_clk_hex = payload["grants_clk"][str(resource_id)]
        grants_clk = bytes.fromhex(grants_clk_hex)

        print(f"Decrypting: {resourceName} (ID: {resource_id})")

        files = self.get_all_files(resourcePath)
        tasks = []
        with ThreadPoolExecutor(max_workers=6) as exe:
            for file_full in files:
                if file_full.endswith(".fxap"):
                    continue
                relative = os.path.relpath(file_full, resourcePath).replace("\\", "/")
                tasks.append(exe.submit(self.decrypt_resource_file, resourcePath, relative, decrypt_key, resourceName, grants_clk))

            # wait
            for t in tasks:
                try:
                    t.result()
                except Exception as e:
                    print("Error decrypting file:", e)

    def decrypt_all_resources(self):
        resource_dirs = []
        resources_root = "Unpacked"
        if not os.path.isdir(resources_root):
            print("No Unpacked/ directory found - run the dumper/unpacker first.")
            return
        for entry in os.listdir(resources_root):
            full = os.path.join(resources_root, entry)
            if os.path.isdir(full):
                resource_dirs.append(full)
        for resource_dir in resource_dirs:
            resource_name = os.path.basename(resource_dir)
            self.decrypt_resource(resource_dir, resource_name)

    def start(self):
        print("Starting resource decryption...")
        self.decrypt_all_resources()
        print("Decryption completed!")

# =============== MAIN ===============
if __name__=="__main__":
    # Step 1: dumper (download & unpack)
    if len(sys.argv) < 2:
        link = input("Enter cfx.re link: ").strip()
    else:
        link = sys.argv[1]

    ip = get_ip_from_cfx(link)
    print("[*] Server IP:", ip)

    token = get_token()
    if not token:
        sys.exit("Token not found. Make sure FiveM is running and connected.")
    print("[*] Token:", token)

    base_url = "http://"+ip
    dumper = FiveMDumper(base_url, token, max_workers=15)
    dumper.run()

    # Step 2: decrypt unpacked resources into Output/
    decryptor = FiveMDecryptor()
    # if user passed a grants key or grants file as second argument, forward it
    if len(sys.argv) >= 3:
        decryptor.start()  # the decryptor uses Resources/Grants.txt by default
    else:
        decryptor.start()#

            # Step 3: cleanup temporary folders
        # Step 3: cleanup temporary folders
    import shutil
    for folder in ["Temp", "Unpacked", "TempCompiled", "Resources"]:
        if os.path.isdir(folder):
            try:
                shutil.rmtree(folder)
                print(f"🧹 Cleaned up {folder}/")
            except Exception as e:
                print(f"⚠️ Could not remove {folder}/: {e}")

