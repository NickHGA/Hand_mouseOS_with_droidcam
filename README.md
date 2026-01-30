# RemoteCam Virtual Webcam

Transforme ton téléphone en webcam système pour Zoom, Meet, Teams, OBS, etc.

## 🏗️ Architecture

```
[PHONE]                           [PC]
RemoteCam App                     ├── Video Decoder (FFmpeg/OpenCV)
  └── MJPEG stream ──────────────►├── Virtual Webcam Driver
      (HTTP)                      │    ├── Linux: v4l2loopback
                                  │    └── Windows: DirectShow
                                  └── Applications (Zoom, OBS, Meet...)
```

## 📁 Structure du projet

```
project/
├── phone/
│   └── RemoteCam (app Android)
├── pc/
│   ├── linux/
│   │   ├── setup_v4l2loopback.sh    # Installe le driver webcam virtuelle
│   │   ├── remotecam_to_webcam.sh   # Script FFmpeg Linux
│   │   └── remotecam_to_webcam.py   # Script Python Linux
│   ├── windows/
│   │   ├── install_virtual_cam.ps1  # Guide d'installation Windows
│   │   ├── remotecam_to_webcam.bat  # Script batch Windows
│   │   └── remotecam_to_webcam.py   # Script Python Windows
│   └── common/
│       └── config.yaml              # Configuration partagée
└── docs/
    └── architecture.md              # Documentation technique
```

## 🐧 Linux - Guide Rapide

### 1. Installer la webcam virtuelle
```bash
cd pc/linux
chmod +x setup_v4l2loopback.sh
sudo ./setup_v4l2loopback.sh
```

### 2. Lancer le stream
```bash
chmod +x remotecam_to_webcam.sh
./remotecam_to_webcam.sh -i 192.168.1.100
```

Ou avec Python :
```bash
pip install opencv-python
python remotecam_to_webcam.py -i 192.168.1.100 --preview
```

### 3. Utiliser

La webcam `/dev/video10` est maintenant visible dans Zoom, OBS, etc.

## 🪟 Windows - Guide Rapide

### 1. Installer les dépendances
```powershell
# Exécuter en tant qu'administrateur
.\install_virtual_cam.ps1
```

Ou manuellement :
- **FFmpeg**: `winget install Gyan.FFmpeg`
- **OBS Studio**: https://obsproject.com/download

### 2. Méthode OBS (recommandée)

1. Ouvrir OBS Studio
2. Ajouter une source "VLC Video Source"
3. URL: `http://192.168.1.100:8080/video`
4. Cliquer "Start Virtual Camera"
5. Sélectionner "OBS Virtual Camera" dans Zoom/Meet

### 3. Méthode Python

```bash
pip install opencv-python pyvirtualcam
python remotecam_to_webcam.py -i 192.168.1.100 --preview
```

## ⚙️ Configuration

Éditer `pc/common/config.yaml` :

```yaml
remotecam:
  phone_ip: "192.168.1.100"  # IP de ton téléphone
  port: 8080                  # Port RemoteCam

video:
  width: 640
  height: 480
  fps: 30
```

## 🔧 Dépannage

### Problème: "Cannot connect to RemoteCam"

1. Vérifier que RemoteCam est lancé sur le téléphone
2. Vérifier que téléphone et PC sont sur le même réseau WiFi
3. Tester l'URL dans un navigateur: `http://192.168.1.100:8080/video`

### Problème: "Video device does not exist" (Linux)

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10
```

### Problème: "Virtual camera not available" (Windows)

1. Installer OBS Studio
2. Ouvrir OBS au moins une fois
3. Vérifier que Virtual Camera est activé dans les paramètres OBS

## 📝 Options en ligne de commande

### Linux (bash)
```bash
./remotecam_to_webcam.sh -i <IP> -p <PORT> -d /dev/videoX -r WxH
```

### Python (cross-platform)
```bash
python remotecam_to_webcam.py \
  -i 192.168.1.100 \
  --width 1280 --height 720 \
  --fps 30 \
  --flip horizontal \
  --preview
```

## 🎯 Ce que fait ce projet

✅ **Transport vidéo**: RemoteCam (téléphone → HTTP)
✅ **Virtualisation**: v4l2loopback / DirectShow (HTTP → Webcam système)
✅ **Cross-platform**: Linux & Windows
✅ **Open source**: Aucun logiciel propriétaire requis