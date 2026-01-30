# RemoteCam Virtual Webcam & Hand Mouse

Transforme ton téléphone en **webcam système** pour Zoom, Meet, OBS, etc., et en **souris virtuelle** contrôlée par la main !

## 🏗️ Architecture

```
[PHONE]                           [PC (Windows / Linux)]
RemoteCam App                     ├── 1. NETWORK & DISCOVERY
  └── MJPEG stream ──────────────►│    ├── Auto-detection (UDP/Scanning)
      (HTTP)                      │    └── Stream Capture (OpenCV)
                                  │
                                  ├── 2. PROCESSING LAYER
                                  │    ├── Video Filters (Rotate, Blur, Vintage...)
                                  │    └── HAND TRACKING (MediaPipe) ────► [MOUSE CONTROL]
                                  │
                                  └── 3. VIRTUAL WEBCAM DRIVER
                                       ├── Linux: v4l2loopback
                                       └── Windows: pyvirtualcam / DirectShow
                                       │
                                       ▼
                                  [APPLICATIONS]
                                  (Zoom, OBS, Google Meet, Teams...)
```

## ✨ Fonctionnalités

- **Webcam Virtuelle** : Utilise ton téléphone comme caméra HD sans fil.
- **Auto-Détection** : Trouve automatiquement l'IP de ton téléphone sur le réseau.
- **Contrôle Souris (Hand Tracking)** 🖱️ : Contrôle ta souris avec l'index et clique en pinçant.
- **Filtres Vidéo** 🎨 : Rotation, Miroir, Flou, Vintage, Cartoon, etc.
- **Compatible** : Windows & Linux.

## 🚀 Installation

### Pré-requis communs (Python)
```bash
cd pc
pip install -r requirements.txt
```

### Linux
1. Installer le driver v4l2loopback :
   ```bash
   cd pc/linux
   sudo ./setup_v4l2loopback.sh
   ```

### Windows
1. Installer OBS Studio (pour le driver webcam virtuelle) ou utiliser le mode Preview seul.

## 🎮 Utilisation

### Mode Automatique (Recommandé)
Le script cherche ton téléphone et lance la webcam virtuelle :

```bash
# Windows
python pc/windows/remotecam_to_webcam.py --auto-detect --mouse-control

# Linux
python pc/linux/remotecam_to_webcam.py --auto-detect
```

### Mode Manuel
Si l'auto-détection échoue, spécifie l'IP (visible sur l'app RemoteCam) :

```bash
python pc/windows/remotecam_to_webcam.py -i 192.168.0.XX
```

### Options Utiles

| Option | Description |
|--------|-------------|
| `--mouse-control` | Active le contrôle de la souris par la main |
| `--preview` | Affiche une fenêtre de prévisualisation |
| `--rotate 90` | Tourne l'image (90, 180, 270) |
| `--grayscale` | Filtre Noir & Blanc |
| `--vintage` | Filtre effet ancien |
| `--blur 10` | Floute l'arrière-plan (simulé) |
| `--flip horizontal` | Miroir (utile pour la webcam) |

## 🖱️ Guide Contrôle Souris

1. Active l'option `--mouse-control`
2. Montre ta main à la caméra.
3. **Bouger** : Pointe avec l'**index**. La souris suit ton doigt.
4. **Cliquer** : Pince le **pouce et l'index** ensemble.

## ⚙️ Configuration Avancée

Tu peux modifier `pc/common/config.yaml` pour sauvegarder tes préférences :

```yaml
remotecam:
  phone_ip: "192.168.0.XX"  # Ton IP fixe
  scan_timeout: 2.0         # Durée scan réseau

video:
  width: 1280
  height: 720
  fps: 30

filters:
  enabled: []               # Liste: ['rotate', 'vintage']
  rotate_angle: 90
```

## 📁 Structure du projet

```
project/
├── phone/                  # Code Android (RemoteCam)
├── pc/
│   ├── common/             # Modules partagés (Scan, Config, Filtres, HandTracking)
│   ├── linux/              # Scripts Linux (Bash & Python)
│   ├── windows/            # Scripts Windows (Bat & Python)
│   └── requirements.txt    # Dépendances Python
└── docs/                   # Documentation technique
```