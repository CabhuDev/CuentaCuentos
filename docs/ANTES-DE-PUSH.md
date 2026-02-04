# 🔒 ANTES DE SUBIR A GITHUB

## Checklist Rápido

```powershell
# 1. Ejecuta auditoría de seguridad
.\audit-security.ps1

# 2. Si todo está OK, añade cambios
git add .

# 3. Verifica qué archivos se van a subir
git status

# 4. Confirma que NO veas:
#    - backend/.env
#    - backend/*.db
#    - backend/.venv/
#    - __pycache__/

# 5. Haz commit
git commit -m "tu mensaje descriptivo"

# 6. Sube a GitHub
git push origin main
```

## ⚠️ Si ves archivos sensibles

```powershell
# Quitar del staging
git reset HEAD backend/.env
git reset HEAD backend/*.db

# Verificar .gitignore
cat .gitignore

# Volver a intentar
git status
```

## 🆘 Si YA subiste una clave

1. **REGENERA** tu API key inmediatamente en: https://aistudio.google.com/app/apikey
2. Actualiza `backend/.env` con la nueva clave
3. Lee [SECURITY.md](SECURITY.md) sección "Si expones accidentalmente una clave"

## ✅ Archivos Seguros

Solo estos tipos de archivos deben subirse:
- `.py` - Código Python
- `.js`, `.html`, `.css` - Frontend
- `.md` - Documentación  
- `.json` - Configuración (SIN claves)
- `.ps1` - Scripts
- `.gitignore` - Configuración git
- `requirements.txt` - Dependencias
- `.env.example` - Plantilla SIN claves reales

## 📖 Más Info

- [SECURITY.md](SECURITY.md) - Guía completa de seguridad
- [README.md](README.md) - Documentación principal
