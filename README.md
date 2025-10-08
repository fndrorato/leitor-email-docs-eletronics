# 📧 Leitor de E-mails com Processamento de Documentos Eletrônicos

Este projeto é uma aplicação fullstack composta por:

- **Backend** em Django + Celery (para ler e processar anexos XML de e-mails)
- **Frontend** em React
- Banco de dados **PostgreSQL**
- Fila de tarefas **Redis + Celery**
- **Gerador PDF** em React (serve apenas para gerar o PDF que o usuário deseja baixar)

## 🚀 Funcionalidades

- Conexão com contas de e-mail via IMAP
- Leitura de anexos `.xml` (Factura Electrónica - Paraguai)
- Armazenamento em banco de dados
- Visualização e filtros de documentos via frontend
- Download do XML e visualização do conteúdo em PDF

---

## 🧱 Estrutura dos Serviços (Docker Compose)

| Serviço       | Porta Externa  | Descrição                          |
|---------------|----------------|------------------------------------|
| `db`          | 5436           | Banco de dados PostgreSQL 15       |
| `redis`       | 6381           | Armazenamento de tarefas Celery    |
| `backend`     | 4101           | API Django                         |
| `celery`      | -              | Worker Celery                      |
| `frontend`    | 4102           | Interface Web (React)              |
| `gerador-pdf` | 4102           | App que gera o PDF.                |

---

## ⚙️ Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Configure o `.env`

Crie um arquivo `.env` na raiz com o seguinte conteúdo:

```dotenv
# Backend
DEBUG=True
DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_password
DB_HOST=db (nome do host do docker compose)
DB_PORT=5432 (porta padrão do postgresql)

DJANGO_SUPERUSER_USERNAME=usuario
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=senha

REDIS_HOST=redis
REDIS_PORT=6379

ROUTE_PDF_GENERATOR=http://ip_do_servidor:port


# Frontend
VITE_API_BASE_URL=http://backend:4101
VITE_APP_TITLE=Filtro de Documentos Electronicos
VITE_APP_PAGE_DESCRIPTION=Sistema de filtro para documentos electronicos emitidos contra BOX Mayorista
```

> ⚠️‼️ **IMPORTANTE**
> ⚠️‼️ Hoje dia 08/10/2025 - começaremos a utilizar o e-mail documentos.electronicos@amiria.com.py
> ⚠️‼️ Ele será válido por um ano o token.
---

### 3. Suba os containers

```bash
docker compose build
docker compose up -d
```

- Acesse o **backend (Django API)**: [http://localhost:4101](http://localhost:4101)
- Acesse o **frontend (React)**: [http://localhost:4102](http://localhost:4102)

---

## 📂 Estrutura do Projeto

```
.
├── server/          # Backend Django
│   ├── documentos/  # App principal
│   ├── users/       # Controle de usuários IMAP
│   └── ...
├── web/             # Frontend React
├── gerador-pdf/     # Sistema que gera o PDF do XML
├── .env             # Variáveis de ambiente
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Comandos úteis

### Backend Django

```bash
# Migrations
docker exec -it leitor-email-backend python manage.py makemigrations
docker exec -it leitor-email-backend python manage.py migrate

# Criação de superusuário
docker exec -it leitor-email-backend python manage.py createsuperuser
```

### Celery

```bash
docker logs -f leitor-email-celery
```

---

## 📄 Licença

Este projeto é privado. Todos os direitos reservados.
