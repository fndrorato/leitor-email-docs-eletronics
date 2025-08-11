# 📧 Leitor de E-mails com Processamento de Documentos Eletrônicos

Este projeto é uma aplicação fullstack composta por:

- **Backend** em Django + Celery (para ler e processar anexos XML de e-mails)
- **Frontend** em React
- Banco de dados **PostgreSQL**
- Fila de tarefas **Redis + Celery**

## 🚀 Funcionalidades

- Conexão com contas de e-mail via IMAP
- Leitura de anexos `.xml` (Factura Electrónica - Paraguai)
- Armazenamento em banco de dados
- Visualização e filtros de documentos via frontend
- Download do XML e visualização do conteúdo em PDF

---

## 🧱 Estrutura dos Serviços (Docker Compose)

| Serviço     | Porta Externa | Descrição                          |
|-------------|----------------|------------------------------------|
| `db`        | 5436           | Banco de dados PostgreSQL 15       |
| `redis`     | 6381           | Armazenamento de tarefas Celery    |
| `backend`   | 4101           | API Django                         |
| `celery`    | -              | Worker Celery                      |
| `frontend`  | 4102           | Interface Web (React)              |

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
# Banco de dados
DB_NAME=docselectronicos
DB_USER=whatsuser
DB_PASSWORD=whatspass
DB_HOST=db
DB_PORT=5432

# Django
DEBUG=True
```

> ✅ **Importante:** esses valores são apenas exemplos. Use variáveis seguras em produção.

---

### 3. Suba os containers

```bash
docker-compose up --build
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
