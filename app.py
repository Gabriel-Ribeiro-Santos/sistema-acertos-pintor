from flask import Flask, flash, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_segura_12345!'


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '01030465gG@',
    'database': 'pintor_automotivo'
}



@app.route('/cadastrar-carro', methods=['GET', 'POST'])
def cadastrar_carro():
    if request.method == 'POST':
        nome = request.form['nome']
        placa = request.form['placa']
        cor = request.form['cor']
        pecas = request.form['pecas']
        valor_pintura = request.form['valor_pintura']

        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()

        query = """
        INSERT INTO carros (nome, placa, cor, pecas, valor_pintura)
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (nome, placa, cor, pecas, valor_pintura)
        cursor.execute(query, valores)
        conexao.commit()

        cursor.close()
        conexao.close()

        return redirect('/')

    return render_template('cadastrar_carro.html')

@app.route('/carros')
def listar_carros():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM carros WHERE acerto_id IS NULL")
    carros = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('listar_carros.html', carros=carros)


@app.route('/cadastrar-despesa', methods=['GET', 'POST'])
def cadastrar_despesa():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        data_compra = request.form['data_compra']

        try:
            conexao = mysql.connector.connect(**db_config)
            cursor = conexao.cursor()
            query = """
            INSERT INTO despesas (descricao, valor, data_compra)
            VALUES (%s, %s, %s)
            """
            valores = (descricao, valor, data_compra)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()
            return "Despesa cadastrada com sucesso! <a href='/cadastrar-despesa'>Cadastrar outra</a>"
        except mysql.connector.Error as erro:
            return f"Erro ao cadastrar despesa: {erro}"

    return render_template('cadastrar_despesa.html')

@app.route('/despesas')
def listar_despesas():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM despesas WHERE acerto_id IS NULL ORDER BY data_compra")
    despesas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('listar_despesas.html', despesas=despesas)

@app.route('/cadastrar-polimento', methods=['GET', 'POST'])
def cadastrar_polimento():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    if request.method == 'POST':
        carro_id = request.form['carro_id']
        quantidade = request.form['quantidade']
        data_polimento = request.form['data_polimento']

        try:
            query = """
            INSERT INTO polimentos (carro_id, quantidade, data_polimento)
            VALUES (%s, %s, %s)
            """
            valores = (carro_id, quantidade, data_polimento)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()
            return "Polimento cadastrado com sucesso! <a href='/cadastrar-polimento'>Cadastrar outro</a>"
        except mysql.connector.Error as erro:
            return f"Erro ao cadastrar polimento: {erro}"

    cursor.execute("SELECT id, nome, placa FROM carros")
    carros = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('cadastrar_polimento.html', carros=carros)

@app.route('/polimentos')
def listar_polimentos():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()
    query = "SELECT * FROM polimentos WHERE acerto_id IS NULL"
    cursor.execute(query)
    polimentos = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('listar_polimentos.html', polimentos=polimentos)

@app.route('/cadastrar-vale', methods=['GET', 'POST'])
def cadastrar_vale():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    if request.method == 'POST':
        valor = request.form['valor']
        data_retirada = request.form['data_retirada']

        try:
            query = "INSERT INTO vales (valor, data_retirada) VALUES (%s, %s)"
            cursor.execute(query, (valor, data_retirada))
            conexao.commit()
            cursor.close()
            conexao.close()
            return "Vale cadastrado com sucesso! <a href='/cadastrar-vale'>Cadastrar outro</a>"
        except mysql.connector.Error as erro:
            return f"Erro ao cadastrar vale: {erro}"

    return render_template('cadastrar_vale.html')

@app.route('/vales')
def listar_vales():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()
    query = "SELECT valor, data_retirada FROM vales WHERE acerto_id IS NULL ORDER BY data_retirada DESC"
    cursor.execute(query)
    vales = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('listar_vales.html', vales=vales)

@app.route('/acerto')
def acerto():
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    # Total de serviços (em aberto)
    cursor.execute("SELECT SUM(valor_pintura) FROM carros WHERE acerto_id IS NULL")
    total_servicos = cursor.fetchone()[0] or 0

    # Total despesas (em aberto)
    cursor.execute("SELECT SUM(valor) FROM despesas WHERE acerto_id IS NULL")
    total_despesas = cursor.fetchone()[0] or 0

    # Total polimentos (em aberto)
    cursor.execute("SELECT SUM(quantidade * valor_unitario) FROM polimentos WHERE acerto_id IS NULL")
    total_polimentos = cursor.fetchone()[0] or 0

    # Total vales (em aberto)
    cursor.execute("SELECT SUM(valor) FROM vales WHERE acerto_id IS NULL")
    total_vales = cursor.fetchone()[0] or 0

    # Cálculos
    total_lucro = total_servicos - total_despesas - total_polimentos
    seu_acerto = total_lucro / 2
    a_receber = seu_acerto - total_vales

    cursor.close()
    conexao.close()

    return render_template('acerto_final.html', 
        total_servicos=total_servicos,
        total_despesas=total_despesas,
        total_polimentos=total_polimentos,
        total_lucro=total_lucro,
        seu_acerto=seu_acerto,
        total_vales=total_vales,
        a_receber=a_receber
    )



@app.route('/')
def menu():
    return render_template('menu.html') 

@app.route("/fechar_acerto")
@app.route("/fechar_acerto", methods=["POST"])
def fechar_acerto():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. Somar todos os dados em aberto
        cursor.execute("SELECT IFNULL(SUM(valor_pintura), 0) FROM carros WHERE acerto_id IS NULL")
        total_servico = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(valor), 0) FROM despesas WHERE acerto_id IS NULL")
        total_material = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(quantidade * valor_unitario), 0) FROM polimentos WHERE acerto_id IS NULL")
        total_polimento = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(valor), 0) FROM vales WHERE acerto_id IS NULL")
        total_vales = cursor.fetchone()[0]

        # 2. Impede salvar se tudo estiver zerado
        if total_servico == 0 and total_material == 0 and total_polimento == 0 and total_vales == 0:
            flash("Nenhum dado novo para fechar o acerto.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for("menu"))  # ⚠️ ESSE return é fundamental

        # 3. Calcular valores
        total = total_servico - total_material - total_polimento
        valor_recebido = (total / 2) - total_vales

        # 4. Inserir novo acerto
        cursor.execute("""
            INSERT INTO acertos (data_acerto, total_servico, total_material, total_polimento, total_vales, valor_recebido)
            VALUES (CURDATE(), %s, %s, %s, %s, %s)
        """, (total_servico, total_material, total_polimento, total_vales, valor_recebido))
        conn.commit()

        acerto_id = cursor.lastrowid

        # 5. Atualiza outras tabelas com esse acerto_id
        tabelas = ['carros', 'despesas', 'polimentos', 'vales']
        for tabela in tabelas:
            cursor.execute(f"UPDATE {tabela} SET acerto_id = %s WHERE acerto_id IS NULL", (acerto_id,))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Acerto fechado com sucesso!", "success")
        return redirect(url_for("menu"))

    except Exception as e:
        flash(f"Erro ao fechar acerto: {e}", "danger")
        return redirect(url_for("menu"))

    

@app.route('/acertos')
def listar_acertos():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM acertos ORDER BY data_acerto DESC")
        acertos = cursor.fetchall()
        conn.close()
        return render_template('acertos.html', acertos=acertos)
    except Exception as e:
        return f"Erro ao buscar acertos: {e}"
    

@app.route('/acerto/<int:id>')
def detalhes_acerto(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Buscar dados do acerto
        cursor.execute("SELECT * FROM acertos WHERE id = %s", (id,))
        acerto = cursor.fetchone()

        # Buscar carros do acerto
        cursor.execute("SELECT * FROM carros WHERE acerto_id = %s", (id,))
        carros = cursor.fetchall()

        # Buscar despesas do acerto
        cursor.execute("SELECT * FROM despesas WHERE acerto_id = %s", (id,))
        despesas = cursor.fetchall()

        # Buscar polimentos do acerto (ligados aos carros)
        cursor.execute("""
            SELECT p.* FROM polimentos p
            JOIN carros c ON p.carro_id = c.id
            WHERE c.acerto_id = %s
        """, (id,))
        polimentos = cursor.fetchall()

        # Buscar vales do acerto
        cursor.execute("SELECT * FROM vales WHERE acerto_id = %s", (id,))
        vales = cursor.fetchall()

        conn.close()
        print("Carros:", carros)
        print("Despesas:", despesas)
        print("Polimentos:", polimentos)
        print("Vales:", vales)


        return render_template(
            'detalhes_acerto.html',
            acerto=acerto,
            carros=carros,
            despesas=despesas,
            polimentos=polimentos,
            vales=vales
        )

    except Exception as e:
        return f"Erro ao buscar detalhes do acerto: {e}"






if __name__ == '__main__':
    app.run(debug=True)
