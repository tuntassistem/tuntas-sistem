"""
utils/auth_manager.py — Session Manager T.U.N.T.A.S
=====================================================
Menggantikan streamlit-authenticator dengan sistem yang tahan
iframe Streamlit Cloud menggunakan:

  1. Supabase Auth  — JWT management, refresh token, user store
  2. localStorage   — First-party storage, tidak terdampak SameSite cookie policy
  3. st.query_params — Bridge JS↔Python (localStorage → URL params → session_state)
"""

from __future__ import annotations

import json
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit-javascript import st_javascript
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
    """Supabase client khusus auth (anon key)."""
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
    """Membaca localStorage via URL query params parent window."""
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

                var parentSearch = window.parent.location.search;
                var parentParams = new URLSearchParams(parentSearch);
                if (parentParams.get("{_PARAM_TOKEN}")) return;

                parentParams.set("{_PARAM_TOKEN}",   data.access_token);
                parentParams.set("{_PARAM_REFRESH}",  data.refresh_token);
                parentParams.set("{_PARAM_EXPIRY}",   String(data.expires_at || 0));

                window.parent.location.search = parentParams.toString();

            }} catch (err) {{
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
    """Inject JS untuk menyimpan session ke localStorage."""
    payload = json.dumps({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "expires_at":    expires_at,
    })
    components.html(
        f"<script>localStorage.setItem({repr(_STORAGE_KEY)}, {repr(payload)});</script>",
        height=0,
        scrolling=False,
    )


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
    """Simpan Supabase session ke st.session_state."""
    user_meta = getattr(session_obj.user, "user_metadata", {}) or {}

    st.session_state["tuntas_session"] = {
        "access_token":  session_obj.access_token,
        "refresh_token": session_obj.refresh_token,
        "expires_at":    session_obj.expires_at,
        "user_id":       session_obj.user.id,
        "email":         session_obj.user.email,
        "display_name":  user_meta.get("full_name", session_obj.user.email),
    }

    st.session_state["name"]                  = user_meta.get("full_name", session_obj.user.email)
    st.session_state["username"]              = session_obj.user.email
    st.session_state["authentication_status"] = True


def _clear_session() -> None:
    """Bersihkan semua session dari session_state."""
    for key in ["tuntas_session", "name", "username", "authentication_status"]:
        st.session_state.pop(key, None)


def _session_still_valid() -> bool:
    """Cek apakah session di session_state masih valid."""
    sess = st.session_state.get("tuntas_session")
    if not sess:
        return False

    expires_at = sess.get("expires_at", 0)
    if time.time() < (expires_at - _BUFFER_SECS):
        return True

    return _do_refresh(sess["refresh_token"])


def _do_refresh(refresh_token: str) -> bool:
    """Refresh access token menggunakan refresh_token."""
    sb = _get_auth_client()
    if not sb:
        return False
    try:
        resp = sb.auth.refresh_session(refresh_token)
        if resp and resp.session:
            _save_session(resp.session)
            _js_write_storage(
                resp.session.access_token,
                resp.session.refresh_token,
                resp.session.expires_at,
            )
            return True
    except Exception:
        pass
    return False


def _restore_from_tokens(access_token: str, refresh_token: str, expires_at: int) -> bool:
    """Restore session dari token pair yang datang via query_params."""
    sb = _get_auth_client()
    if not sb:
        return False

    if time.time() < (expires_at - _BUFFER_SECS) and access_token:
        try:
            resp = sb.auth.set_session(access_token, refresh_token)
            if resp and getattr(resp, "user", None):
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

    return _do_refresh(refresh_token)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def check_session() -> bool:
    """Cek dan restore session dari semua sumber."""
    if _session_still_valid():
        return True

    qp            = st.query_params
    access_token  = qp.get(_PARAM_TOKEN,   "")
    refresh_token = qp.get(_PARAM_REFRESH, "")
    expires_at    = int(qp.get(_PARAM_EXPIRY, "0") or "0")

    if access_token and refresh_token:
        st.query_params.clear()
        if _restore_from_tokens(access_token, refresh_token, expires_at):
            return True

    if not access_token:
        _js_read_storage()

    return False


def login(email: str, password: str) -> tuple[bool, str]:
    """Login dengan email + password via Supabase Auth."""
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
    """Logout user total."""
    sb = _get_auth_client()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass

    _js_clear_storage()
    _clear_session()
    st.rerun()


def get_current_user() -> Optional[dict]:
    """Ambil info user aktif."""
    sess = st.session_state.get("tuntas_session")
    if not sess:
        return None
    return {
        "id":    sess.get("user_id"),
        "email": sess.get("email"),
        "name":  sess.get("display_name", sess.get("email")),
    }


def create_user_admin(email: str, password: str, full_name: str) -> tuple[bool, str]:
    """Buat user baru via Admin API Supabase."""
    try:
        admin_sb = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["service_role_key"],
        )
        resp = admin_sb.auth.admin.create_user({
            "email":            email,
            "password":         password,
            "email_confirm":    True,
            "user_metadata":    {"full_name": full_name},
        })
        if resp and resp.user:
            return True, f"User {email} berhasil dibuat."
        return False, "Gagal membuat user."
    except Exception as e:
        return False, str(e)
