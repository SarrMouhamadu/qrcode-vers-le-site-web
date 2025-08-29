import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import QRCode from 'qrcode';
import jsPDF from 'jspdf';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
})
export class App {
  // Champs du formulaire
  url: string = 'https://artbeaurescence.sn/ai-karangue';
  withLogo: boolean = true;
  quietZone: number = 2;
  gradientTop: string = '#0096ff';
  gradientBottom: string = '#00c878';

  // Rendu courant (aperçu)
  qrDataUrl: string | null = null;

  toNumber(val: any): number { return Number(val); }

  /** Charge une image (logo) */
  private loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  /** Génère un canvas QR brandé à la taille souhaitée (pixels) */
  private async renderCanvas(size: number): Promise<HTMLCanvasElement> {
    // 1) masque QR (modules opaques, fond transparent)
    const mask = document.createElement('canvas');
    mask.width = size; mask.height = size;
    await QRCode.toCanvas(mask, this.url.trim(), {
      errorCorrectionLevel: 'H',
      margin: this.quietZone,
      width: size,
      color: { dark: '#000000', light: '#00000000' },
    });

    // 2) fond dégradé + application masque
    const canvas = document.createElement('canvas');
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d')!;

    const grad = ctx.createLinearGradient(0, 0, 0, size);
    grad.addColorStop(0, this.gradientTop);
    grad.addColorStop(1, this.gradientBottom);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, size, size);

    ctx.globalCompositeOperation = 'destination-in';
    ctx.drawImage(mask, 0, 0);
    ctx.globalCompositeOperation = 'source-over';

    // 3) logo optionnel
    if (this.withLogo) {
      try {
        const logo = await this.loadImage('logo.png'); // mettre public/logo.png
        const target = Math.round(size * 0.22);
        const ratio = Math.min(target / logo.width, target / logo.height);
        const lw = Math.round(logo.width * ratio);
        const lh = Math.round(logo.height * ratio);
        const lx = Math.round((size - lw) / 2);
        const ly = Math.round((size - lh) / 2);

        // halo blanc pour contraste
        const pad = Math.round(Math.max(lw, lh) * 0.12);
        const cx = size / 2, cy = size / 2, r = Math.max(lw, lh)/2 + pad;
        ctx.save();
        ctx.globalAlpha = 0.92;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
        ctx.restore();

        ctx.drawImage(logo, lx, ly, lw, lh);
      } catch {
        // pas de logo → ignore
      }
    }

    return canvas;
  }

  /** Aperçu à l’écran (rapide) */
  async generate(): Promise<void> {
    try {
      const canvas = await this.renderCanvas(640);
      this.qrDataUrl = canvas.toDataURL('image/png');
    } catch (err) {
      console.error('Erreur de génération QR:', err);
      this.qrDataUrl = null;
    }
  }

  /** Téléchargement PNG HQ (par défaut 2000px) */
  async downloadPNG(size = 2000): Promise<void> {
    const canvas = await this.renderCanvas(size);
    this.triggerDownload(canvas.toDataURL('image/png'), 'qrcode_artbeaurescence.png');
  }

  /** Téléchargement JPEG HQ (qualité 0.95) */
  async downloadJPEG(size = 2000): Promise<void> {
    const canvas = await this.renderCanvas(size);
    this.triggerDownload(canvas.toDataURL('image/jpeg', 0.95), 'qrcode_artbeaurescence.jpg');
  }

  /** Téléchargement PDF (image centrée sur page A4) */
  async downloadPDF(size = 2000): Promise<void> {
    const canvas = await this.renderCanvas(size);
    const imgData = canvas.toDataURL('image/png');

    // A4 en mm
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();

    // On occupe 160mm de largeur max (marges propres)
    const targetWmm = 160;
    const targetHmm = targetWmm; // carré
    const x = (pageW - targetWmm) / 2;
    const y = (pageH - targetHmm) / 2;

    pdf.addImage(imgData, 'PNG', x, y, targetWmm, targetHmm, undefined, 'FAST');
    pdf.save('qrcode_artbeaurescence.pdf');
  }

  /** Utilitaire de téléchargement */
  private triggerDownload(dataUrl: string, filename: string) {
    const a = document.createElement('a');
    a.href = dataUrl; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
  }
}
