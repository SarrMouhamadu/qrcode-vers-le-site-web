#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
from urllib.parse import urlparse

import streamlit as st
from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import ERROR_CORRECT_H

st.set_page_config(page_title="Art'Beau-Rescence QR Generator", layout="centered")

st.title("Art'Beau-Rescence To-Do QR Generator")
st.caption("Colle ton lien → Clique → Télécharge ton QR brandé 🚀")

# -------- utilitaires --------
def is_valid_url(u: str) -> bool:
    try:
        p = urlparse(u.strip())
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False

def make_qr_colorized(url: str, logo_path: str = "logo.jpeg", alpha: int = 220) -> Image.Image:
    # Génération QR robuste
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_bw = qr.make_image(fill_color="black", back_color="white").convert("L")

    # Dégradé bleu/vert (couleurs Art’Beau-Rescence)
    color1 = (0, 150, 255, alpha)   # bleu
    color2 = (0, 200, 120, alpha)   # vert
    qr_color = Image.new("RGBA", qr_bw.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(qr_color)

    pixels = qr_bw.load()
    w, h = qr_bw.size
    for y in range(h):
        for x in range(w):
            if pixels[x, y] < 128:
                ratio = y / h
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.point((x, y), fill=(r, g, b, alpha))

    # Ajouter le logo centré
    try:
        logo = Image.open(logo_path).convert("RGBA")
        lw = int(qr_color.width * 0.22)
        logo.thumbnail((lw, lw))
        lx = (qr_color.width - logo.width) // 2
        ly = (qr_color.height - logo.height) // 2
        qr_color.alpha_composite(logo, (lx, ly))
    except Exception:
        pass  # si pas de logo, on ignore

    return qr_color

# -------- UI --------
url = st.text_input("Entre ton lien :", placeholder="https://artbeaurescence.sn/ai-karangue")

if st.button("🎨 Générer mon QR Art'Beau-Rescence"):
    if not is_valid_url(url):
        st.error("⚠️ Lien invalide. Exemple : https://artbeaurescence.sn/ai-karangue")
    else:
        img = make_qr_colorized(url)

        st.subheader("Ton QR code est prêt ✅")
        st.image(img, use_container_width=False)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(
            "⬇️ Télécharger le QR",
            data=buf.getvalue(),
            file_name="qrcode_artbeaurescence.png",
            mime="image/png",
        )
