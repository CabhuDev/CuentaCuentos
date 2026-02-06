# Voces Gratuitas Disponibles - ElevenLabs

## 🎤 Voces Recomendadas para Narración de Cuentos

### ⭐ Top 3 para CuentaCuentos

#### 1. **George** (CONFIGURADA POR DEFECTO)
- **ID:** `JBFqnCBsd6RMkjVDRZzb`
- **Descripción:** Warm, Captivating Storyteller
- **Acento:** British
- **Género:** Male
- **Edad:** Middle-aged
- **Uso:** Narrative/Story
- **✅ RECOMENDADA:** Excelente para narración de cuentos infantiles

#### 2. **Sarah**
- **ID:** `EXAVITQu4vr4xnSDxMaL`
- **Descripción:** Mature, Reassuring, Confident
- **Acento:** American
- **Género:** Female
- **Edad:** Young
- **Uso:** Entertainment/TV

#### 3. **Alice**
- **ID:** `Xb7hH8MSUJpSbSDYk0k2`
- **Descripción:** Clear, Engaging Educator
- **Acento:** British
- **Género:** Female
- **Edad:** Middle-aged
- **Uso:** Informative/Educational

---

## 📋 Lista Completa de Voces Gratuitas (Plan Free)

### Voces Masculinas

| Nombre | Voice ID | Descripción | Acento | Uso Recomendado |
|--------|----------|-------------|--------|-----------------|
| **George** ⭐ | `JBFqnCBsd6RMkjVDRZzb` | Warm, Captivating Storyteller | British | **Narrativa/Cuentos** |
| Roger | `CwhRBWXzGAHq8TQ4Fs17` | Laid-Back, Casual, Resonant | American | Conversacional |
| Charlie | `IKne3meq5aSn9XLyUdCD` | Deep, Confident, Energetic | Australian | Conversacional |
| Callum | `N2lVS1w4EtoT3dr4eOWO` | Husky Trickster | American | Animación/Personajes |
| Harry | `SOYHLrjzK2X1ezoPC6cr` | Fierce Warrior | American | Animación/Personajes |
| Liam | `TX3LPaxmHKxFdv7VOQHJ` | Energetic, Social Media Creator | American | Redes Sociales |
| Will | `bIHbv24MWmeRgasZH58o` | Relaxed Optimist | American | Conversacional |
| Eric | `cjVigY5qzO86Huf0OWal` | Smooth, Trustworthy | American | Conversacional |
| Chris | `iP95p4xoKVk53GoZ742B` | Charming, Down-to-Earth | American | Conversacional |
| Brian | `nPczCjzI2devNBz1zQrb` | Deep, Resonant and Comforting | American | Redes Sociales |
| Daniel | `onwK4e9ZLuTAKqWW03F9` | Steady Broadcaster | British | Informativo/Educativo |
| Adam | `pNInz6obpgDQGcFmaJgB` | Dominant, Firm | American | Redes Sociales |
| Bill | `pqHfZKP75CvOlQylNhV4` | Wise, Mature, Balanced | American | Publicidad |

### Voces Femeninas

| Nombre | Voice ID | Descripción | Acento | Uso Recomendado |
|--------|----------|-------------|--------|-----------------|
| **Alice** ⭐ | `Xb7hH8MSUJpSbSDYk0k2` | Clear, Engaging Educator | British | **Informativo/Educativo** |
| **Sarah** ⭐ | `EXAVITQu4vr4xnSDxMaL` | Mature, Reassuring, Confident | American | **Entertainment/TV** |
| Laura | `FGY2WhTYpPnrIDTdsKH5` | Enthusiast, Quirky Attitude | American | Redes Sociales |
| Matilda | `XrExE9yKIg1WjnnlVkGX` | Knowledgable, Professional | American | Informativo/Educativo |
| Jessica | `cgSgspJ2msm6clMCkdW9` | Playful, Bright, Warm | American | Conversacional |
| Bella | `hpp4J3VqNfWAUOO0d1Us` | Professional, Bright, Warm | American | Informativo/Educativo |
| Lily | `pFZP5JQG7iQjIQuC4Bku` | Velvety Actress | British | Informativo/Educativo |

### Voces Neutrales

| Nombre | Voice ID | Descripción | Acento | Uso Recomendado |
|--------|----------|-------------|--------|-----------------|
| River | `SAz9YHcvj6GT2YYXdXww` | Relaxed, Neutral, Informative | American | Conversacional |

---

## 🔒 Voces Pro (Requieren Plan de Pago)

### Voces en Español (No disponibles en plan gratuito)

| Nombre | Voice ID | Descripción | Acento |
|--------|----------|-------------|--------|
| Elena | `tXgbXPnsMpKXkuTgvE3h` | Stories and Narrations | Peninsular |
| JeiJo | `PBaBRSRTvwmnK1PAq9e0` | Confident | Castilian |
| Martin Osborne 2 | `Vpv1YgvVd6CHIzOTiTt8` | Deep | Peninsular |

---

## 💡 Recomendaciones

### Para Cuentos Infantiles:
1. **George** - Narrador cálido y cautivador
2. **Sarah** - Voz materna reconfortante
3. **Alice** - Educadora clara

### Para Diferentes Edades:
- **3-6 años:** Jessica (Playful, Bright)
- **7-10 años:** George (Captivating Storyteller)
- **10+ años:** Alice (Clear Educator)

### Para Diferentes Géneros:
- **Aventuras:** George, Charlie
- **Cuentos de Hadas:** Sarah, Lily
- **Educativos:** Alice, Matilda
- **Cómicos:** Jessica, Laura

---

## 🔧 Cómo Cambiar la Voz

### Opción 1: Cambiar la voz por defecto
Edita `backend/.env`:
```env
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb  # Cambia este ID
```

### Opción 2: Cambiar voz por cuento (próximamente)
Cuando implementemos el endpoint, podrás especificar:
```json
{
  "voice_id": "EXAVITQu4vr4xnSDxMaL"  // Sarah
}
```

---

## 📊 Límites del Plan Gratuito

- **Caracteres:** 10,000 / mes
- **Voces:** 21 voces gratuitas + voces clonadas
- **Calidad:** MP3 hasta 128kbps
- **Idiomas:** Las voces gratuitas hablan español con acento

---

## 🎯 Nota sobre Español

Aunque las voces gratuitas son en inglés, **funcionan perfectamente para narrar en español**. El modelo `eleven_multilingual_v2` hace que las voces se adapten al idioma del texto manteniendo su carácter distintivo.

**Resultado:** Cuentos en español con calidad profesional ✅
