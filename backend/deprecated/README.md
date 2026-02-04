# Archivos Obsoletos / Deprecated

Esta carpeta contiene código que ya no se usa en la aplicación actual pero se conserva como referencia histórica.

## 📁 Archivos Movidos Aquí

### `main_old.py` (425 líneas)
- **Obsoleto desde:** Migración a arquitectura API-First
- **Razón:** Versión monolítica antigua con lógica mezclada
- **Reemplazado por:** 
  - `main.py` (API REST pura)
  - Routers modulares en `/routers`
  - Servicios en `/services`

### `database_postgres.py` (112 líneas)
- **Obsoleto desde:** Migración a SQLite para desarrollo
- **Razón:** Duplicado en la raíz del proyecto, requiere PostgreSQL
- **Reemplazado por:** `models/database_sqlite.py`
- **Nota:** Puede restaurarse si necesitas PostgreSQL con pgvector

### `database_postgres_models.py` (94 líneas)
- **Obsoleto desde:** Migración a SQLite para desarrollo
- **Razón:** Modelos diseñados específicamente para PostgreSQL con pgvector
- **Reemplazado por:** `models/database_sqlite.py`
- **Diferencias clave:**
  - Usa `Vector` de pgvector (PostgreSQL)
  - Usa `UUID` nativo de PostgreSQL
  - Requiere extensión pgvector instalada

## 🔄 Si necesitas volver a PostgreSQL

1. Copia `database_postgres_models.py` a `models/database.py`
2. Actualiza imports en routers de `database_sqlite` a `database`
3. Configura PostgreSQL y pgvector:
   ```sql
   CREATE EXTENSION vector;
   ```
4. Actualiza `.env`:
   ```env
   DATABASE_URL=postgresql://usuario:password@localhost/cuentacuentos_db
   ```

## ⚠️ No eliminar estos archivos

Se conservan como:
- Referencia de implementación PostgreSQL
- Backup del código funcional
- Documentación de decisiones técnicas
- Facilitar rollback si es necesario

---
**Última actualización:** 4 de febrero de 2026  
**Contexto:** Migración de PostgreSQL a SQLite para simplificar desarrollo local
