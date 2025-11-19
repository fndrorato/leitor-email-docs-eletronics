# 🔧 Referencia Rápida de Comandos / Quick Command Reference

Comandos útiles para gestión diaria del sistema.

Comandos úteis para gestão diária do sistema.

---

## 🐳 Docker Compose

### Gestión Básica / Gestão Básica

```bash
# Iniciar todos los servicios / Iniciar todos os serviços
docker-compose up -d

# Detener todos los servicios / Parar todos os serviços
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA DATOS)
# Parar e remover volumes (⚠️ APAGA DADOS)
docker-compose down -v

# Ver estado de servicios / Ver status dos serviços
docker-compose ps

# Ver uso de recursos / Ver uso de recursos
docker stats
```

### Logs y Monitoreo / Logs e Monitoramento

```bash
# Ver logs de todos los servicios / Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de un servicio específico / Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f beat
docker-compose logs -f frontend
docker-compose logs -f pdf

# Ver últimas 100 líneas / Ver últimas 100 linhas
docker-compose logs --tail=100 backend

# Logs desde una fecha específica / Logs desde uma data específica
docker-compose logs --since="2025-10-01" backend
```

### Reiniciar Servicios / Reiniciar Serviços

```bash
# Reiniciar todos los servicios / Reiniciar todos os serviços
docker-compose restart

# Reiniciar servicio específico / Reiniciar serviço específico
docker-compose restart backend
docker-compose restart celery
docker-compose restart beat
docker-compose restart frontend

# Reconstruir imagen y reiniciar / Reconstruir imagem e reiniciar
docker-compose build backend
docker-compose up -d backend
```

---

## 🎨 Django (Backend)

### Migraciones / Migrações

```bash
# Crear migraciones / Criar migrações
docker exec -it leitor-email-backend python manage.py makemigrations

# Aplicar migraciones / Aplicar migrações
docker exec -it leitor-email-backend python manage.py migrate

# Ver estado de migraciones / Ver estado de migrações
docker exec -it leitor-email-backend python manage.py showmigrations

# Revertir migración / Reverter migração
docker exec -it leitor-email-backend python manage.py migrate app_name migration_name
```

### Gestión de Usuarios / Gestão de Usuários

```bash
# Crear superusuario / Criar superusuário
docker exec -it leitor-email-backend python manage.py createsuperuser

# Cambiar contraseña de usuario / Alterar senha de usuário
docker exec -it leitor-email-backend python manage.py changepassword username
```

### Shell y Desarrollo / Shell e Desenvolvimento

```bash
# Abrir shell de Django / Abrir shell do Django
docker exec -it leitor-email-backend python manage.py shell

# Abrir shell de Python / Abrir shell de Python
docker exec -it leitor-email-backend python

# Ejecutar script Python / Executar script Python
docker exec -it leitor-email-backend python manage.py shell < script.py
```

### Tests

```bash
# Ejecutar todos los tests / Executar todos os testes
docker exec -it leitor-email-backend python manage.py test

# Ejecutar tests de una app específica / Executar testes de um app específico
docker exec -it leitor-email-backend python manage.py test documentos

# Tests con cobertura / Testes com cobertura
docker exec -it leitor-email-backend coverage run manage.py test
docker exec -it leitor-email-backend coverage report
```

### Archivos Estáticos / Arquivos Estáticos

```bash
# Recolectar archivos estáticos / Coletar arquivos estáticos
docker exec -it leitor-email-backend python manage.py collectstatic --no-input

# Limpiar archivos estáticos / Limpar arquivos estáticos
docker exec -it leitor-email-backend python manage.py collectstatic --clear --no-input
```

---

## 🔄 Celery

### Monitoreo / Monitoramento

```bash
# Ver tareas activas / Ver tarefas ativas
docker exec -it leitor-email-celery celery -A app inspect active

# Ver tareas programadas / Ver tarefas agendadas
docker exec -it leitor-email-celery celery -A app inspect scheduled

# Ver tareas reservadas / Ver tarefas reservadas
docker exec -it leitor-email-celery celery -A app inspect reserved

# Ver estadísticas / Ver estatísticas
docker exec -it leitor-email-celery celery -A app inspect stats
```

### Gestión de Workers / Gestão de Workers

```bash
# Ver workers activos / Ver workers ativos
docker exec -it leitor-email-celery celery -A app inspect active_queues

# Cancelar todas las tareas / Cancelar todas as tarefas
docker exec -it leitor-email-celery celery -A app purge

# Reiniciar workers / Reiniciar workers
docker-compose restart celery beat
```

---

## 🗄️ PostgreSQL

### Acceso a Base de Datos / Acesso ao Banco de Dados

```bash
# Conectar a PostgreSQL / Conectar ao PostgreSQL
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db

# Conectar como usuario específico / Conectar como usuário específico
docker exec -it leitor-email-db psql -U postgres
```

### Backup y Restauración / Backup e Restauração

```bash
# Hacer backup / Fazer backup
docker exec -it leitor-email-db pg_dump -U postgres leitor_email_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido / Backup comprimido
docker exec -it leitor-email-db pg_dump -U postgres leitor_email_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Restaurar desde backup / Restaurar de backup
docker exec -i leitor-email-db psql -U postgres -d leitor_email_db < backup.sql

# Restaurar desde backup comprimido / Restaurar de backup comprimido
gunzip -c backup.sql.gz | docker exec -i leitor-email-db psql -U postgres -d leitor_email_db
```

### Consultas Útiles / Consultas Úteis

```bash
# Ver tamaño de base de datos / Ver tamanho do banco de dados
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT pg_size_pretty(pg_database_size('leitor_email_db'));"

# Ver tamaño de tablas / Ver tamanho das tabelas
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT 
  schemaname, 
  tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;"

# Contar registros de una tabla / Contar registros de uma tabela
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT COUNT(*) FROM documentos_documento;"

# Ver conexiones activas / Ver conexões ativas
docker exec -it leitor-email-db psql -U postgres -d leitor_email_db -c "
SELECT * FROM pg_stat_activity;"
```

---

## 📦 Redis

### Monitoreo / Monitoramento

```bash
# Verificar conexión / Verificar conexão
docker exec -it leitor-email-redis redis-cli ping
# Debe responder: PONG / Deve responder: PONG

# Ver información del servidor / Ver informação do servidor
docker exec -it leitor-email-redis redis-cli info

# Ver estadísticas de memoria / Ver estatísticas de memória
docker exec -it leitor-email-redis redis-cli info memory

# Ver todas las claves / Ver todas as chaves
docker exec -it leitor-email-redis redis-cli keys "*"

# Contar claves / Contar chaves
docker exec -it leitor-email-redis redis-cli dbsize
```

### Limpieza / Limpeza

```bash
# Limpiar todas las claves (⚠️ CUIDADO)
# Limpar todas as chaves (⚠️ CUIDADO)
docker exec -it leitor-email-redis redis-cli flushall

# Limpiar base de datos actual / Limpar banco de dados atual
docker exec -it leitor-email-redis redis-cli flushdb
```

---

## 📊 Frontend (React)

### Desarrollo / Desenvolvimento

```bash
# Ver logs / Ver logs
docker-compose logs -f frontend

# Reconstruir frontend / Reconstruir frontend
docker-compose build frontend
docker-compose up -d frontend

# Acceder al contenedor / Acessar o container
docker exec -it leitor-email-frontend sh

# Ver archivos build / Ver arquivos build
docker exec -it leitor-email-frontend ls -la /app/dist
```

---

## 🔒 Seguridad / Segurança

### Generar Claves / Gerar Chaves

```bash
# Generar SECRET_KEY para Django / Gerar SECRET_KEY para Django
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generar password seguro / Gerar senha segura
openssl rand -base64 32

# Hash de password Django / Hash de senha Django
docker exec -it leitor-email-backend python manage.py shell -c "
from django.contrib.auth.hashers import make_password
print(make_password('your_password'))"
```

### Permisos / Permissões

```bash
# Ajustar permisos del proyecto / Ajustar permissões do projeto
sudo chown -R $USER:$USER .

# Dar permisos de ejecución / Dar permissões de execução
chmod +x server/entrypoint.sh
```

---

## 🧹 Limpieza / Limpeza

### Docker

```bash
# Ver espacio usado / Ver espaço usado
docker system df

# Limpiar contenedores detenidos / Limpar containers parados
docker container prune

# Limpiar imágenes no usadas / Limpar imagens não usadas
docker image prune

# Limpiar todo (⚠️ CUIDADO) / Limpar tudo (⚠️ CUIDADO)
docker system prune -a

# Limpiar volúmenes no usados / Limpar volumes não usados
docker volume prune
```

### Logs de Django / Logs do Django

```bash
# Dentro del shell de Django / Dentro do shell do Django
docker exec -it leitor-email-backend python manage.py shell

# Limpiar logs antiguos (ejemplo) / Limpar logs antigos (exemplo)
>>> from documentos.models import Log
>>> from datetime import datetime, timedelta
>>> fecha_limite = datetime.now() - timedelta(days=30)
>>> Log.objects.filter(created_at__lt=fecha_limite).delete()
>>> exit()
```

---

## 📝 Utilidades / Utilidades

### Exportar Variables de Entorno / Exportar Variáveis de Ambiente

```bash
# Cargar .env en la sesión actual / Carregar .env na sessão atual
export $(cat .env | xargs)

# Ver variable específica / Ver variável específica
echo $DB_NAME
```

### Monitoreo de Recursos / Monitoramento de Recursos

```bash
# Ver uso de CPU y memoria / Ver uso de CPU e memória
docker stats --no-stream

# Ver uso continuo / Ver uso contínuo
docker stats

# Ver solo un servicio / Ver apenas um serviço
docker stats leitor-email-backend
```

### Network

```bash
# Ver redes Docker / Ver redes Docker
docker network ls

# Inspeccionar red / Inspecionar rede
docker network inspect leitor-email_default

# Ver IPs de contenedores / Ver IPs dos containers
docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q)
```

---

## 🆘 Comandos de Emergencia / Comandos de Emergência

```bash
# Detener todo inmediatamente / Parar tudo imediatamente
docker-compose kill

# Eliminar todo y empezar de cero (⚠️ BORRA TODO)
# Remover tudo e começar do zero (⚠️ APAGA TUDO)
docker-compose down -v
docker system prune -a -f
docker-compose build
docker-compose up -d

# Ver todos los procesos de Docker / Ver todos os processos do Docker
docker ps -a

# Forzar eliminación de contenedor / Forçar remoção de container
docker rm -f container_name

# Ver logs de Docker daemon / Ver logs do Docker daemon
sudo journalctl -u docker -f
```

---

## 📚 Más Información / Mais Informações

- [README Español](./README.es.md)
- [README Português](./README.pt-BR.md)
- [Guía de Instalación](./INSTALL.md)

---

**💡 Tip:** Guarda este archivo como referencia rápida para el día a día.

**💡 Dica:** Salve este arquivo como referência rápida para o dia a dia.