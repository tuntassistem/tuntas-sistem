"""
utils/auth_manager.py — Session Manager T.U.N.T.A.S
=====================================================
Menggantikan streamlit-authenticator dengan sistem yang tahan
iframe Streamlit Cloud menggunakan:

  1. Supabase Auth  — JWT management, refresh token, user store
  2. localStorage   — First-party storage, tidak terdampak SameSite cookie policy
  3. st.query_params — Bridge JS↔Python (localStorage → URL params → session_state)

FLOW:
  Page Load
    → Cek session_state (in-memory, paling cepat)
    → Cek query_params  (hasil bridge dari localStorage reader JS)
    → Inject localStorage reader JS → triggers rerun via URL change
    → Validate + restore via Supabase → simpan ke session_state

  Login
    → supabase.auth.sign_in_with_password()
    → Simpan ke session_state
    → Inject JS writer → simpan ke localStorage

  Logout
    → supabase.auth.sign_out()
    → Inject JS cleaner → hapus dari localStorage
    → Bersihkan session_state

KEAMANAN:
  - Access token: short-lived JWT (default 1 jam Supabase)
  - Refresh token: long-lived, single-use, dirotasi setiap refresh
  - localStorage: same-origin scoped, tidak bisa diakses cross-site
  - Token di query_params: langsung dibersihkan setelah dibaca Python
  - Tidak ada plaintext password yang pernah disimpan

KOMPATIBILITAS:
  - Tetap set st.session_state["authentication_status"] agar
    kode existing (app.py, pages/*.py) tidak perlu banyak berubah.
  - Tetap set st.session_state["name"] untuk tampilan sidebar.
"""

from __future__ import annotations

import json
import time
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# KONSTANTA
# ─────────────────────────────────────────────────────────────────────────────
_STORAGE_KEY   = "tuntas_session_v1"   # Key localStorage
_PARAM_TOKEN   = "_tk"                 # query param: access token
_PARAM_REFRESH = "_rt"                 # query param: refresh token
_PARAM_EXPIRY  = "_exp"                # query param: expiry unix timestamp
_BUFFER_SECS   = 300                   # Refresh 5 menit sebelum expiry


# ─────────────────────────────────────────────────────────────────────────────
# SUPABASE CLIENT (untuk auth saja)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_auth_client() -> Optional[Client]:
    """
    Supabase client khusus auth (anon key).
    Dipisah dari admin client di supabase_client.py agar tidak bentrok.
    """
    try:
        return create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"],
        )
    except Exception as e:
        st.error(f"⚠️ Koneksi Supabase Auth gagal: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# JS INJECTORS — localStorage bridge
# ─────────────────────────────────────────────────────────────────────────────

def _js_read_storage() -> None:
    """
    Inject JS yang:
      1. Membaca localStorage
      2. Jika ada token, set ke URL query params parent window
      3. Streamlit mendeteksi perubahan query_params → rerun otomatis

    Dieksekusi hanya ketika session_state kosong DAN query_params kosong.
    Guard `if (params.get(...))` mencegah infinite loop.
    """
    components.html(
        f"""
        <script>
        (function() {{
            try {{
                var STORAGE_KEY = "{_STORAGE_KEY}";
                var stored = localStorage.getItem(STORAGE_KEY);
                if (!stored) return;

                var data;
                try {{ data = JSON.parse(stored); }}
                catch (e) {{
                    localStorage.removeItem(STORAGE_KEY);
                    return;
                }}

                if (!data || !data.access_token || !data.refresh_token) return;

                // Guard: jika parent URL sudah punya _tk, jangan inject ulang
                var parentSearch = window.parent.location.search;
                var parentParams = new URLSearchParams(parentSearch);
                if (parentParams.get("{_PARAM_TOKEN}")) return;

                // Set token ke URL parent → Streamlit rerun
                parentParams.set("{_PARAM_TOKEN}",   data.access_token);
                parentParams.set("{_PARAM_REFRESH}",  data.refresh_token);
                parentParams.set("{_PARAM_EXPIRY}",   String(data.expires_at || 0));

                window.parent.location.search = parentParams.toString();

            }} catch (err) {{
                // Fallback: window.parent mungkin blocked di beberapa config
                // Coba window sendiri (jika app diakses langsung, bukan via iframe)
                try {{
                    var stored2 = localStorage.getItem("{_STORAGE_KEY}");
                    if (!stored2) return;
                    var data2 = JSON.parse(stored2);
                    if (!data2 || !data2.access_token) return;

                    var params2 = new URLSearchParams(window.location.search);
                    if (params2.get("{_PARAM_TOKEN}")) return;

                    params2.set("{_PARAM_TOKEN}",   data2.access_token);
                    params2.set("{_PARAM_REFRESH}",  data2.refresh_token);
                    params2.set("{_PARAM_EXPIRY}",   String(data2.expires_at || 0));
                    window.location.search = params2.toString();
                }} catch (e2) {{ /* silent */ }}
            }}
        }})();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def _js_write_storage(access_token: str, refresh_token: str, expires_at: int) -> None:
    """Inject JS untuk menyimpan session ke localStorage dengan aman."""
    payload = json.dumps({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "expires_at":    expires_at,
    })
    
    js_code = f"""
    <script>
    (function() {{
        var KEY = {repr(_STORAGE_KEY)};
        var DATA = {repr(payload)};
        
        // 1. Tulis ke storage lokal iframe dulu
        try {{
            localStorage.setItem(KEY, DATA);
            console.log("✅ Berhasil tulis localStorage lokal");
        }} catch(e) {{ console.error(e); }}
        
        // 2. Tulis ke storage parent window (Streamlit Cloud wrapper)
        try {{
            if (window.parent && window.parent.localStorage) {{
                window.parent.localStorage.setItem(KEY, DATA);
                console.log("✅ Berhasil tulis localStorage parent");
            }}
        }} catch(e) {{ 
            console.warn("window.parent di-block oleh browser policy:", e); 
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0, scrolling=False)


def _js_clear_storage() -> None:
    """Inject JS untuk menghapus session dari localStorage."""
    components.html(
        f"<script>localStorage.removeItem({repr(_STORAGE_KEY)});</script>",
        height=0,
        scrolling=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _save_session(session_obj) -> None:
    """
    Simpan Supabase session ke st.session_state.
    Tetap set "name" dan "authentication_status" untuk kompatibilitas
    dengan kode existing di app.py dan pages/*.py.
    """
    user_meta = getattr(session_obj.user, "user_metadata", {}) or {}

    st.session_state["tuntas_session"] = {
        "access_token":  session_obj.access_token,
        "refresh_token": session_obj.refresh_token,
        "expires_at":    session_obj.expires_at,
        "user_id":       session_obj.user.id,
        "email":         session_obj.user.email,
        "display_name":  user_meta.get("full_name", session_obj.user.email),
    }

    # Kompatibilitas dengan existing code
    st.session_state["name"]                  = user_meta.get("full_name", session_obj.user.email)
    st.session_state["username"]              = session_obj.user.email
    st.session_state["authentication_status"] = True


def _clear_session() -> None:
    """Bersihkan semua session dari session_state."""
    for key in ["tuntas_session", "name", "username", "authentication_status"]:
        st.session_state.pop(key, None)


def _session_still_valid() -> bool:
    """
    Cek apakah session di session_state masih valid.
    Jika hampir expired, otomatis refresh.
    """
    sess = st.session_state.get("tuntas_session")
    if not sess:
        return False

    expires_at = sess.get("expires_at", 0)
    if time.time() < (expires_at - _BUFFER_SECS):
        return True  # Masih valid, tidak perlu apa-apa

    # Hampir / sudah expired → coba refresh
    return _do_refresh(sess["refresh_token"])


def _do_refresh(refresh_token: str) -> bool:
    """Refresh access token menggunakan refresh_token. Returns True jika berhasil."""
    sb = _get_auth_client()
    if not sb:
        return False
    try:
        resp = sb.auth.refresh_session(refresh_token)
        if resp and resp.session:
            _save_session(resp.session)
            # Update localStorage dengan token baru
            _js_write_storage(
                resp.session.access_token,
                resp.session.refresh_token,
                resp.session.expires_at,
            )
            return True
    except Exception:
        pass
    return False


def _restore_from_tokens(
    access_token: str,
    refresh_token: str,
    expires_at: int,
) -> bool:
    """
    Restore session dari token pair yang datang via query_params.
    
    Logic:
      - Jika access_token masih valid (belum expired) → set session langsung
      - Jika sudah expired → gunakan refresh_token untuk dapat token baru
    """
    sb = _get_auth_client()
    if not sb:
        return False

    # Coba set session jika access token belum expired
    if time.time() < (expires_at - _BUFFER_SECS) and access_token:
        try:
            resp = sb.auth.set_session(access_token, refresh_token)
            if resp and getattr(resp, "user", None):
                # set_session tidak selalu mengembalikan session object lengkap
                # Buat session object manual
                class _FakeSession:
                    pass
                s = _FakeSession()
                s.access_token  = access_token
                s.refresh_token = refresh_token
                s.expires_at    = expires_at
                s.user          = resp.user
                _save_session(s)
                return True
        except Exception:
            pass

    # Access token expired atau set gagal → refresh
    return _do_refresh(refresh_token)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def check_session() -> bool:
    """
    Cek dan restore session dari semua sumber yang mungkin.
    Dipanggil di app.py setiap page load sebagai ganti
    authenticator.login(location="unrendered").

    Returns:
        True  → User terautentikasi, lanjut render halaman
        False → User belum login, arahkan ke login page
    """

    # ── 1. Cek session_state (in-memory, tidak perlu network) ────────────
    if _session_still_valid():
        return True

    # ── 2. Cek query_params (hasil JS localStorage bridge) ───────────────
    qp           = st.query_params
    access_token  = qp.get(_PARAM_TOKEN,   "")
    refresh_token = qp.get(_PARAM_REFRESH, "")
    expires_at    = int(qp.get(_PARAM_EXPIRY, "0") or "0")

    if access_token and refresh_token:
        # PENTING: hapus token dari URL sebelum proses
        # agar tidak muncul di browser history dan tidak ter-reuse
        st.query_params.clear()

        if _restore_from_tokens(access_token, refresh_token, expires_at):
            return True

    # ── 3. Inject JS localStorage reader (jika params kosong) ────────────
    # JS akan set query_params → Streamlit rerun → step 2 handle
    if not access_token:
        _js_read_storage()

    return False


def login(email: str, password: str) -> tuple[bool, str]:
    """
    Login dengan email + password via Supabase Auth.

    Args:
        email    : email user (digunakan sebagai username)
        password : password plaintext (tidak disimpan, hanya dikirim sekali)

    Returns:
        (True, "Login berhasil!")     jika sukses
        (False, "<pesan error>")      jika gagal
    """
    if not email.strip() or not password:
        return False, "Email dan password wajib diisi."

    sb = _get_auth_client()
    if not sb:
        return False, "Koneksi ke server gagal. Periksa konfigurasi Supabase."

    try:
        resp = sb.auth.sign_in_with_password({
            "email":    email.strip().lower(),
            "password": password,
        })

        if resp and resp.session:
            _save_session(resp.session)
            # Simpan ke localStorage agar persist setelah refresh
            _js_write_storage(
                resp.session.access_token,
                resp.session.refresh_token,
                resp.session.expires_at,
            )
            return True, "Login berhasil!"

        return False, "Login gagal. Respons tidak valid dari server."

    except Exception as e:
        err = str(e).lower()
        if any(kw in err for kw in ["invalid", "wrong", "credentials", "email not confirmed"]):
            return False, "Email atau password salah."
        if "user not found" in err:
            return False, "Akun tidak ditemukan. Hubungi admin SPI."
        return False, f"Terjadi kesalahan: {e}"


def logout() -> None:
    """
    Logout user:
      1. Sign out dari Supabase (invalidate token di server)
      2. Hapus localStorage via JS
      3. Bersihkan session_state
    """
    sb = _get_auth_client()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass  # Tetap lanjut bersihkan lokal meski server gagal

    _js_clear_storage()
    _clear_session()


def get_current_user() -> Optional[dict]:
    """
    Ambil info user yang sedang login dari session_state.

    Returns:
        dict dengan keys: id, email, name
        None jika tidak ada session aktif
    """
    sess = st.session_state.get("tuntas_session")
    if not sess:
        return None
    return {
        "id":    sess.get("user_id"),
        "email": sess.get("email"),
        "name":  sess.get("display_name", sess.get("email")),
    }


def create_user_admin(
    email: str,
    password: str,
    full_name: str,
) -> tuple[bool, str]:
    """
    Buat user baru via Admin API Supabase.
    HANYA untuk dijalankan oleh admin SPI melalui skrip setup,
    bukan diekspos ke UI umum.

    Membutuhkan service_role_key di secrets.toml.
    """
    try:
        admin_sb = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["service_role_key"],
        )
        resp = admin_sb.auth.admin.create_user({
            "email":            email,
            "password":         password,
            "email_confirm":    True,  # Skip email verification
            "user_metadata":    {"full_name": full_name},
        })
        if resp and resp.user:
            return True, f"User {email} berhasil dibuat."
        return False, "Gagal membuat user."
    except Exception as e:
        return False, str(e)
