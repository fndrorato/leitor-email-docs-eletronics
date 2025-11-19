# 📧 Sistema de Lectura y Procesamiento de Documentos Electrónicos

Sistema multi-empresa para lectura automática de correos electrónicos, procesamiento de archivos XML de Factura Electrónica (Paraguay) y gestión de documentos con exportación a PDF y Excel.

## 📋 Descripción General

Esta aplicación fullstack permite a las empresas:
- **Leer correos electrónicos** automáticamente mediante IMAP
- **Procesar archivos XML** de Facturas Electrónicas paraguayas
- **Almacenar documentos** en base de datos PostgreSQL
- **Visualizar y filtrar** documentos electrónicos
- **Generar PDFs** de los documentos XML
- **Exportar datos** a Excel
- **Gestión multi-empresa** con usuarios independientes

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

| Componente | Tecnología | Puerto | Descripción |
|------------|------------|--------|-------------|
| **Frontend** | React + Vite | 4102 | Interfaz de usuario |
| **Backend** | Django + DRF | 4101 | API REST y lógica de negocio |
| **Worker** | Celery | - | Procesamiento asíncrono de tareas |
| **Scheduler** | Celery Beat | - | Programación de tareas automáticas |
| **Generador PDF** | Node.js | 4103 | Servicio de generación de PDFs |
| **Base de Datos** | PostgreSQL 15 | 5436 | Almacenamiento de datos |
| **Cola de Tareas** | Redis 7 | 6381 | Gestión de tareas asíncronas |

---

## 📁 Estructura del Proyecto

```
.
├── server/                 # Backend Django
│   ├── documentos/        # App principal - gestión de documentos
│   ├── users/             # Gestión de usuarios y cuentas IMAP
│   ├── app/               # Configuración del proyecto Django
│   ├── requirements.txt   # Dependencias Python
│   ├── Dockerfile         # Imagen Docker del backend
│   └── entrypoint.sh      # Script de inicialización
│
├── web/                   # Frontend React
│   ├── src/               # Código fuente React
│   ├── package.json       # Dependencias Node.js
│   ├── Dockerfile         # Imagen Docker del frontend
│   └── .env.production    # Variables de entorno de producción
│
├── gerador-pdf/           # Servicio generador de PDF
│   ├── server.js          # Servidor Node.js
│   ├── package.json       # Dependencias
│   └── Dockerfile         # Imagen Docker del generador
│
├── docker-compose.yml     # Orquestación de contenedores
├── .env                   # Variables de entorno
└── README.md              # Este archivo
```

---

## 🚀 Requisitos Previos

Antes de comenzar, asegúrese de tener instalado:

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)
- Al menos **4GB de RAM** disponible
- **10GB de espacio en disco**

### Verificar instalación

```bash
docker --version
docker-compose --version
```

---

## ⚙️ Instalación y Configuración

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/seu-usuario/leitor-email.git
cd leitor-email
```

### Paso 2: Configurar Variables de Entorno

Cree un archivo `.env` en la raíz del proyecto:

```bash
touch .env
```

Copie y configure las siguientes variables:

```dotenv
# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
DB_NAME=leitor_email_db
DB_USER=postgres
DB_PASSWORD=postgres_password_secure_123
DB_HOST=db
DB_PORT=5432

# ==========================================
# CONFIGURACIÓN DE DJANGO
# ==========================================
DEBUG=False
SECRET_KEY=django-insecure-cambiar-esta-clave-en-produccion
ALLOWED_HOSTS=localhost,127.0.0.1,10.1.1.4

# Superusuario Django (se crea automáticamente)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=Admin@2525

# ==========================================
# CONFIGURACIÓN DE REDIS
# ==========================================
REDIS_HOST=redis
REDIS_PORT=6379

# ==========================================
# CONFIGURACIÓN DEL GENERADOR PDF
# ==========================================
ROUTE_PDF_GENERATOR=http://10.1.1.4:4103

# ==========================================
# CONFIGURACIÓN DEL FRONTEND
# ==========================================
VITE_API_BASE_URL=http://10.1.1.4:4101
VITE_APP_TITLE=Filtro de Documentos Electrónicos
VITE_APP_PAGE_DESCRIPTION=Sistema de filtro para documentos electrónicos emitidos contra BOX Mayorista
```

> ⚠️ **IMPORTANTE - SEGURIDAD**
> 
> - Cambie todas las contraseñas en producción
> - Genere un `SECRET_KEY` único para Django
> - Use contraseñas seguras para la base de datos
> - Configure `ALLOWED_HOSTS` con sus dominios

### Paso 3: Construir las Imágenes Docker

```bash
docker-compose build
```

Este proceso puede tardar varios minutos la primera vez, ya que descarga todas las dependencias.

**Salida esperada:**
```
[+] Building 234.5s (45/45) FINISHED
 => [backend] ...
 => [frontend] ...
 => [pdf] ...
```

### Paso 4: Iniciar los Contenedores

```bash
docker-compose up -d
```

El flag `-d` ejecuta los contenedores en segundo plano (modo detached).

**Verificar que todos los servicios están corriendo:**

```bash
docker-compose ps
```

**Salida esperada:**
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

### Paso 5: Ejecutar Migraciones de Base de Datos

```bash
docker exec -it leitor-email-backend python manage.py migrate
```

### Paso 6: (Opcional) Crear Superusuario Manualmente

Si no se creó automáticamente, puede crearlo con:

```bash
docker exec -it leitor-email-backend python manage.py createsuperuser
```

---

## 🌐 Acceso al Sistema

### Frontend (Aplicación Web)

**URL:** `http://10.1.1.4:4102/`

**Credenciales por defecto:**
- **Usuario:** admin@admin.com
- **Contraseña:** Admin@2525

### Backend (Panel de Administración Django)

**URL:** `http://10.1.1.4:4101/admin`

**Credenciales por defecto:**
- **Usuario:** admin
- **Contraseña:** Admin@2525

### API REST

**URL Base:** `http://10.1.1.4:4101/api/`

**Documentación Swagger:** `http://10.1.1.4:4101/swagger/`

---

## 📧 Configuración de Cuentas de Correo

### Email Corporativo Actual

> ⚠️ **INFORMACIÓN IMPORTANTE**
> 
> **Fecha de inicio:** 08/10/2025
> 
> **Email activo:** documentos.electronicos@amiria.com.py
> 
> **Validez del token:** 1 año (hasta 08/10/2026)

### Agregar Nueva Cuenta de Correo

1. Acceda al panel de administración: `http://10.1.1.4:4101/admin`
2. Navegue a **Users → Email Accounts**
3. Click en **Agregar Email Account**
4. Complete los campos:
   - **Email:** dirección de correo completa
   - **Password:** contraseña de la cuenta
   - **IMAP Server:** servidor IMAP (ej: imap.gmail.com)
   - **IMAP Port:** puerto IMAP (generalmente 993)
   - **Empresa:** seleccione la empresa asociada
5. Guarde los cambios

---

## 🔄 Configuración de Tareas Automáticas (Celery Beat)

El sistema utiliza **Celery Beat** con **django-celery-beat** para programar tareas automáticas.

### Ver Tareas Programadas

1. Acceda al admin de Django: `http://10.1.1.4:4101/admin`
2. Navegue a **Periodic Tasks**
3. Aquí puede ver, editar o crear nuevas tareas

### Crear Tarea de Lectura de Emails

1. En **Periodic Tasks** → **Add**
2. Configure:
   - **Name:** Leer emails cada hora
   - **Task:** `documentos.tasks.read_all_emails` (nombre de su tarea)
   - **Interval:** Seleccione o cree intervalo (ej: cada 1 hora)
   - **Enabled:** ✓ Activado
3. Guarde

### Intervalos Recomendados

- **Lectura de emails:** Cada 30-60 minutos
- **Limpieza de logs:** Diariamente a las 3:00 AM
- **Respaldo de base de datos:** Semanalmente

---

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f beat

# Detener todos los contenedores
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BASE DE DATOS)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart backend
docker-compose restart celery

# Ver uso de recursos
docker stats
```

### Django (Backend)

```bash
# Ejecutar migraciones
docker exec -it leitor-email-backend python manage.py migrate

# Crear migraciones
docker exec -it leitor-email-backend python manage.py makemigrations

# Crear superusuario
docker exec -it leitor-email-backend python manage.py createsuperuser

# Abrir shell de Django
docker exec -it leitor-email-backend python manage.py shell

# Ejecutar tests
docker exec -it leitor-email-backend python manage.py test

# Recolectar archivos estáticos
docker exec -it leitor-email-backend python manage.py collectstatic --no-input
```

### Celery

```bash
# Ver logs del worker
docker logs -f leitor-email-celery

# Ver logs del beat scheduler
docker logs -f leitor-email-beat

# Reiniciar celery worker
docker-compose restart celery

# Reiniciar celery beat
docker-compose restart beat

# Ver tareas activas
docker exec -it leitor-email-celery celery -A app inspect active

# Ver tareas programadas
docker exec -it leitor-email-celery celery -A app inspect scheduled
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db

# Hacer backup de la base de datos
docker exec -it leitor-email-db pg_dump -U postgres leitor_email_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i leitor-email-db psql -U postgres -d leitor_email_db < backup_20250101.sql

# Ver tamaño de la base de datos
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "SELECT pg_size_pretty(pg_database_size('leitor_email_db'));"
```

---

## 🔍 Funcionalidades del Sistema

### 1. Gestión Multi-Empresa

- Cada empresa tiene sus propias cuentas de correo
- Usuarios independientes por empresa
- Filtros y permisos por empresa

### 2. Lectura Automática de Emails

- Conexión IMAP configurable
- Lectura programada via Celery Beat
- Detección automática de archivos XML adjuntos
- Marcado de emails procesados

### 3. Procesamiento de Documentos XML

- Extracción de datos de Factura Electrónica Paraguay
- Validación de estructura XML
- Almacenamiento normalizado en BD
- Indexación para búsquedas rápidas

### 4. Interfaz de Usuario (Frontend)

- Dashboard con estadísticas
- Filtros avanzados de búsqueda
- Visualización de documentos
- Descarga de XMLs originales
- Generación de PDFs

### 5. Generación de PDFs

- Conversión de XML a formato PDF legible
- Diseño profesional basado en estándares
- Descarga inmediata

### 6. Exportación de Datos

- Exportar a Excel (.xlsx)
- Filtros aplicados se mantienen en exportación
- Columnas personalizables

---

## 🐛 Solución de Problemas

### El backend no inicia

**Síntoma:** Error de conexión a la base de datos

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps db

# Ver logs de la base de datos
docker-compose logs db

# Reiniciar la base de datos
docker-compose restart db

# Si persiste, eliminar volumen y recrear (⚠️ borra datos)
docker-compose down -v
docker-compose up -d
```

### Celery no procesa tareas

**Síntoma:** Las tareas quedan pendientes

**Solución:**
```bash
# Ver logs del worker
docker-compose logs celery

# Verificar conexión a Redis
docker exec -it leitor-email-redis redis-cli ping
# Debe responder: PONG

# Reiniciar celery
docker-compose restart celery beat
```

### Frontend no carga

**Síntoma:** Página en blanco o error 502

**Solución:**
```bash
# Ver logs del frontend
docker-compose logs frontend

# Verificar que el build fue exitoso
docker exec -it leitor-email-frontend ls -la /app/dist

# Reconstruir frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Error de permisos en archivos

**Solución:**
```bash
# Ajustar permisos de las carpetas del proyecto
sudo chown -R $USER:$USER .

# Reiniciar contenedores
docker-compose restart
```

### Base de datos llena

**Solución:**
```bash
# Ver tamaño de las tablas
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Limpiar logs antiguos (adapte según su modelo)
docker exec -it leitor-email-backend python manage.py shell
>>> from documentos.models import Log
>>> Log.objects.filter(created_at__lt='2025-01-01').delete()
```

---

## 🔐 Seguridad

### Recomendaciones de Producción

1. **Cambiar todas las contraseñas por defecto**
2. **Usar HTTPS** con certificados SSL/TLS
3. **Configurar firewall** para limitar acceso a puertos
4. **Backups automáticos** de la base de datos
5. **Monitoreo de logs** para detectar accesos no autorizados
6. **Actualizar dependencias** regularmente

### Generar SECRET_KEY de Django

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 📊 Monitoreo y Mantenimiento

### Monitoreo de Recursos

```bash
# Ver uso de CPU y memoria
docker stats

# Espacio en disco usado por Docker
docker system df

# Limpiar recursos no utilizados
docker system prune -a
```

### Backups Automatizados

Crear un cron job para backups diarios:

```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * docker exec leitor-email-db pg_dump -U postgres leitor_email_db | gzip > /backups/leitor_$(date +\%Y\%m\%d).sql.gz
```

### Logs de Aplicación

Los logs se almacenan en:
- **Backend Django:** stdout (ver con `docker-compose logs backend`)
- **Celery:** stdout (ver con `docker-compose logs celery`)
- **PostgreSQL:** `/var/lib/postgresql/data/log/` (dentro del contenedor)

---

## 📝 Notas de Desarrollo

### Desarrollo Local (sin Docker)

Si desea desarrollar sin Docker:

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

### Agregar Nueva Dependencia

**Python (Backend):**
```bash
# Agregar a requirements.txt
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

## 📞 Soporte

Para problemas o consultas:

- **Email:** soporte@amiria.com.py
- **Documentación:** Este README.md
- **Logs:** Siempre incluya logs al reportar problemas

---

## 📄 Licencia

Este proyecto es privado. Todos los derechos reservados © 2025.

**Uso autorizado únicamente para:** BOX Mayorista y empresas asociadas.

---

## 🔄 Actualizaciones

### Versión 1.0.0 (Actual)

- ✅ Lectura automática de emails via IMAP
- ✅ Procesamiento de XML de Factura Electrónica
- ✅ Interfaz web React
- ✅ Generación de PDFs
- ✅ Exportación a Excel
- ✅ Sistema multi-empresa

### Próximas Funcionalidades

- 🔄 Notificaciones por email
- 🔄 Dashboard de estadísticas avanzadas
- 🔄 API pública con autenticación
- 🔄 Integración con sistemas contables

---

**¡Sistema listo para usar! 🚀**