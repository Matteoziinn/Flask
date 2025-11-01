# Encurtador de URL com Métricas (Flask + Prometheus + Grafana)

Projeto acadêmico para ADS (4º período): API Flask que encurta URLs, expõe métricas em `/metrics`
(via `prometheus-flask-exporter`), e um stack Prometheus + Grafana via Docker Compose.

---

## 1) Pré-requisitos
- Python 3.10+
- Docker Desktop (Windows/macOS) ou Docker Engine + Compose (Linux)
- VS Code (opcional, recomendado)

## 2) Preparar ambiente
```powershell
# Windows PowerShell no diretório do projeto
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3) Rodar a API
```bash
python app.py
```
Testes:
- Criar link:
  ```powershell
  curl -Method POST http://localhost:5000/encurtar `
   -ContentType "application/json" `
   -Body '{ "url_longa": "https://www.google.com" }'
  ```
- Métricas: abra `http://localhost:5000/metrics`

## 4) Subir Prometheus + Grafana
Em outro terminal, na pasta do projeto:
```bash
docker compose up -d
```
- Prometheus: `http://localhost:9090` → **Status > Targets** → deve estar **UP**.
- Grafana: `http://localhost:3000` (login: `admin` / `admin` no primeiro acesso).

### Conectar o Prometheus no Grafana
1. Grafana → **Gear (Config)** → **Data sources** → **Add data source** → **Prometheus**
2. Em **URL**: `http://prometheus:9090` → **Save & test**

### Criar Dashboard (5 painéis)
- **(Stat)** Total de Links Criados  
  ```
  links_criados_total
  ```
- **(Time series)** Redirecionamentos por Minuto  
  ```
  rate(redirecionamentos_total[1m]) * 60
  ```
- **(Time series)** Requisições por Segundo  
  ```
  rate(flask_http_requests_total[1m])
  ```
- **(Time series)** Latência P95  
  ```
  histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[1m])) by (le))
  ```
- **(Time series)** Erros 404 por Minuto  
  ```
  rate(flask_http_requests_total{status="404"}[1m])
  ```

## 5) Dicas e Problemas comuns
- **Target DOWN no Prometheus**: confirme que a API está em `0.0.0.0:5000`.  
  Em alguns Linux, `host.docker.internal` pode não resolver. Use o IP da máquina (ex.: `192.168.x.x:5000`) no `prometheus.yml` e rode `docker compose up -d` novamente.
- **Porta ocupada** (5000/9090/3000): troque as portas ou finalize processos em uso.
- **Latência P95 sem dados**: use **Explore** no Grafana e procure por `flask_http_`. Ajuste o nome do bucket se necessário.

## 6) Estrutura de Pastas
```
encurtador-flask/
├─ app.py
├─ requirements.txt
├─ prometheus.yml
├─ docker-compose.yml
└─ venv/  (não subir para o GitHub)
```

## 7) Como subir no GitHub
```bash
git init
git add .
git commit -m "Encurtador Flask + Observabilidade"
git branch -M main
git remote add origin <URL_DO_SEU_REPO>
git push -u origin main
```

## 8) Licença
Uso educacional.
