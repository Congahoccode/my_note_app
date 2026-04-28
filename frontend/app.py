import base64
import html
import json

import streamlit as st
import requests

# ─────────────────────────────────────────────
# Config — đọc từ .streamlit/secrets.toml
# ─────────────────────────────────────────────
BACKEND_URL = st.secrets["backend"]["url"]
GOOGLE_LOGIN_URL = f"{BACKEND_URL}/auth/google/login"

# ─────────────────────────────────────────────
# Icon / ảnh custom cho giao diện
# Muốn đổi icon sau này thì chỉ cần thay URL ở đây.
# ─────────────────────────────────────────────
NEW_NOTE_ICON_URL = "https://w7.pngwing.com/pngs/844/516/png-transparent-continuous-integration-gitlab-circleci-github-ci-cd-github-first-aid-nodejs-black-and-white-thumbnail.png"
APP_LOGO_URL = "https://i.pinimg.com/1200x/5f/e6/d6/5fe6d669f7714ad361ee4e5365c04fca.jpg"
EDIT_ICON_URL = "https://i.pinimg.com/736x/82/55/ec/8255ecfa6320b44ac4114171b88bb290.jpg"
DELETE_ICON_URL = "https://i.pinimg.com/736x/ee/6f/c1/ee6fc12ff6c5e192e66b4cdab0700a55.jpg"

st.set_page_config(page_title="MyNoteApp", page_icon="📝", layout="wide")


# ─────────────────────────────────────────────
# CSS giao diện
# ─────────────────────────────────────────────
def apply_custom_css():
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #070b12;
                --card-bg: rgba(17, 24, 39, 0.78);
                --card-bg-soft: rgba(21, 27, 42, 0.86);
                --border: rgba(148, 163, 184, 0.22);
                --text-muted: #9ca3af;
                --primary: #ef4444;
                --primary-hover: #dc2626;
            }

            /* BACKGROUND CHÍNH: đổi nền ở đây */
            .stApp {
                background:
                    radial-gradient(circle at 12% 8%, rgba(239, 68, 68, 0.12), transparent 28%),
                    radial-gradient(circle at 88% 12%, rgba(59, 130, 246, 0.12), transparent 30%),
                    radial-gradient(circle at 52% 95%, rgba(139, 92, 246, 0.10), transparent 32%),
                    linear-gradient(135deg, #070b12 0%, #0b1020 45%, #070b12 100%);
            }

            .block-container {
                padding-top: 3rem;
                padding-bottom: 3rem;
                max-width: 1500px;
            }

            h1, h2, h3 {
                letter-spacing: -0.035em;
            }

            /* Header */
            .app-title-row {
                display: flex;
                align-items: center;
                gap: 14px;
            }

            .app-title-row h1 {
                margin: 0;
                font-size: 2.35rem;
                line-height: 1.1;
            }

            .app-subtitle {
                color: var(--text-muted);
                margin-top: 8px;
                font-size: 0.96rem;
            }

            .user-email-box {
                height: 42px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                color: #cbd5e1;
                font-size: 0.88rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                padding-top: 4px;
            }

            .profile-card {
                height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: 0;
            }

            .profile-avatar {
                width: 40px;
                height: 40px;
                border-radius: 999px;
                object-fit: cover;
                border: 2px solid rgba(255, 255, 255, 0.30);
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
            }

            .profile-avatar-fallback {
                width: 40px;
                height: 40px;
                border-radius: 999px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #ef4444, #8b5cf6);
                color: white;
                font-weight: 800;
                border: 2px solid rgba(255, 255, 255, 0.30);
            }

            .st-key-logout_btn button {
                min-height: 34px;
                width: 104px;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 0.84rem;
                font-weight: 650;
            }

            /* Login Google */
            .google-oauth-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                width: 100%;
                min-height: 44px;
                padding: 0 16px;
                border-radius: 10px;
                border: 1px solid rgba(148, 163, 184, 0.35);
                background: #111827;
                color: #f9fafb !important;
                font-weight: 650;
                text-decoration: none !important;
                transition: all 0.15s ease;
            }

            .google-oauth-btn:hover {
                border-color: rgba(255, 255, 255, 0.52);
                background: #172033;
                transform: translateY(-1px);
            }

            .google-logo-wrap {
                width: 22px;
                height: 22px;
                border-radius: 999px;
                background: white;
                display: flex;
                align-items: center;
                justify-content: center;
                flex: 0 0 22px;
            }

            .google-logo-wrap svg {
                width: 16px;
                height: 16px;
            }

            /* Form tạo ghi chú */
            div[data-testid="stForm"] {
                border: 1px solid var(--border);
                background: linear-gradient(180deg, rgba(17, 24, 39, 0.90), rgba(10, 15, 26, 0.92));
                border-radius: 20px;
                padding: 24px 24px 20px 24px;
                box-shadow: 0 22px 60px rgba(0, 0, 0, 0.26);
                backdrop-filter: blur(12px);
            }

            div[data-testid="stTextInput"] input,
            div[data-testid="stTextArea"] textarea {
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.20);
                background-color: rgba(31, 36, 48, 0.92);
            }

            div[data-testid="stTextInput"] input:focus,
            div[data-testid="stTextArea"] textarea:focus {
                border-color: rgba(239, 68, 68, 0.72);
                box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.22);
            }

            .form-heading {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 12px 0 2px 0;
            }

            .form-heading-icon {
                width: 34px;
                height: 34px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(239, 68, 68, 0.14);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.2);
                font-size: 18px;
            }

            .form-subtitle {
                color: var(--text-muted);
                margin: 0 0 16px 44px;
                font-size: 0.92rem;
            }

            /* Card ghi chú */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(17, 24, 39, 0.42);
                border-radius: 16px;
                backdrop-filter: blur(8px);
            }

            /* Logo app */
            .app-logo-img {
                width: 52px;
                height: 52px;
                border-radius: 16px;
                object-fit: cover;
                border: 1px solid rgba(255, 255, 255, 0.18);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
            }

            .login-brand-row {
                display: flex;
                align-items: center;
                gap: 14px;
                margin-bottom: 4px;
            }

            .login-brand-row h1 {
                margin: 0;
                font-size: 2.4rem;
            }

            /* Nút hành động có icon ảnh */
            .st-key-new_note_btn button,
            div[class*="st-key-edit_"] button,
            div[class*="st-key-del_"] button {
                border-radius: 12px;
                min-height: 42px;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 9px;
            }

            .st-key-new_note_btn button::before,
            div[class*="st-key-edit_"] button::before,
            div[class*="st-key-del_"] button::before {
                content: "";
                width: 22px;
                height: 22px;
                border-radius: 7px;
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                flex: 0 0 22px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.22);
            }

            .st-key-new_note_btn button::before {
                background-image: url("https://i.pinimg.com/736x/fa/8f/bb/fa8fbb1367b3bd7bcd41dfda08314d86.jpg");
            }

            div[class*="st-key-edit_"] button::before {
                background-image: url("https://i.pinimg.com/1200x/34/4a/4e/344a4e0baa73b69d49fcc0fcf47d8361.jpg");
            }

            div[class*="st-key-del_"] button::before {
                background-image: url("https://i.pinimg.com/736x/cf/f3/84/cff38431bdc4bbbf322aaeab58f47471.jpg");
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()


# ─────────────────────────────────────────────
# Session state khởi tạo
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "id_token": None,
        "user_email": None,
        "user_name": None,
        "user_photo_url": None,
        "editing_note": None,
        "show_form": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session()


# ─────────────────────────────────────────────
# User info từ Firebase / Google ID token
# Dùng để hiển thị avatar; không dùng để xác thực bảo mật.
# ─────────────────────────────────────────────
def decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def save_user_session(token: str, fallback_email: str | None = None):
    payload = decode_jwt_payload(token)
    email = payload.get("email") or fallback_email

    st.session_state.id_token = token
    st.session_state.user_email = email
    st.session_state.user_name = payload.get("name") or email
    st.session_state.user_photo_url = payload.get("picture")


def clear_user_session():
    for key in ["id_token", "user_email", "user_name", "user_photo_url", "editing_note"]:
        st.session_state[key] = None
    st.session_state.show_form = False


# ─────────────────────────────────────────────
# Xử lý Google OAuth callback
# Sau khi Google xác thực xong, backend redirect về:
#   http://localhost:8501?token=xxx&email=yyy
# hoặc nếu lỗi: ?google_error=...
# ─────────────────────────────────────────────
def handle_google_callback():
    params = st.query_params

    if "google_error" in params:
        st.error(f"❌ Đăng nhập Google thất bại: `{params['google_error']}`")
        st.query_params.clear()
        return

    if "token" in params and "email" in params and st.session_state.id_token is None:
        save_user_session(params["token"], params["email"])
        st.query_params.clear()  # Xóa token khỏi URL
        st.rerun()


handle_google_callback()


# ─────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────
def auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.id_token}"}


def api_get(path: str):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", headers=auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối: {e}")
        return None


def api_post(path: str, data: dict):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=data, headers=auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        st.error(f"Lỗi: {r.json().get('detail', 'Lỗi không xác định')}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối: {e}")
        return None


def api_put(path: str, data: dict):
    try:
        r = requests.put(f"{BACKEND_URL}{path}", json=data, headers=auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        st.error(f"Lỗi: {r.json().get('detail', 'Lỗi không xác định')}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối: {e}")
        return None


def api_delete(path: str):
    try:
        r = requests.delete(f"{BACKEND_URL}{path}", headers=auth_headers(), timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối: {e}")
        return False


# ─────────────────────────────────────────────
# Component nhỏ
# ─────────────────────────────────────────────
def google_logo_svg() -> str:
    return """
    <svg viewBox="0 0 48 48" aria-hidden="true">
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.5 24.5c0-1.64-.15-3.22-.43-4.74H24v8.99h12.62c-.54 2.91-2.19 5.38-4.66 7.04l7.18 5.57C43.34 37.49 46.5 31.78 46.5 24.5z"/>
        <path fill="#FBBC05" d="M10.54 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.93 16.46 0 20.12 0 24s.93 7.54 2.56 10.78l7.98-6.19z"/>
        <path fill="#34A853" d="M24 48c6.47 0 11.9-2.13 15.87-5.82l-7.18-5.57c-1.99 1.33-4.54 2.12-8.69 2.12-6.26 0-11.57-4.22-13.46-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>
    """


def render_google_button():
    safe_url = html.escape(GOOGLE_LOGIN_URL, quote=True)
    st.markdown(
        f"""
        <a class="google-oauth-btn" href="{safe_url}" target="_self">
            <span class="google-logo-wrap">{google_logo_svg()}</span>
            <span>Đăng nhập bằng Google</span>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_user_profile():
    photo_url = st.session_state.user_photo_url

    if photo_url:
        avatar_html = f'<img class="profile-avatar" src="{html.escape(photo_url, quote=True)}" alt="Google avatar">'
    else:
        first_letter = (st.session_state.user_email or "U")[:1].upper()
        avatar_html = f'<div class="profile-avatar-fallback">{html.escape(first_letter)}</div>'

    st.markdown(
        f"""
        <div class="profile-card">
            {avatar_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Trang đăng nhập
# ─────────────────────────────────────────────
def render_login():
    st.markdown(
        f"""
        <div class="login-brand-row">
            <img class="app-logo-img" src="{html.escape(APP_LOGO_URL, quote=True)}" alt="MyNoteApp logo">
            <h1>MyNoteApp</h1>
        </div>
        <div class="app-subtitle">Quản lý ghi chú cá nhân - Lab 2</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    with col_center:
        st.subheader("🔑 Đăng nhập")

        # ── Email / Password ──────────────────
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="example@gmail.com")
            password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(
                "Đăng nhập bằng Email", type="primary", use_container_width=True
            )

        if submitted:
            if not email or not password:
                st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
            else:
                with st.spinner("Đang đăng nhập..."):
                    try:
                        r = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"email": email, "password": password},
                            timeout=10,
                        )
                        if r.status_code == 200:
                            data = r.json()
                            save_user_session(data["id_token"], data.get("email"))
                            st.rerun()
                        else:
                            st.error(f"❌ {r.json().get('detail', 'Đăng nhập thất bại')}")
                    except Exception as e:
                        st.error(f"Không thể kết nối tới server: {e}")

        # ── Google OAuth ──────────────────────
        st.divider()
        render_google_button()
        st.divider()
        st.caption("Chưa có tài khoản? Vui lòng tạo tài khoản trên Firebase Console.")


# ─────────────────────────────────────────────
# Form tạo / chỉnh sửa ghi chú
# ─────────────────────────────────────────────
def render_note_form():
    is_edit = st.session_state.editing_note is not None
    note = st.session_state.editing_note or {}

    icon_url = EDIT_ICON_URL if is_edit else NEW_NOTE_ICON_URL
    title_text = "Chỉnh sửa ghi chú" if is_edit else "Tạo ghi chú mới"
    subtitle = "Cập nhật nội dung ghi chú hiện có." if is_edit else "Ghi nhanh ý tưởng, việc cần làm hoặc tài liệu học tập của bạn."

    st.markdown(
        f"""
        <div class="form-heading">
            <div class="form-heading-icon" style="padding: 0; overflow: hidden;">
                <img src="{html.escape(icon_url, quote=True)}" style="width: 100%; height: 100%; object-fit: cover;" alt="note form icon">
            </div>
            <h2 style="margin: 0; font-size: 1.65rem;">{title_text}</h2>
        </div>
        <p class="form-subtitle">{subtitle}</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("note_form", clear_on_submit=True):
        title = st.text_input(
            "Tiêu đề",
            value=note.get("title", ""),
            max_chars=100,
            placeholder="VD: Kế hoạch ôn tập Cấu trúc dữ liệu",
        )
        content = st.text_area(
            "Nội dung",
            value=note.get("content", ""),
            height=210,
            placeholder="Nhập nội dung ghi chú...",
        )
        tags_input = st.text_input(
            "Tags",
            value=", ".join(note.get("tags", [])),
            placeholder="hoc_tap, lab2, quan_trong",
            help="Phân cách các tag bằng dấu phẩy.",
        )
        col_save, col_cancel, col_empty = st.columns([1.1, 1.1, 4])
        with col_save:
            submitted = st.form_submit_button("Lưu ghi chú", type="primary", use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("Hủy", use_container_width=True)

    if submitted:
        if not title.strip():
            st.warning("Tiêu đề không được để trống.")
            return
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        payload = {"title": title.strip(), "content": content.strip(), "tags": tags}

        if is_edit:
            result = api_put(f"/notes/{note['id']}", payload)
            if result:
                st.success("Đã cập nhật ghi chú.")
                st.session_state.editing_note = None
                st.session_state.show_form = False
                st.rerun()
        else:
            result = api_post("/notes", payload)
            if result:
                st.success("Đã tạo ghi chú mới.")
                st.session_state.show_form = False
                st.rerun()

    if cancelled:
        st.session_state.editing_note = None
        st.session_state.show_form = False
        st.rerun()


# ─────────────────────────────────────────────
# Danh sách ghi chú
# ─────────────────────────────────────────────
def render_notes_list():
    notes = api_get("/notes")
    if notes is None:
        return

    if not notes:
        st.info("📭 Bạn chưa có ghi chú nào. Hãy tạo ghi chú đầu tiên!")
        return

    st.caption(f"Tổng cộng {len(notes)} ghi chú")

    for note in notes:
        with st.container(border=True):
            col_title, col_actions = st.columns([5, 1])

            with col_title:
                st.markdown(f"### {note['title']}")
                st.write(note["content"])
                if note.get("tags"):
                    st.markdown("  ".join([f"`{tag}`" for tag in note["tags"]]))
                created = note.get("created_at", "")[:10]
                updated = note.get("updated_at", "")[:10]
                st.caption(f"🕒 Tạo: {created}  |  Cập nhật: {updated}")

            with col_actions:
                if st.button("Chỉnh sửa", key=f"edit_{note['id']}", help="Chỉnh sửa", use_container_width=True):
                    st.session_state.editing_note = note
                    st.session_state.show_form = True
                    st.rerun()
                if st.button("Xóa ghi chú", key=f"del_{note['id']}", help="Xóa ghi chú", use_container_width=True):
                    if api_delete(f"/notes/{note['id']}"):
                        st.success("Đã xóa ghi chú.")
                        st.rerun()


# ─────────────────────────────────────────────
# Trang chính (sau khi đăng nhập)
# ─────────────────────────────────────────────
def render_main():
    col_title, col_email, col_avatar, col_logout = st.columns([5.5, 2.1, 0.45, 0.85], vertical_alignment="center")

    with col_title:
        st.markdown(
            f"""
            <div class="app-title-row">
                <img class="app-logo-img" src="{html.escape(APP_LOGO_URL, quote=True)}" alt="MyNoteApp logo">
                <h1>MyNoteApp</h1>
            </div>
            <div class="app-subtitle">Không gian ghi chú cá nhân, học tập và công việc.</div>
            """,
            unsafe_allow_html=True,
        )

    with col_email:
        email = html.escape(st.session_state.user_email or "")
        st.markdown(f'<div class="user-email-box">{email}</div>', unsafe_allow_html=True)

    with col_avatar:
        render_user_profile()

    with col_logout:
        if st.button("Đăng xuất", key="logout_btn"):
            clear_user_session()
            st.rerun()

    st.divider()

    if not st.session_state.show_form:
        if st.button("Tạo ghi chú mới", type="primary", key="new_note_btn"):
            st.session_state.show_form = True
            st.session_state.editing_note = None
            st.rerun()

    if st.session_state.show_form:
        render_note_form()
        st.divider()

    st.subheader("📋 Danh sách ghi chú")
    render_notes_list()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if st.session_state.id_token is None:
    render_login()
else:
    render_main()
