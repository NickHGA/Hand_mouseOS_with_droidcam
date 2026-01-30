# RemoteCam Virtual Webcam - Architecture

## Vue d'ensemble

Ce projet transforme un téléphone en webcam système utilisable par n'importe quelle application (Zoom, OBS, Meet, Teams, etc.).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHONE                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        RemoteCam App                                │   │
│  │                                                                     │   │
│  │  Camera ────► Encoder ────► HTTP Server (port 8080)                │   │
│  │                              │                                      │   │
│  │                              ▼                                      │   │
│  │                   MJPEG Stream: /video                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ WiFi / LAN
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                PC                                           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Transport Layer                                    │  │
│  │                                                                       │  │
│  │   HTTP Client (FFmpeg / OpenCV / curl)                               │  │
│  │        │                                                              │  │
│  │        ▼                                                              │  │
│  │   MJPEG Decoder                                                       │  │
│  │        │                                                              │  │
│  │        ▼                                                              │  │
│  │   Raw Video Frames (BGR / YUV)                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  Processing Layer (Optional)                          │  │
│  │                                                                       │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │  │
│  │   │   Resize    │  │    Flip     │  │  Filters    │                  │  │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                  │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │         Hand Tracking / Face Detection (MediaPipe)          │    │  │
│  │   └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  Virtualization Layer                                 │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────┐   ┌─────────────────────────────────┐  │  │
│  │   │        LINUX            │   │           WINDOWS               │  │  │
│  │   │                         │   │                                 │  │  │
│  │   │   v4l2loopback driver   │   │   DirectShow Virtual Camera    │  │  │
│  │   │         │               │   │            │                   │  │  │
│  │   │         ▼               │   │            ▼                   │  │  │
│  │   │   /dev/video10          │   │   "OBS Virtual Camera"         │  │  │
│  │   │                         │   │   "AK Virtual Camera"          │  │  │
│  │   └─────────────────────────┘   └─────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  Application Layer                                    │  │
│  │                                                                       │  │
│  │   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │  │
│  │   │  Zoom  │  │  Meet  │  │ Teams  │  │  OBS   │  │ Chrome │        │  │
│  │   └────────┘  └────────┘  └────────┘  └────────┘  └────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Composants

### 1. RemoteCam (Source)
- **Rôle**: Capture vidéo du téléphone et expose un flux HTTP
- **Protocole**: MJPEG over HTTP
- **URL type**: `http://<PHONE_IP>:8080/video`
- **Note**: RemoteCam ne crée PAS de webcam système, c'est juste un transport

### 2. Transport Layer (Réception)
- **FFmpeg**: Solution recommandée, stable et performante
- **OpenCV**: Solution Python, flexible pour ajouter du traitement
- **Fonction**: Récupère le flux MJPEG et décode les frames

### 3. Processing Layer (Traitement - Optionnel)
- Redimensionnement
- Rotation / Flip
- Filtres visuels
- **Hand Tracking** avec MediaPipe
- Face Detection, etc.

### 4. Virtualization Layer (Sortie)

#### Linux: v4l2loopback
```bash
# Installation
sudo apt install v4l2loopback-dkms

# Chargement
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="RemoteCam"

# Résultat: /dev/video10
```

#### Windows: DirectShow
- **OBS Virtual Camera**: Solution la plus simple
- **akvcam**: Solution open-source avancée
- **Unity Capture**: Alternative DirectShow

### 5. Application Layer (Utilisation)
- Toute application qui utilise une webcam peut voir le device virtuel
- Aucune modification nécessaire côté applications

## Pipelines

### Pipeline FFmpeg (Linux)
```bash
ffmpeg -f mjpeg -i http://PHONE:8080/video -pix_fmt yuyv422 -f v4l2 /dev/video10
```

### Pipeline FFmpeg (Windows avec OBS)
1. OBS reçoit le flux via "Browser Source" ou "VLC Source"
2. OBS expose "OBS Virtual Camera"
3. Les apps sélectionnent "OBS Virtual Camera"

### Pipeline Python
```python
cap = cv2.VideoCapture("http://PHONE:8080/video")
out = cv2.VideoWriter("/dev/video10", fourcc, 30, (640, 480))

while True:
    ret, frame = cap.read()
    # Traitement optionnel...
    out.write(frame)
```

## Avantages de cette architecture

1. **Modulaire**: Chaque couche est indépendante
2. **Cross-platform**: Même logique Linux/Windows
3. **Extensible**: Facile d'ajouter du traitement vidéo
4. **Standard**: Utilise des protocoles et APIs standards
5. **Sans logiciel propriétaire**: Solutions 100% open-source disponibles

## Flux de données

```
Camera → MJPEG → HTTP → Decode → Process → Encode → Virtual Device → Apps
        (phone)    (network)         (PC - optionnel)      (OS driver)
```

## Latence typique

| Étape | Latence |
|-------|---------|
| Capture caméra | ~10ms |
| Encodage MJPEG | ~5-10ms |
| Transmission WiFi | ~10-50ms |
| Décodage | ~5ms |
| Traitement (si activé) | ~10-50ms |
| Virtualisation | ~5ms |
| **Total** | **~50-130ms** |
