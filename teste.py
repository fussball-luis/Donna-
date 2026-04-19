
from flask import Flask, render_template, request, redirect, session, url_for 
import sqlite3
 
app = Flask(__name__)
app.secret_key = "donna_secret_key"
 
# ---------------- BANCO ----------------
def conectar():
    return sqlite3.connect("banco.db")
 
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        nome TEXT,
        email TEXT PRIMARY KEY,
        senha TEXT,
        tipo TEXT
    )
    """)
 
    # garante que o personal exista
    cursor.execute("SELECT * FROM usuarios WHERE email=?", ("elissteglich@hotmail.com",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (email, senha, tipo) VALUES (?, ?, ?)",
            ("elissteglich@hotmail.com", "VithorLuis2012", "profissional")
        )
 
    conn.commit()
    conn.close()
 
criar_banco()
 
# criar personal padrão
def criar_personal():
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("personal@fit.com",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (?, ?, ?, ?)
        """, ("Personal", "personal@fit.com", "1234", "profissional"))
 
    conn.commit()
    conn.close()
 
criar_personal()
 
dias_semana = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira"
]
 
horarios_base = [
    "06:00 - 07:00",
    "07:00 - 08:00",
    "08:00 - 09:00",
    "09:00 - 10:00",
    "11:30 - 12:30",
    "17:30 - 18:30",
    "18:30 - 19:30",
    "19:30 - 20:30"
]
 
agenda = {}
 
def gerar_horarios(dia):
    horarios = horarios_base.copy()
 
    if dia in ["Terça-feira", "Quinta-feira"]:
        horarios.remove("11:30 - 12:30")
 
    if dia == "Sexta-feira":
        horarios = [h for h in horarios if h < "17:30"]
 
    return [{"horario": h, "vagas": 3, "alunas": []} for h in horarios]
 
# inicializar agenda
for dia in dias_semana:
    agenda[dia] = gerar_horarios(dia)
 
@app.route("/", methods=["GET", "POST"])
def login():
 
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
 
        conn = conectar()
        cursor = conn.cursor()
 
        cursor.execute("SELECT tipo FROM usuarios WHERE email=? AND senha=?", (email, senha))
        user = cursor.fetchone()
        conn.close()
 
        if user:
            session["usuario"] = {
                "email": email,
                "tipo": user[0]
            }
            return redirect(url_for("mostrar_agenda"))
 
        return "<h2>Login inválido</h2><a href='/'>Voltar</a>"
 
    return """
    <html>
    <head>
    <style>
    body {
        font-family: Arial;
        background-color: #1F2E2E;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
    }
    .box {
        background: rgba(255, 255, 255, 0.0);
        padding:30px;
        border-radius:15px;
        box-shadow:0 5px 15px rgba(0,0,0,0.1);
        text-align:center;
    }
    .titulo {
        font-size:40px;
        color:#6EC1E4;
        margin-bottom:20px;
    }
    input {
        width:90%;
        padding:10px;
        margin:10px;
        border-radius:8px;
        border:1px solid #ccc;
    }
    button {
        width:90%;
        padding:10px;
        margin:10px;
        background:#A4DDED;
        border:none;
        border-radius:8px;
        cursor:pointer;
    }
    </style>
    </head>
    <body>
        <div class="box">
            <img src="/static/Donna.png" width="200">
            <form method="post">
                <input name="email" placeholder="Email" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button>Entrar</button>
            </form>
            <a href="/cadastro">Não tem conta? Criar conta</a>
        </div>
    </body>
    </html>
    """
 
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
 
        conn = conectar()
        cursor = conn.cursor()
 
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha, "aluna")
            )
            conn.commit()
        except:
            return "<h2>Email já cadastrado</h2><a href='/cadastro'>Voltar</a>"
 
        conn.close()
        return redirect("/")
 
    return """
<html>
<head>
<style>
body {
    font-family: Arial;
    background-color: #1F2E2E;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}
.box {
    background: rgba(255, 255, 255, 0.00);
    padding:30px;
    border-radius:15px;
    box-shadow:0 5px 15px rgba(0,0,0,0.1);
    text-align:center;
}
.titulo {
    font-size:40px;
    color:#6EC1E4;
    margin-bottom:20px;
}
input {
    width:90%;
    padding:10px;
    margin:10px;
    border-radius:8px;
    border:1px solid #ccc;
}
button {
    width:100%;
    padding:10px;
    background:#A4DDED;
    border:none;
    border-radius:8px;
    cursor:pointer;
}
</style>
</head>
<body>
    <div class="box">
        <img src="/static/Donna.png" width="200">
        <form method="post">
            <input type="text" name="nome" placeholder="Nome completo" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Cadastrar</button>
        </form>
        <a href="/">Voltar</a>
    </div>
</body>
</html>
"""
 
@app.route("/agenda")
def mostrar_agenda():
    usuario = session.get("usuario")
 
    if not usuario:
        return redirect("/")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email=?", (usuario["email"],))
    usuario_nome = cursor.fetchone()[0]
    conn.close()
 
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial;
                background-color: #E6F3FF;
                padding: 20px;
            }}
 
            h1 {{
                color: #1F2E2E;
            }}
 
            h2 {{
                color: #1F2E2E;
                margin-top: 30px;
            }}
 
            .card {{
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                margin: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                width: 220px;
                display: inline-block;
                vertical-align: top;
            }}
 
            .botao {{
                background-color: #A4DDED;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                margin-top: 5px;
            }}
 
            .botao:hover {{
                opacity: 0.8;
            }}
 
            input[type="text"] {{
                padding: 5px;
                margin-top: 5px;
                width: 90%;
                border-radius: 6px;
                border: 1px solid #ccc;
            }}
 
            .topo {{
                margin-bottom: 20px;
            }}
 
            a {{
                text-decoration: none;
                color: #1F2E2E;
            }}
 
            .divider {{
                border: none;
                border-top: 1px solid #ccc;
                margin: 8px 0;
            }}
        </style>
    </head>
    <body>
    """
 
    html += f"<div class='topo'><h1>{'Agenda de Aulas' if usuario['tipo'] == 'aluna' else 'Painel do Personal'}</h1>"
    html += "<a href='/logout'>Sair</a></div>"
 
    for dia in dias_semana:
        html += f"<h2>{dia}</h2>"
 
        for i, slot in enumerate(agenda[dia]):
            html += f"<div class='card'>"
            html += f"<strong>{slot['horario']}</strong><br>"
            html += f"Vagas: {slot['vagas']}<br>"
 
            # Lista de alunas
            if slot.get("alunas"):
                if usuario["tipo"] == "profissional":
                    # Personal vê cada nome com botão de remover
                    html += "<div style='margin-top:6px;'>"
                    for nome_slot in slot["alunas"]:
                        html += f"""
                        <div style='display:flex; align-items:center; justify-content:space-between; margin:3px 0;'>
                            <span style='font-size:13px;'>{nome_slot}</span>
                            <form action='/remover_aluna/{dia}/{i}' method='post' style='margin:0;'>
                                <input type='hidden' name='nome_aluna' value='{nome_slot}'>
                                <button class='botao' type='submit' style='padding:3px 8px; font-size:12px; background:#ffaaaa;'>✕</button>
                            </form>
                        </div>
                        """
                    html += "</div>"
                else:
                    html += "Alunas: " + ", ".join(slot["alunas"]) + "<br>"
 
            # ALUNA
            if usuario["tipo"] == "aluna":
                if usuario_nome in slot["alunas"]:
                    html += f"""
                    <button class='botao' onclick="confirmarCancelamento('{dia}', {i})">Cancelar</button>
                    """
                else:
                    html += f"""
                    <form action='/reservar/{dia}/{i}' method='post'>
                        <button class='botao' type='submit'>Reservar</button>
                    </form>
                    """
 
            # PERSONAL
            if usuario["tipo"] == "profissional":
                html += f"""
                <hr class='divider'>
                <form action='/reservar_personal/{dia}/{i}' method='post'>
                    <input type='text' name='nome_aluna' placeholder='Nome da aluna' required>
                    <button class='botao' type='submit' style='margin-top:6px; width:100%;'>Reservar</button>
                </form>
                <a href='/resetar/{dia}/{i}'><button class='botao' style='margin-top:4px; width:100%;'>Resetar tudo</button></a>
                """
 
            html += "</div>"
 
    html += """
    <style>
    .popup {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(31, 46, 46, 0.9);
        display: none;
        justify-content: center;
        align-items: center;
    }
 
    .popup-box {
        background: #1F2E2E;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
    }
 
    .popup button {
        margin: 10px;
        padding: 10px;
        border: none;
        border-radius: 8px;
        background: #A4DDED;
        cursor: pointer;
    }
    </style>
 
    <div id="popup" class="popup">
        <div class="popup-box">
            <h2 style="color:#A4DDED;">Cancelar reserva?</h2>
            <button onclick="confirmar()">Sim</button>
            <button onclick="fechar()">Não</button>
        </div>
    </div>
 
    <script>
    let diaSelecionado = "";
    let indexSelecionado = 0;
 
    function confirmarCancelamento(dia, index) {
        diaSelecionado = dia;
        indexSelecionado = index;
        document.getElementById("popup").style.display = "flex";
    }
 
    function fechar() {
        document.getElementById("popup").style.display = "none";
    }
 
    function confirmar() {
        fetch(`/cancelar/${diaSelecionado}/${indexSelecionado}`, { method: "POST" })
        .then(() => window.location.reload());
    }
    </script>
 
    </body>
    </html>
    """
    return html
 
@app.route("/reservar/<dia>/<int:index>", methods=["POST"])
def reservar(dia, index):
    usuario = session.get("usuario")
 
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email=?", (usuario["email"],))
    nome = cursor.fetchone()[0]
    conn.close()
 
    for slot in agenda[dia]:
        if nome in slot["alunas"]:
            return """
            <html>
            <head>
            <style>
            body {
                font-family: Arial;
                background-color: #1F2E2E;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }
            .box {
                background: rgba(255, 255, 255, 0.05);
                padding:40px;
                border-radius:15px;
                text-align:center;
                box-shadow:0 5px 15px rgba(0,0,0,0.2);
            }
            h2 { color:#A4DDED; margin-bottom:20px; }
            a { text-decoration:none; }
            button {
                padding:10px 20px;
                background:#A4DDED;
                border:none;
                border-radius:8px;
                cursor:pointer;
            }
            </style>
            </head>
            <body>
                <div class="box">
                    <h2>Você já tem uma reserva nesse dia!</h2>
                    <a href="/agenda"><button>Voltar</button></a>
                </div>
            </body>
            </html>
            """
    
    if agenda[dia][index]["vagas"] > 0:
        agenda[dia][index]["vagas"] -= 1
        agenda[dia][index]["alunas"].append(nome)
 
    return redirect("/agenda")
 
@app.route("/reservar_personal/<dia>/<int:index>", methods=["POST"])
def reservar_personal(dia, index):
    usuario = session.get("usuario")
 
    if not usuario or usuario["tipo"] != "profissional":
        return redirect("/")
 
    nome_aluna = request.form.get("nome_aluna", "").strip()
 
    if not nome_aluna:
        return redirect("/agenda")
 
    # Verifica se a aluna já tem reserva nesse dia
    for slot in agenda[dia]:
        if nome_aluna in slot["alunas"]:
            return """
            <html>
            <head>
            <style>
            body {
                font-family: Arial;
                background-color: #1F2E2E;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }
            .box {
                background: rgba(255,255,255,0.05);
                padding:40px;
                border-radius:15px;
                text-align:center;
                box-shadow:0 5px 15px rgba(0,0,0,0.2);
            }
            h2 { color:#A4DDED; margin-bottom:20px; }
            a { text-decoration:none; }
            button {
                padding:10px 20px;
                background:#A4DDED;
                border:none;
                border-radius:8px;
                cursor:pointer;
            }
            </style>
            </head>
            <body>
                <div class="box">
                    <h2>Essa aluna já tem reserva nesse dia!</h2>
                    <a href="/agenda"><button>Voltar</button></a>
                </div>
            </body>
            </html>
            """
 
    if agenda[dia][index]["vagas"] > 0:
        agenda[dia][index]["vagas"] -= 1
        agenda[dia][index]["alunas"].append(nome_aluna)
 
    return redirect("/agenda")
 
@app.route("/remover_aluna/<dia>/<int:index>", methods=["POST"])
def remover_aluna(dia, index):
    usuario = session.get("usuario")
 
    if not usuario or usuario["tipo"] != "profissional":
        return redirect("/")
 
    nome_aluna = request.form.get("nome_aluna", "").strip()
 
    if nome_aluna in agenda[dia][index]["alunas"]:
        agenda[dia][index]["alunas"].remove(nome_aluna)
        agenda[dia][index]["vagas"] += 1
 
    return redirect("/agenda")
 
@app.route("/cancelar/<dia>/<int:index>", methods=["POST"])
def cancelar(dia, index):
    usuario = session.get("usuario")
 
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email=?", (usuario["email"],))
    nome = cursor.fetchone()[0]
    conn.close()
 
    if nome in agenda[dia][index]["alunas"]:
        agenda[dia][index]["alunas"].remove(nome)
        agenda[dia][index]["vagas"] += 1
 
    return redirect("/agenda")
 
@app.route("/resetar/<dia>/<int:index>")
def resetar(dia, index):
    agenda[dia][index]["vagas"] = 3
    agenda[dia][index]["alunas"] = []
 
    return redirect("/agenda")
 
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")
 
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
 
