# 📧 Sistema de Lectura y Procesamiento de Documentos Electrónicos
# 📧 Sistema de Leitura e Processamento de Documentos Eletrônicos

Sistema multi-empresa para lectura automática de correos electrónicos, procesamiento de archivos XML de Factura Electrónica (Paraguay) y gestión de documentos con exportación a PDF y Excel.

---

## 📖 Documentación Completa / Documentação Completa

Elija su idioma preferido para acceder a la documentación completa:

Escolha seu idioma preferido para acessar a documentação completa:

- **[🇪🇸 Español (Spanish)](./README.es.md)** - Documentación completa en español
- **[🇧🇷 Português (Portuguese)](./README.pt-BR.md)** - Documentação completa em português

---

## 🚀 Quick Start / Início Rápido

### Requisitos / Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 10GB espacio en disco / espaço em disco

### Instalación / Instalação

```bash
# Clonar repositorio / Clonar repositório
git clone https://github.com/seu-usuario/leitor-email.git
cd leitor-email

# Configurar .env (ver documentación completa)
# Configurar .env (ver documentação completa)
cp .env.example .env

# Construir e iniciar / Construir e iniciar
docker-compose build
docker-compose up -d

# Ejecutar migraciones / Executar migrações
docker exec -it leitor-email-backend python manage.py migrate
```

### Acceso / Acesso

**Frontend:**
- URL: http://10.1.1.4:4102/
- Usuario/Usuário: admin@admin.com
- Contraseña/Senha: Admin@2525

**Backend Admin:**
- URL: http://10.1.1.4:4101/admin
- Usuario/Usuário: admin
- Contraseña/Senha: Admin@2525

---

## 🏗️ Arquitectura / Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│    Django    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Celery    │
                    │   + Redis    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Node.js     │
                    │ PDF Generator│
                    └──────────────┘
```

---

## 📦 Servicios / Serviços

| Servicio/Serviço | Puerto/Porta | Descripción/Descrição |
|------------------|--------------|----------------------|
| Frontend (React) | 4102 | Interfaz web / Interface web |
| Backend (Django) | 4101 | API REST |
| PDF Generator | 4103 | Generador PDF / Gerador PDF |
| PostgreSQL | 5436 | Base de datos / Banco de dados |
| Redis | 6381 | Cola de tareas / Fila de tarefas |

---

## ✨ Funcionalidades / Funcionalidades

- ✅ Lectura automática de emails / Leitura automática de e-mails
- ✅ Procesamiento XML Factura Electrónica / Processamento XML Nota Fiscal
- ✅ Gestión multi-empresa / Gestão multi-empresas
- ✅ Generación de PDFs / Geração de PDFs
- ✅ Exportación a Excel / Exportação para Excel
- ✅ Filtros avanzados / Filtros avançados
- ✅ Tareas programadas (Celery Beat) / Tarefas agendadas (Celery Beat)

---

## 🛠️ Comandos Básicos / Comandos Básicos

```bash
# Ver logs / Ver logs
docker-compose logs -f

# Reiniciar servicios / Reiniciar serviços
docker-compose restart

# Detener todo / Parar tudo
docker-compose down

# Backup DB
docker exec leitor-email-db pg_dump -U postgres leitor_email_db > backup.sql
```

---

## 📞 Soporte / Suporte

- 📧 Email: soporte@amiria.com.py
- 📚 Docs: Ver README completo en tu idioma / Veja o README completo no seu idioma

---

## 📄 Licencia / Licença

Proyecto privado - Todos los derechos reservados © 2025

Projeto privado - Todos os direitos reservados © 2025

**BOX Mayorista**