# 📧 Sistema de Leitura e Processamento de Documentos Eletrônicos

Sistema multi-empresas para leitura automática de e-mails, processamento de arquivos XML de Nota Fiscal Eletrônica (Paraguai) e gestão de documentos com exportação para PDF e Excel.

## 📋 Descrição Geral

Esta aplicação fullstack permite às empresas:
- **Ler e-mails automaticamente** através de IMAP
- **Processar arquivos XML** de Faturas Eletrônicas paraguaias
- **Armazenar documentos** em banco de dados PostgreSQL
- **Visualizar e filtrar** documentos eletrônicos
- **Gerar PDFs** dos documentos XML
- **Exportar dados** para Excel
- **Gestão multi-empresas** com usuários independentes

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

| Componente | Tecnologia | Porta | Descrição |
|------------|------------|-------|-----------|
| **Frontend** | React + Vite | 4102 | Interface de usuário |
| **Backend** | Django + DRF | 4101 | API REST e lógica de negócio |
| **Worker** | Celery | - | Processamento assíncrono de tarefas |
| **Scheduler** | Celery Beat | - | Agendamento de tarefas automáticas |
| **Gerador PDF** | Node.js | 4103 | Serviço de geração de PDFs |
| **Banco de Dados** | PostgreSQL 15 | 5436 | Armazenamento de dados |
| **Fila de Tarefas** | Redis 7 | 6381 | Gerenciamento de tarefas assíncronas |

---

## 📁 Estrutura do Projeto

```
.
├── server/                 # Backend Django
│   ├── documentos/        # App principal - gestão de documentos
│   ├── users/             # Gestão de usuários e contas IMAP
│   ├── app/               # Configuração do projeto Django
│   ├── requirements.txt   # Dependências Python
│   ├── Dockerfile         # Imagem Docker do backend
│   └── entrypoint.sh      # Script de inicialização
│
├── web/                   # Frontend React
│   ├── src/               # Código fonte React
│   ├── package.json       # Dependências Node.js
│   ├── Dockerfile         # Imagem Docker do frontend
│   └── .env.production    # Variáveis de ambiente de produção
│
├── gerador-pdf/           # Serviço gerador de PDF
│   ├── server.js          # Servidor Node.js
│   ├── package.json       # Dependências
│   └── Dockerfile         # Imagem Docker do gerador
│
├── docker-compose.yml     # Orquestração de containers
├── .env                   # Variáveis de ambiente
└── README.md              # Este arquivo
```

---

## 🚀 Requisitos Prévios

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git** (para clonar o repositório)
- Pelo menos **4GB de RAM** disponível
- **10GB de espaço em disco**

### Verificar instalação

```bash
docker --version
docker-compose --version
```

---

## ⚙️ Instalação e Configuração

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/leitor-email.git
cd leitor-email
```

### Passo 2: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env
```

Copie e configure as seguintes variáveis:

```dotenv
# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================
DB_NAME=leitor_email_db
DB_USER=postgres
DB_PASSWORD=postgres_password_secure_123
DB_HOST=db
DB_PORT=5432

# ==========================================
# CONFIGURAÇÃO DO DJANGO
# ==========================================
DEBUG=False
SECRET_KEY=django-insecure-trocar-esta-chave-em-producao
ALLOWED_HOSTS=localhost,127.0.0.1,10.1.1.4

# Superusuário Django (criado automaticamente)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=Admin@2525

# ==========================================
# CONFIGURAÇÃO DO REDIS
# ==========================================
REDIS_HOST=redis
REDIS_PORT=6379

# ==========================================
# CONFIGURAÇÃO DO GERADOR PDF
# ==========================================
ROUTE_PDF_GENERATOR=http://10.1.1.4:4103

# ==========================================
# CONFIGURAÇÃO DO FRONTEND
# ==========================================
VITE_API_BASE_URL=http://10.1.1.4:4101
VITE_APP_TITLE=Filtro de Documentos Eletrônicos
VITE_APP_PAGE_DESCRIPTION=Sistema de filtro para documentos eletrônicos emitidos contra BOX Mayorista
```

> ⚠️ **IMPORTANTE - SEGURANÇA**
> 
> - Altere todas as senhas em produção
> - Gere uma `SECRET_KEY` única para Django
> - Use senhas fortes para o banco de dados
> - Configure `ALLOWED_HOSTS` com seus domínios

### Passo 3: Construir as Imagens Docker

```bash
docker-compose build
```

Este processo pode levar vários minutos na primeira vez, pois baixa todas as dependências.

**Saída esperada:**
```
[+] Building 234.5s (45/45) FINISHED
 => [backend] ...
 => [frontend] ...
 => [pdf] ...
```

### Passo 4: Iniciar os Containers

```bash
docker-compose up -d
```

A flag `-d` executa os containers em segundo plano (modo detached).

**Verificar se todos os serviços estão rodando:**

```bash
docker-compose ps
```

**Saída esperada:**
```
NAME                        STATUS              PORTS
leitor-email-db             Up                  0.0.0.0:5436->5432/tcp
leitor-email-redis          Up                  0.0.0.0:6381->6379/tcp
leitor-email-backend        Up                  0.0.0.0:4101->8000/tcp
leitor-email-celery         Up
leitor-email-beat           Up
leitor-email-frontend       Up                  0.0.0.0:4102->3000/tcp
leitor-email-gerador-pdf    Up                  0.0.0.0:4103->3001/tcp
```

### Passo 5: Executar Migrações do Banco de Dados

```bash
docker exec -it leitor-email-backend python manage.py migrate
```

### Passo 6: (Opcional) Criar Superusuário Manualmente

Se não foi criado automaticamente, você pode criá-lo com:

```bash
docker exec -it leitor-email-backend python manage.py createsuperuser
```

---

## 🌐 Acesso ao Sistema

### Frontend (Aplicação Web)

**URL:** `http://10.1.1.4:4102/`

**Credenciais padrão:**
- **Usuário:** admin@admin.com
- **Senha:** Admin@2525

### Backend (Painel de Administração Django)

**URL:** `http://10.1.1.4:4101/admin`

**Credenciais padrão:**
- **Usuário:** admin
- **Senha:** Admin@2525

### API REST

**URL Base:** `http://10.1.1.4:4101/api/`

**Documentação Swagger:** `http://10.1.1.4:4101/swagger/`

---

## 📧 Configuração de Contas de E-mail

### E-mail Corporativo Atual

> ⚠️ **INFORMAÇÃO IMPORTANTE**
> 
> **Data de início:** 08/10/2025
> 
> **E-mail ativo:** documentos.electronicos@amiria.com.py
> 
> **Validade do token:** 1 ano (até 08/10/2026)

### Adicionar Nova Conta de E-mail

1. Acesse o painel de administração: `http://10.1.1.4:4101/admin`
2. Navegue até **Users → Email Accounts**
3. Clique em **Adicionar Email Account**
4. Preencha os campos:
   - **Email:** endereço de e-mail completo
   - **Password:** senha da conta
   - **IMAP Server:** servidor IMAP (ex: imap.gmail.com)
   - **IMAP Port:** porta IMAP (geralmente 993)
   - **Empresa:** selecione a empresa associada
5. Salve as alterações

---

## 🔄 Configuração de Tarefas Automáticas (Celery Beat)

O sistema utiliza **Celery Beat** com **django-celery-beat** para agendar tarefas automáticas.

### Ver Tarefas Agendadas

1. Acesse o admin do Django: `http://10.1.1.4:4101/admin`
2. Navegue até **Periodic Tasks**
3. Aqui você pode ver, editar ou criar novas tarefas

### Criar Tarefa de Leitura de E-mails

1. Em **Periodic Tasks** → **Add**
2. Configure:
   - **Name:** Ler e-mails a cada hora
   - **Task:** `documentos.tasks.read_all_emails` (nome da sua tarefa)
   - **Interval:** Selecione ou crie intervalo (ex: a cada 1 hora)
   - **Enabled:** ✓ Ativado
3. Salve

### Intervalos Recomendados

- **Leitura de e-mails:** A cada 30-60 minutos
- **Limpeza de logs:** Diariamente às 3:00 AM
- **Backup do banco de dados:** Semanalmente

---

## 🛠️ Comandos Úteis

### Docker Compose

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f beat

# Parar todos os containers
docker-compose down

# Parar e remover volumes (⚠️ APAGA O BANCO DE DADOS)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart backend
docker-compose restart celery

# Ver uso de recursos
docker stats
```

### Django (Backend)

```bash
# Executar migrações
docker exec -it leitor-email-backend python manage.py migrate

# Criar migrações
docker exec -it leitor-email-backend python manage.py makemigrations

# Criar superusuário
docker exec -it leitor-email-backend python manage.py createsuperuser

# Abrir shell do Django
docker exec -it leitor-email-backend python manage.py shell

# Executar testes
docker exec -it leitor-email-backend python manage.py test

# Coletar arquivos estáticos
docker exec -it leitor-email-backend python manage.py collectstatic --no-input
```

### Celery

```bash
# Ver logs do worker
docker logs -f leitor-email-celery

# Ver logs do beat scheduler
docker logs -f leitor-email-beat

# Reiniciar celery worker
docker-compose restart celery

# Reiniciar celery beat
docker-compose restart beat

# Ver tarefas ativas
docker exec -it leitor-email-celery celery -A app inspect active

# Ver tarefas agendadas
docker exec -it leitor-email-celery celery -A app inspect scheduled
```

### Banco de Dados

```bash
# Acessar PostgreSQL
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db

# Fazer backup do banco de dados
docker exec -it leitor-email-db pg_dump -U postgres leitor_email_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i leitor-email-db psql -U postgres -d leitor_email_db < backup_20250101.sql

# Ver tamanho do banco de dados
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "SELECT pg_size_pretty(pg_database_size('leitor_email_db'));"
```

---

## 🔍 Funcionalidades do Sistema

### 1. Gestão Multi-Empresas

- Cada empresa tem suas próprias contas de e-mail
- Usuários independentes por empresa
- Filtros e permissões por empresa

### 2. Leitura Automática de E-mails

- Conexão IMAP configurável
- Leitura agendada via Celery Beat
- Detecção automática de arquivos XML anexados
- Marcação de e-mails processados

### 3. Processamento de Documentos XML

- Extração de dados de Fatura Eletrônica Paraguai
- Validação de estrutura XML
- Armazenamento normalizado no BD
- Indexação para buscas rápidas

### 4. Interface de Usuário (Frontend)

- Dashboard com estatísticas
- Filtros avançados de busca
- Visualização de documentos
- Download de XMLs originais
- Geração de PDFs

### 5. Geração de PDFs

- Conversão de XML para formato PDF legível
- Design profissional baseado em padrões
- Download imediato

### 6. Exportação de Dados

- Exportar para Excel (.xlsx)
- Filtros aplicados são mantidos na exportação
- Colunas personalizáveis

---

## 🐛 Solução de Problemas

### O backend não inicia

**Sintoma:** Erro de conexão com o banco de dados

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Ver logs do banco de dados
docker-compose logs db

# Reiniciar o banco de dados
docker-compose restart db

# Se persistir, remover volume e recriar (⚠️ apaga dados)
docker-compose down -v
docker-compose up -d
```

### Celery não processa tarefas

**Sintoma:** As tarefas ficam pendentes

**Solução:**
```bash
# Ver logs do worker
docker-compose logs celery

# Verificar conexão ao Redis
docker exec -it leitor-email-redis redis-cli ping
# Deve responder: PONG

# Reiniciar celery
docker-compose restart celery beat
```

### Frontend não carrega

**Sintoma:** Página em branco ou erro 502

**Solução:**
```bash
# Ver logs do frontend
docker-compose logs frontend

# Verificar se o build foi bem-sucedido
docker exec -it leitor-email-frontend ls -la /app/dist

# Reconstruir frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Erro de permissões em arquivos

**Solução:**
```bash
# Ajustar permissões das pastas do projeto
sudo chown -R $USER:$USER .

# Reiniciar containers
docker-compose restart
```

### Banco de dados cheio

**Solução:**
```bash
# Ver tamanho das tabelas
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Limpar logs antigos (adapte conforme seu modelo)
docker exec -it leitor-email-backend python manage.py shell
>>> from documentos.models import Log
>>> Log.objects.filter(created_at__lt='2025-01-01').delete()
```

---

## 🔐 Segurança

### Recomendações de Produção

1. **Alterar todas as senhas padrão**
2. **Usar HTTPS** com certificados SSL/TLS
3. **Configurar firewall** para limitar acesso às portas
4. **Backups automáticos** do banco de dados
5. **Monitoramento de logs** para detectar acessos não autorizados
6. **Atualizar dependências** regularmente

### Gerar SECRET_KEY do Django

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 📊 Monitoramento e Manutenção

### Monitoramento de Recursos

```bash
# Ver uso de CPU e memória
docker stats

# Espaço em disco usado pelo Docker
docker system df

# Limpar recursos não utilizados
docker system prune -a
```

### Backups Automatizados

Criar um cron job para backups diários:

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 2 AM)
0 2 * * * docker exec leitor-email-db pg_dump -U postgres leitor_email_db | gzip > /backups/leitor_$(date +\%Y\%m\%d).sql.gz
```

### Logs da Aplicação

Os logs são armazenados em:
- **Backend Django:** stdout (ver com `docker-compose logs backend`)
- **Celery:** stdout (ver com `docker-compose logs celery`)
- **PostgreSQL:** `/var/lib/postgresql/data/log/` (dentro do container)

---

## 📝 Notas de Desenvolvimento

### Desenvolvimento Local (sem Docker)

Se deseja desenvolver sem Docker:

**Backend:**
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

**Frontend:**
```bash
cd web
npm install
npm run dev
```

### Adicionar Nova Dependência

**Python (Backend):**
```bash
# Adicionar ao requirements.txt
docker-compose build backend
docker-compose up -d backend
```

**Node (Frontend):**
```bash
# Editar package.json
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📞 Suporte

Para problemas ou dúvidas:

- **E-mail:** soporte@amiria.com.py
- **Documentação:** Este README.md
- **Logs:** Sempre inclua logs ao reportar problemas

---

## 📄 Licença

Este projeto é privado. Todos os direitos reservados © 2025.

**Uso autorizado somente para:** BOX Mayorista e empresas associadas.

---

## 🔄 Atualizações

### Versão 1.0.0 (Atual)

- ✅ Leitura automática de e-mails via IMAP
- ✅ Processamento de XML de Fatura Eletrônica
- ✅ Interface web React
- ✅ Geração de PDFs
- ✅ Exportação para Excel
- ✅ Sistema multi-empresas

### Próximas Funcionalidades

- 🔄 Notificações por e-mail
- 🔄 Dashboard de estatísticas avançadas
- 🔄 API pública com autenticação
- 🔄 Integração com sistemas contábeis

---

**Sistema pronto para uso! 🚀**