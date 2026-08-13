// ============================================================================
// Café Cenit — Currency Switcher
// Convierte precios USD → VES usando tasa BCV en vivo
// Con fallback elegante si la API falla
// ============================================================================

interface SiteConfig {
  currency: {
    primary: string;
    secondary: string;
    bcv_api_url: string;
    bcv_api_fallback: string;
    fallback_rate_ves_per_usd: number;
  };
}

interface BCVResponse {
  fuente: string;
  nombre: string;
  compra: number;
  venta: number;
  promedio: number;
  fechaActualizacion: string;
}

interface ExchangeRateResponse {
  rates: {
    VES: number;
  };
  time_last_updated: number;
}

class CurrencySwitcher {
  private site: SiteConfig;
  private currentCurrency: 'USD' | 'VES' = 'USD';
  private rate: number | null = null;
  private rateUpdatedAt: string | null = null;
  private isLoading = false;

  constructor(site: SiteConfig) {
    this.site = site;
  }

  async init(): Promise<void> {
    this.bindUI();
    await this.loadRate();
    this.applyPrices();
    this.updateRateBadge();
  }

  private async loadRate(): Promise<void> {
    this.isLoading = true;
    this.updateRateBadge();

    try {
      const res = await fetch(this.site.currency.bcv_api_url, {
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error('BCV primary failed');
      const data: BCVResponse = await res.json();
      this.rate = data.promedio;
      this.rateUpdatedAt = data.fechaActualizacion;
    } catch {
      try {
        const res = await fetch(this.site.currency.bcv_api_fallback, {
          signal: AbortSignal.timeout(5000),
        });
        if (!res.ok) throw new Error('Fallback failed');
        const data: ExchangeRateResponse = await res.json();
        this.rate = data.rates.VES;
        this.rateUpdatedAt = new Date(data.time_last_updated * 1000).toISOString();
      } catch {
        this.rate = this.site.currency.fallback_rate_ves_per_usd;
        this.rateUpdatedAt = null;
      }
    } finally {
      this.isLoading = false;
      this.updateRateBadge();
    }
  }

  private applyPrices(): void {
    const elements = document.querySelectorAll<HTMLElement>('[data-price-usd]');
    elements.forEach((el) => {
      const usd = parseFloat(el.dataset.priceUsd || '0');
      if (Number.isNaN(usd)) return;
      if (this.currentCurrency === 'USD') {
        el.textContent = this.formatUSD(usd);
      } else if (this.rate !== null) {
        el.textContent = this.formatVES(usd * this.rate);
      } else {
        el.textContent = 'No disponible';
      }
    });
  }

  private formatUSD(value: number): string {
    return `$${value.toFixed(value % 1 === 0 ? 0 : 2)} USD`;
  }

  private formatVES(value: number): string {
    return `Bs. ${Math.round(value).toLocaleString('es-VE')}`;
  }

  private bindUI(): void {
    const switchers = document.querySelectorAll<HTMLButtonElement>('[data-currency-switch]');
    switchers.forEach((btn) => {
      btn.addEventListener('click', () => {
        const next = btn.dataset.currencySwitch as 'USD' | 'VES';
        if (next && next !== this.currentCurrency) {
          this.currentCurrency = next;
          this.applyPrices();
          this.updateSwitcherUI();
        }
      });
    });
  }

  private updateSwitcherUI(): void {
    document.querySelectorAll<HTMLButtonElement>('[data-currency-switch]').forEach((btn) => {
      const isActive = btn.dataset.currencySwitch === this.currentCurrency;
      btn.setAttribute('aria-pressed', String(isActive));
      btn.classList.toggle('is-active', isActive);
    });
  }

  private updateRateBadge(): void {
    const badge = document.querySelector<HTMLElement>('[data-rate-badge]');
    if (!badge) return;

    if (this.isLoading) {
      badge.textContent = 'Cargando tasa BCV…';
      badge.classList.remove('is-error');
      return;
    }

    if (this.rate === null) {
      badge.textContent = 'Tasa no disponible';
      badge.classList.add('is-error');
      return;
    }

    if (this.rateUpdatedAt) {
      const d = new Date(this.rateUpdatedAt);
      const formatted = d.toLocaleDateString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric' });
      badge.textContent = `1 USD = Bs. ${this.rate.toFixed(2)} · BCV ${formatted}`;
      badge.classList.remove('is-error');
    } else {
      badge.textContent = `1 USD = Bs. ${this.rate.toFixed(2)} · Tasa referencial`;
      badge.classList.add('is-error');
    }
  }
}

declare global {
  interface Window {
    __CURRENCY_SWITCHER__?: CurrencySwitcher;
    __SITE_CONFIG__?: SiteConfig;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const site = window.__SITE_CONFIG__;
  if (!site) return;
  const switcher = new CurrencySwitcher(site);
  window.__CURRENCY_SWITCHER__ = switcher;
  switcher.init();
});

export {};
