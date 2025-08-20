# QR Code vers artbeaurescence.sn

Ce projet Python permet de générer un QR Code qui pointe vers le site https://artbeaurescence.sn.  
Le QR code restera valide tant que le site est accessible en ligne.

## Fonctionnalités
- Génération de QR code en PNG (bitmap) ou SVG (vectoriel).
- Vérification optionnelle de la disponibilité du site.
- Niveaux de correction d’erreur L, M, Q, H.
- Personnalisation des couleurs (avant-plan, arrière-plan).

## Prérequis
- Python 3.13.3
- Installation des dépendances :
```bash
pip install -r requirements.txt

git clone https://github.com/SarrMouhamadu/qrcode-vers-le-site-web.git
cd qrcode-vers-le-site-web
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt

python make_qr.py

Génération en SVG (vectoriel) avec correction maximale :
python make_qr.py --svg artbeaurescence_qr.svg --ec-level H
Structure du projet
qrcode-vers-le-site-web/
│── make_qr.py
│── requirements.txt
│── .gitignore
│── README.md
Licence
Projet open source, libre de réutilisation et de modification.
Développé par SarrMouhamadu
