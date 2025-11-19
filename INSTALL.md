# 🚀 Guía de Instalación Rápida / Quick Installation Guide

## Español 🇪🇸

### 📋 Requisitos Previos

- [ ] Docker instalado (v20.10+)
- [ ] Docker Compose instalado (v2.0+)
- [ ] Git instalado
- [ ] 4GB RAM disponible
- [ ] 10GB espacio en disco

### 🔧 Instalación en 5 Pasos

#### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/seu-usuario/leitor-email.git
cd leitor-email
```

#### 2️⃣ Configurar Variables de Ambiente

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env
nano .env  # o usar vim, code, etc.
```

**Campos OBLIGATORIOS a cambiar:**
- `DB_PASSWORD` - Contraseña segura para PostgreSQL
- `SECRET_KEY` - Clave secreta de Django (generar nueva)
- `ALLOWED_HOSTS` - IP o dominio de tu servidor

**Generar SECRET_KEY:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 3️⃣ Construir las Imágenes

```bash
docker-compose build
```

⏱️ **Tiempo estimado:** 5-10 minutos (primera vez)

#### 4️⃣ Iniciar los Servicios

```bash
docker-compose up -d
```

**Verificar que todo está corriendo:**
```bash
docker-compose ps
```

Todos los servicios deben mostrar **STATUS: Up**

#### 5️⃣ Ejecutar Migraciones

```bash
docker exec -it leitor-email-backend python manage.py migrate
```

### ✅ Verificación de Instalación

Acceder a:

1. **Frontend:** http://10.1.1.4:4102/
   - Usuario: admin@admin.com
   - Contraseña: Admin@2525

2. **Backend Admin:** http://10.1.1.4:4101/admin
   - Usuario: admin
   - Contraseña: Admin@2525

Si puede acceder a ambas URLs, ¡la instalación fue exitosa! 🎉

---

## Português 🇧🇷

### 📋 Requisitos Prévios

- [ ] Docker instalado (v20.10+)
- [ ] Docker Compose instalado (v2.0+)
- [ ] Git instalado
- [ ] 4GB RAM disponível
- [ ] 10GB espaço em disco

### 🔧 Instalação em 5 Passos

#### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/leitor-email.git
cd leitor-email
```

#### 2️⃣ Configurar Variáveis de Ambiente

```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env
nano .env  # ou usar vim, code, etc.
```

**Campos OBRIGATÓRIOS para alterar:**
- `DB_PASSWORD` - Senha segura para PostgreSQL
- `SECRET_KEY` - Chave secreta do Django (gerar nova)
- `ALLOWED_HOSTS` - IP ou domínio do seu servidor

**Gerar SECRET_KEY:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 3️⃣ Construir as Imagens

```bash
docker-compose build
```

⏱️ **Tempo estimado:** 5-10 minutos (primeira vez)

#### 4️⃣ Iniciar os Serviços

```bash
docker-compose up -d
```

**Verificar se tudo está rodando:**
```bash
docker-compose ps
```

Todos os serviços devem mostrar **STATUS: Up**

#### 5️⃣ Executar Migrações

```bash
docker exec -it leitor-email-backend python manage.py migrate
```

### ✅ Verificação da Instalação

Acessar:

1. **Frontend:** http://10.1.1.4:4102/
   - Usuário: admin@admin.com
   - Senha: Admin@2525

2. **Backend Admin:** http://10.1.1.4:4101/admin
   - Usuário: admin
   - Senha: Admin@2525

Se conseguir acessar ambas as URLs, a instalação foi bem-sucedida! 🎉

---

## 🔧 Solución de Problemas Comunes / Problemas Comuns

### Error: "Puerto ya en uso" / "Port already in use"

```bash
# Ver qué está usando el puerto
sudo lsof -i :4101  # o 4102, 4103, 5436, 6381

# Cambiar puertos en docker-compose.yml si es necesario
# Alterar portas no docker-compose.yml se necessário
```

### Error: "Cannot connect to Docker daemon"

```bash
# Iniciar Docker / Iniciar o Docker
sudo systemctl start docker

# Agregar usuario al grupo docker / Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Backend no inicia / Backend não inicia

```bash
# Ver logs / Ver logs
docker-compose logs backend

# Reiniciar servicio / Reiniciar serviço
docker-compose restart backend
```

### Base de datos no conecta / Banco de dados não conecta

```bash
# Verificar que PostgreSQL está corriendo / Verificar se PostgreSQL está rodando
docker-compose ps db

# Ver logs / Ver logs
docker-compose logs db

# Reiniciar / Reiniciar
docker-compose restart db
```

---

## 📚 Siguiente Paso / Próximo Passo

Consulta la documentación completa en tu idioma:

Consulte a documentação completa no seu idioma:

- **[🇪🇸 Español](./README.es.md)**
- **[🇧🇷 Português](./README.pt-BR.md)**

---

## 🆘 Soporte / Suporte

- 📧 Email: soporte@amiria.com.py
- 📖 Documentación completa / Documentação completa: Ver READMEs

**¡Instalación completada con éxito! / Instalação concluída com sucesso!** 🚀