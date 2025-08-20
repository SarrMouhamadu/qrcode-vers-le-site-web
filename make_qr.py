#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Générateur de QR Code de qualité professionnelle pour une URL.
- Par défaut cible: https://artbeaurescence.sn
- Sorties: PNG (raster) et/ou SVG (vectoriel)
- ECC (correction d'erreurs) configurable
- Validation de l'URL + vérification (optionnelle) de disponibilité en ligne

Usage exemples:
  python make_qr.py
  python make_qr.py --url https://artbeaurescence.sn --png artbeaurescence_qr.png
  python make_qr.py --svg artbeaurescence_qr.svg --ec-level H --border 4 --box-size 10
"""

from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import urllib.request
import sys

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
    # Facultatif pour SVG (inclus dans qrcode)
    from qrcode.image.svg import SvgImage
except ImportError as e:
    print(
        "Le module 'qrcode' est requis.\n"
        "Installez-le avec:  pip install \"qrcode[pil]\"\n"
        f"Détail: {e}",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------
# Configuration & Validation
# ---------------------------
@dataclass(frozen=True)
class QRConfig:
    url: str = "https://artbeaurescence.sn"
    box_size: int = 10          # taille d’un module (pixel) - PNG
    border: int = 4             # marge (modules) autour du code
    ec_level: str = "Q"         # L, M, Q, H (Q = robuste, H = très robuste)
    fill_color: str = "black"
    back_color: str = "white"
    png_path: Optional[Path] = Path("artbeaurescence_qr.png")
    svg_path: Optional[Path] = None  # Path("artbeaurescence_qr.svg") si besoin
    check_online: bool = True
    timeout_s: float = 5.0


def _map_ec_level(level: str):
    level = (level or "Q").strip().upper()
    mapping = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
    if level not in mapping:
        raise ValueError(f"Niveau ECC invalide: {level}. Choisir parmi L, M, Q, H.")
    return mapping[level]


def validate_url(url: str) -> None:
    """Vérifie la forme générale de l’URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"URL invalide: {url!r}. Exemple valide: https://exemple.com")


def check_reachability(url: str, timeout: float = 5.0) -> bool:
    """
    Envoie une requête HEAD (sans télécharger la page).
    Retourne True si le serveur répond (2xx/3xx), False sinon.
    NB: le QR code reste valide même si ce test échoue ; il n'encode que l’URL.
    """
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "qr-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Codes 2xx/3xx considérés OK
            return 200 <= getattr(resp, "status", 200) < 400
    except Exception:
        return False


# ---------------------------
# Génération QR
# ---------------------------
def make_qr_png(cfg: QRConfig) -> Optional[Path]:
    if cfg.png_path is None:
        return None
    ec = _map_ec_level(cfg.ec_level)

    qr = qrcode.QRCode(
        version=None,              # laisse la lib optimiser la version selon les données
        error_correction=ec,
        box_size=cfg.box_size,
        border=cfg.border,
    )
    qr.add_data(cfg.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=cfg.fill_color, back_color=cfg.back_color)
    cfg.png_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(cfg.png_path)
    return cfg.png_path


def make_qr_svg(cfg: QRConfig) -> Optional[Path]:
    if cfg.svg_path is None:
        return None
    ec = _map_ec_level(cfg.ec_level)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=cfg.box_size,  # ignoré pour SVG mais gardé pour cohérence
        border=cfg.border,
    )
    qr.add_data(cfg.url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=SvgImage)
    cfg.svg_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(cfg.svg_path)
    return cfg.svg_path


# ---------------------------
# CLI
# ---------------------------
def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Générer un QR Code pour une URL.")
    p.add_argument("--url", default="https://artbeaurescence.sn", help="URL à encoder dans le QR.")
    p.add_argument("--png", default="artbeaurescence_qr.png", help="Chemin du PNG de sortie (ou laissez vide pour désactiver).")
    p.add_argument("--svg", default="", help="Chemin du SVG de sortie (vide pour désactiver).")
    p.add_argument("--ec-level", default="Q", choices=list("LMQH"), help="Niveau de correction d’erreurs: L/M/Q/H.")
    p.add_argument("--box-size", type=int, default=10, help="Taille d’un module (pixels) pour PNG.")
    p.add_argument("--border", type=int, default=4, help="Marge (en modules).")
    p.add_argument("--no-check", action="store_true", help="Ne pas vérifier la disponibilité en ligne de l’URL.")
    p.add_argument("--timeout", type=float, default=5.0, help="Timeout (s) de la vérification en ligne.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    png_path = Path(args.png).resolve() if args.png.strip() else None
    svg_path = Path(args.svg).resolve() if args.svg.strip() else None

    try:
        validate_url(args.url)
    except ValueError as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        return 2

    if not args.no_check:
        reachable = check_reachability(args.url, timeout=args.timeout)
        status = "OK" if reachable else "NON JOIGNABLE"
        print(f"[Info] Vérification en ligne de l’URL: {status}")
        # On continue même si le site ne répond pas, car le QR encode l’URL.

    cfg = QRConfig(
        url=args.url,
        box_size=args.box_size,
        border=args.border,
        ec_level=args.ec_level,
        png_path=png_path,
        svg_path=svg_path,
        check_online=not args.no_check,
        timeout_s=args.timeout,
    )

    out_png = make_qr_png(cfg)
    out_svg = make_qr_svg(cfg)

    if out_png:
        print(f"[OK] PNG généré: {out_png}")
    if out_svg:
        print(f"[OK] SVG généré: {out_svg}")

    if not out_png and not out_svg:
        print("[ATTENTION] Aucune sortie demandée (ni PNG ni SVG). Utilisez --png ou --svg.", file=sys.stderr)
        return 1

    print("[Terminé] Le QR code pointera vers l’URL encodée. Il restera valable tant que cette URL restera accessible en ligne.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
