import random
import string
from flask import Flask, request, redirect, jsonify, Response
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

app = Flask(__name__)

# 1) Instrumentação automática do Flask (latência, contagem, status etc.)
#    NÃO definimos o path aqui para evitar conflito; só registramos os coletores.
metrics = PrometheusMetrics(app)

# 2) Endpoint /metrics garantido de forma explícita (sempre vai existir)
@app.route("/metrics")
def metrics_endpoint():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

# 3) Métricas de negócio
links_criados_total = Counter('links_criados_total', 'Total de novos links encurtados criados.')
redirecionamentos_total = Counter('redirecionamentos_total', 'Total de links redirecionados.')

# "banco" em memória
url_db = {}

def gerar_codigo_curto(tamanho=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

@app.route('/encurtar', methods=['POST'])
def encurtar_url():
    dados = request.get_json()
    if not dados or 'url_longa' not in dados:
        return jsonify({"erro": "URL longa não fornecida"}), 400

    url_longa = dados['url_longa']
    codigo_curto = gerar_codigo_curto()
    while codigo_curto in url_db:
        codigo_curto = gerar_codigo_curto()

    url_db[codigo_curto] = url_longa
    links_criados_total.inc()
    return jsonify({
        "url_longa": url_longa,
        "url_curta": f"{request.host_url}r/{codigo_curto}"
    }), 201

@app.route('/r/<string:codigo_curto>', methods=['GET'])
def redirecionar(codigo_curto):
    url_longa = url_db.get(codigo_curto)
    if url_longa:
        redirecionamentos_total.inc()
        return redirect(url_longa, code=302)
    else:
        return jsonify({"erro": "URL curta não encontrada"}), 404

@app.route('/api/links', methods=['GET'])
def listar_links():
    return jsonify(url_db)

if __name__ == '__main__':
    # importante para o Prometheus alcançar do contêiner
    app.run(debug=True, host='0.0.0.0', port=5000)
