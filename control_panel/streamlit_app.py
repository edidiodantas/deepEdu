import base64
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = (os.getenv("CLOUD_API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")


def _admin_key() -> str:
    # Chave digitada no login; fica só na sessão do navegador, nunca em disco.
    return st.session_state.get("admin_key", "")


def _headers():
    return {"X-Admin-Api-Key": _admin_key()}


def _post(path: str, params: dict):
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, params=params, headers=_headers(), timeout=20)
    return resp.status_code, resp.text


def _get(path: str, params: dict | None = None):
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, params=params or {}, headers=_headers(), timeout=20)
    return resp.status_code, resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text


def _check_admin_key(key: str) -> tuple[bool, str]:
    """A API decide se a chave vale (mesma ADMIN_API_KEY do .env da API)."""
    try:
        resp = requests.get(
            f"{BASE_URL}/admin/materials", headers={"X-Admin-Api-Key": key}, timeout=10
        )
    except requests.RequestException as exc:
        return False, f"API inacessível: {exc}"
    if resp.status_code == 200:
        return True, ""
    if resp.status_code == 403:
        return False, "Chave de administrador incorreta."
    return False, f"Erro {resp.status_code}: {resp.text}"


def _render_fontes(data: dict):
    """Só para o administrador: de onde veio a resposta."""
    sources = data.get("sources") or []
    min_score = data.get("min_score")
    titulo = f"📄 Trechos usados ({len(sources)})"
    if data.get("abstained"):
        titulo = f"📄 Trechos encontrados — relevância insuficiente ({len(sources)})"
    with st.expander(titulo, expanded=True):
        if data.get("abstained"):
            st.warning(
                f"O melhor trecho teve relevância {data.get('max_score', 0):.2f}, abaixo do mínimo "
                f"{min_score:.2f} (RETRIEVAL_MIN_SCORE). Por isso o tutor não respondeu."
            )
        if not sources:
            st.write("Nenhum trecho encontrado. Há materiais indexados?")
        for i, src in enumerate(sources, 1):
            pagina = f", pág. {src['page']}" if src.get("page") else ""
            st.markdown(f"**{i}. {src.get('file', '?')}{pagina}** — relevância {src.get('score', 0):.2f}")
            st.caption(src.get("snippet", ""))
        st.caption("Relevância de 0 a 1. Trilha completa: aba ECA / Auditoria, campo Código da resposta.")


def _render_pergunta(is_admin: bool):
    st.subheader("Pergunte ao tutor")
    st.caption("Escreva sua dúvida de matemática. O tutor responde com base nos materiais da escola.")
    student_id = st.text_input("Seu código de aluno", value="aluno-local")
    question = st.text_area("Sua pergunta")
    if st.button("Perguntar", type="primary"):
        if not question.strip():
            st.warning("Escreva uma pergunta.")
            return
        with st.spinner("Pensando..."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/perguntar",
                    json={"student_id": student_id.strip() or "aluno-local", "question": question},
                    timeout=300,
                )
            except requests.RequestException as exc:
                st.error(f"Tutor indisponível no momento: {exc}" if is_admin else "Tutor indisponível no momento.")
                return
        if resp.headers.get("content-type", "").startswith("application/json"):
            data = resp.json()
        else:
            data = {"detail": resp.text}
        if resp.status_code == 200:
            st.write(data.get("answer", ""))
            st.caption(f"Código da resposta: {data.get('correlation_id', '')}")
            if is_admin:
                _render_fontes(data)
        else:
            st.error(f"Erro {resp.status_code}: {data}" if is_admin else "Não foi possível responder agora.")


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
FAVICON_PATH = os.path.join(ASSETS_DIR, "favicon.png")


@st.cache_data
def _logo_data_uri() -> str:
    if not os.path.exists(LOGO_PATH):
        return ""
    with open(LOGO_PATH, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


st.set_page_config(
    page_title="DeepEdu",
    page_icon=FAVICON_PATH if os.path.exists(FAVICON_PATH) else None,
    layout="wide",
)


def _header(subtitle: str):
    """Logo + nome com degradê suave (azul do tema) e subtítulo leve em cinza."""
    uri = _logo_data_uri()
    logo = f'<img src="{uri}" alt="" style="height: 96px; width: 96px;">' if uri else ""
    st.markdown(
        f"""
<div style="display: flex; align-items: center; gap: 1rem; margin: 0 0 1.5rem 0;">
  {logo}
  <div>
  <div style="display: inline-block; font-size: 2.8rem; font-weight: 800; line-height: 1.1; letter-spacing: -0.02em;
              background: linear-gradient(90deg, #1F4E9E 0%, #3B7DD8 100%);
              -webkit-background-clip: text; background-clip: text;
              -webkit-text-fill-color: transparent; color: #1F4E9E;">DeepEdu</div>
  <div style="font-size: 1.25rem; font-weight: 300; color: #5B6575; margin-top: 0.2rem;">{subtitle}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### Administrador")
    if st.session_state.get("admin_key"):
        st.success("Modo administrador")
        if st.button("Sair"):
            st.session_state.pop("admin_key", None)
            st.rerun()
    else:
        with st.form("login_admin", clear_on_submit=True):
            typed = st.text_input("Chave de administrador", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                ok, msg = _check_admin_key(typed.strip())
                if ok:
                    st.session_state["admin_key"] = typed.strip()
                    st.rerun()
                else:
                    st.error(msg)

IS_ADMIN = bool(st.session_state.get("admin_key"))

if not IS_ADMIN:
    # Aluno: só a pergunta. As outras abas nem são desenhadas.
    _header("Tutor de Matemática")
    _render_pergunta(is_admin=False)
    st.stop()

_header("Painel do administrador")

tab_inicio, tab_q, tab_mat, tab1, tab2, tab3 = st.tabs(
    ["Início", "Pergunta", "Materiais", "Aluno", "Escola", "ECA / Auditoria"]
)

with tab_inicio:
    st.subheader("Como usar este painel")
    st.markdown(
        """
| Aba | Para que serve |
|---|---|
| **Pergunta** | Testar o tutor como se fosse um aluno. |
| **Materiais** | Enviar, listar e remover os PDFs/TXT/MD do conteúdo e **reindexar**. |
| **Aluno** | Assinatura individual: ativar manualmente ou gerar link de pagamento. |
| **Escola** | Plano escola: criar escola, vincular aluno, pagamento e ativação. |
| **ECA / Auditoria** | Matrícula com consentimento dos responsáveis, logs de auditoria, exportar CSV e incidentes. |

**Primeiro uso:** 1) envie os materiais na aba *Materiais* → 2) clique em *Reindexar* → 3) teste na aba *Pergunta*.

Os alunos que abrem o painel sem entrar como administrador veem **somente** a tela de pergunta.
"""
    )
    st.divider()
    st.subheader("Status do sistema")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=10).json()
        st.success("API ligada")
        st.write(f"Modelo de linguagem: `{health.get('llm_model', '?')}`")
        rt = health.get("llm_runtime") or {}
        if rt.get("status") == "carregado":
            st.write(f"Processamento: **{rt.get('device_label')}** ({rt.get('dtype_name')})")
            if rt.get("reason") and rt.get("device_map") == "cpu":
                st.caption(f"Rodando no processador porque: {rt['reason']}")
        else:
            st.write(f"Processamento: {rt.get('status', '?')}")
    except Exception as exc:
        st.error(f"API desligada ou inacessível: {exc}")
    try:
        code, data = _get("/admin/materials")
        if code == 200 and isinstance(data, dict):
            st.write(f"Materiais em data/materials: **{len(data.get('items', []))}**")
    except requests.RequestException:
        pass
    st.caption(f"Endereço da API: {BASE_URL}")

with tab_q:
    _render_pergunta(is_admin=True)

with tab_mat:
    st.subheader("Materiais didáticos (RAG)")
    st.caption("Envie PDFs/TXT/MD e clique em Reindexar. O tutor passa a usar o índice novo na próxima pergunta.")

    uploads = st.file_uploader(
        "Enviar arquivos", type=["pdf", "txt", "md"], accept_multiple_files=True
    )
    if uploads and st.button("Enviar para data/materials", type="primary"):
        try:
            resp = requests.post(
                f"{BASE_URL}/admin/materials",
                files=[("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in uploads],
                headers=_headers(),
                timeout=120,
            )
        except requests.RequestException as exc:
            st.error(f"API inacessível: {exc}")
        else:
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            if resp.status_code == 200:
                for item in data.get("saved", []):
                    st.success(f"{item['name']} enviado ({item['bytes'] / 1024:.1f} KB)")
                for item in data.get("errors", []):
                    st.error(f"{item['name']}: {item['error']}")
                if data.get("saved"):
                    st.info("Agora clique em Reindexar para o tutor usar os arquivos novos.")
            else:
                st.error(f"Erro {resp.status_code}: {data or resp.text}")

    st.divider()
    try:
        code, data = _get("/admin/materials")
    except requests.RequestException as exc:
        code, data = 0, str(exc)
    if code == 200 and isinstance(data, dict):
        items = data.get("items", [])
        st.write(f"{len(items)} arquivo(s) em data/materials")
        if items:
            st.dataframe(
                [{"arquivo": i["name"], "KB": round(i["bytes"] / 1024, 1), "modificado": i["modified_at"]} for i in items],
                use_container_width=True,
            )
            to_delete = st.selectbox("Remover arquivo", [i["name"] for i in items])
            if st.button("Remover"):
                resp = requests.delete(
                    f"{BASE_URL}/admin/materials/{requests.utils.quote(to_delete)}",
                    headers=_headers(),
                    timeout=20,
                )
                if resp.status_code == 200:
                    st.success(f"{to_delete} removido. Reindexe para tirar do tutor.")
                else:
                    st.error(f"Erro {resp.status_code}: {resp.text}")
    else:
        st.error(f"Não foi possível listar materiais ({code}): {data}")

    st.divider()
    if st.button("Reindexar", type="primary"):
        with st.spinner("Indexando... (pode levar alguns minutos)"):
            try:
                resp = requests.post(
                    f"{BASE_URL}/admin/index/rebuild", headers=_headers(), timeout=1800
                )
            except requests.RequestException as exc:
                st.error(f"API inacessível: {exc}")
            else:
                if resp.status_code == 200:
                    st.success(f"Indexação concluída: {resp.json().get('chunks')} trechos.")
                else:
                    st.error(f"Erro {resp.status_code}: {resp.text}")

with tab1:
    st.subheader("Assinatura individual")
    st.caption("Ative a assinatura de um aluno manualmente ou gere o link de pagamento dele.")
    phone = st.text_input("Telefone do aluno (E.164)", value="+5511999999999")
    paid_until = st.text_input(
        "paid_until (ISO, opcional — vazio = +BILLING_PLAN_DAYS)",
        value="",
        key="student_paid_until",
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ativar assinatura (manual)"):
            params = {"phone": phone}
            if paid_until.strip():
                params["paid_until_iso"] = paid_until.strip()
            code, body = _post("/admin/billing/activate", params)
            st.code(f"{code}\n{body}")
    with col2:
        if st.button("Gerar checkout do aluno"):
            code, body = _post(
                "/admin/billing/checkout",
                {"phone": phone, "name": f"Aluno {phone}", "billing_type": "UNDEFINED"},
            )
            st.code(f"{code}\n{body}")

with tab2:
    st.subheader("Plano Escola")
    st.caption("Cadastre a escola, vincule alunos a ela e controle o plano/pagamento da escola.")
    school_id = st.text_input("ID da escola", value="escola-alpha")
    school_name = st.text_input("Nome da escola", value="Escola Alpha")
    school_phone = st.text_input("Telefone do aluno para vincular", value="+5511888888888")
    school_paid_until = st.text_input(
        "paid_until escola (ISO, opcional)",
        value="",
        key="school_paid_until",
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Criar escola"):
            code, body = _post("/admin/schools", {"school_id": school_id, "name": school_name})
            st.code(f"{code}\n{body}")
    with c2:
        if st.button("Vincular aluno"):
            code, body = _post(
                "/admin/schools/assign-student",
                {"phone": school_phone, "school_id": school_id},
            )
            st.code(f"{code}\n{body}")
    with c3:
        if st.button("Checkout escola"):
            code, body = _post(
                "/admin/schools/checkout",
                {"school_id": school_id, "school_name": school_name},
            )
            st.code(f"{code}\n{body}")
    with c4:
        if st.button("Ativar plano escola (manual)"):
            params = {"school_id": school_id}
            if school_paid_until.strip():
                params["paid_until_iso"] = school_paid_until.strip()
            code, body = _post("/admin/schools/activate", params)
            st.code(f"{code}\n{body}")

with tab3:
    st.subheader("Matrícula ECA (Lei 15.211/2025)")
    st.caption("Cadastre o aluno com o consentimento dos responsáveis, consulte a trilha de auditoria e registre incidentes.")
    enroll_phone = st.text_input("Telefone do aluno", value="+5511999999999", key="enroll_phone")
    enroll_school = st.text_input("ID da escola", value="escola-alpha", key="enroll_school")
    enroll_code = st.text_input("Código do aluno", value="MAT2026A")
    consent_ref = st.text_input("Referência consentimento parental", value="RESP-001")
    if st.button("Cadastrar aluno (enrollment)"):
        code, body = _post(
            "/admin/students/enroll",
            {
                "phone": enroll_phone,
                "school_id": enroll_school,
                "student_code": enroll_code,
                "parental_consent_ref": consent_ref,
            },
        )
        st.code(f"{code}\n{body}")

    st.divider()
    st.subheader("Logs de auditoria")
    st.caption(
        "Sem código: os eventos mais recentes primeiro. Com o código de uma resposta: "
        "só a trilha daquela pergunta, em ordem."
    )
    corr_filter = st.text_input("Código da resposta (opcional)", value="")
    action_filter = st.text_input("Filtrar por action (opcional)", value="")
    limit = st.number_input("Limite", min_value=10, max_value=1000, value=100, step=10)
    if st.button("Carregar logs"):
        params = {"limit": int(limit)}
        if action_filter.strip():
            params["action"] = action_filter.strip()
        if corr_filter.strip():
            params["correlation_id"] = corr_filter.strip()
        code, data = _get("/admin/audit/logs", params)
        if code == 200 and isinstance(data, dict):
            items = data.get("items", [])
            if corr_filter.strip():
                st.write(f"{len(items)} eventos da resposta {corr_filter.strip()}")
            else:
                st.write(f"{len(items)} eventos mais recentes")
            # Colunas mais úteis primeiro: o que aconteceu, quando e com que resultado.
            ordem = ["timestamp", "action", "outcome", "actor_type", "resource", "metadata",
                     "correlation_id", "actor_id", "session_id", "event_id", "langsmith_run_id"]
            linhas = [{k: (str(i.get(k)) if k == "metadata" else i.get(k)) for k in ordem} for i in items]
            st.dataframe(linhas, use_container_width=True)
        else:
            st.error(f"Erro {code}: {data}")

    if st.button("Exportar CSV de auditoria"):
        resp = requests.get(
            f"{BASE_URL}/admin/audit/export",
            headers=_headers(),
            timeout=30,
        )
        if resp.status_code == 200:
            st.download_button(
                "Baixar audit_export.csv",
                data=resp.text,
                file_name="audit_export.csv",
                mime="text/csv",
            )
        else:
            st.error(f"Erro {resp.status_code}: {resp.text}")

    st.divider()
    st.subheader("Incidentes")
    severity = st.selectbox("Severidade", ["low", "medium", "high", "critical"])
    description = st.text_area("Descrição do incidente")
    action_taken = st.text_input("Ação tomada", value="")
    if st.button("Registrar incidente"):
        code, body = _post(
            "/admin/incidents",
            {"severity": severity, "description": description, "action_taken": action_taken},
        )
        st.code(f"{code}\n{body}")
