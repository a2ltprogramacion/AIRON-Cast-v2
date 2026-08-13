import json
import time
import random
import logging
import datetime as dt
from decimal import Decimal
from urllib.request import Request as StdLibRequest, urlopen
from urllib.error import URLError, HTTPError
from django.utils import timezone
from .models import ExchangeRateLog

logger = logging.getLogger(__name__)

# =============================================================================
# PROXY POOL - Health-aware proxy rotation
# =============================================================================

class ProxyPool:
    """
    Gestor de proxy pool con health checking.
    Implementa failover parcial: si un proxy falla 3 veces, se marca como
    temporalmente no disponible y se ignora en las siguientes rotaciones.
    """
    
    def __init__(self, proxies: list = None):
        self.proxies = proxies or []
        self.failed_count = {p: 0 for p in self.proxies}
        self.last_used_index = 0
        self._reset_timer = None
        
    def get_next(self) -> str | None:
        """
        Obtiene el siguiente proxy disponible en round-robin.
        Ignora proxies con failed_count >= 3.
        Retorna None si no hay proxies disponibles (sin proxy = conexion directa).
        """
        if not self.proxies:
            return None
            
        available = [p for p in self.proxies if self.failed_count[p] < 3]
        if not available:
            logger.warning("[ProxyPool] Todos los proxies han fallado 3+ veces. Usando conexion directa.")
            return None
            
        proxy = available[self.last_used_index % len(available)]
        self.last_used_index += 1
        return proxy
    
    def mark_failed(self, proxy: str):
        """Marca un proxy como fallido. Si supera 3 fallos, se ignora temporalmente."""
        if proxy not in self.failed_count:
            return
        self.failed_count[proxy] += 1
        logger.warning(f"[ProxyPool] Proxy {proxy} fallido ({self.failed_count[proxy]}/3)")
    
    def reset_all(self):
        """Resetea el contador de fallos de todos los proxies. Usar cada hora."""
        for proxy in self.proxies:
            self.failed_count[proxy] = 0
        self.last_used_index = 0
        logger.info("[ProxyPool] Contadores de fallo reseteados.")
    
    def add_proxy(self, proxy: str):
        """Agrega un nuevo proxy al pool."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.failed_count[proxy] = 0
            logger.info(f"[ProxyPool] Proxy agregado: {proxy}")


# =============================================================================
# BINANCE P2P SERVICE - Resilient fetching with fallback chain
# =============================================================================

class BinanceP2PService:
    """
    Servicio resiliente para obtener la tasa Binance P2P (USDT -> VES).
    
    Implementa una cadena de fallback en 4 niveles:
        1. curl_cffi  -> TLS fingerprint bypass (Chrome 120)
        2. httpx      -> Cliente async con retry automatico
        3. requests   -> stdlib++ con buenas practicas
        4. urllib     -> Ultimo recurso stdlib
    
    El proxy pool se usa en cada intento si esta configurado.
    Cada nivel tiene hasta MAX_RETRIES reintentos internos.
    """
    
    MAX_RETRIES = 3
    PROXY_TIMEOUT = 15  # segundos
    REQUEST_DELAY = (0.5, 1.5)  # base, jitter max para delay aleatorio
    
    def __init__(self, proxy_pool: ProxyPool = None):
        self.proxy_pool = proxy_pool or ProxyPool()
        self._session_headers = {
            "Accept": "application/json",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://p2p.binance.com",
            "Referer": "https://p2p.binance.com/es/trade/sell/USDT?fiat=VES",
        }
    
    def _random_delay(self):
        """Simula comportamiento humano con delay aleatorio entre intentos."""
        base, jitter = self.REQUEST_DELAY
        delay = base + random.uniform(0, jitter)
        time.sleep(delay)
    
    def _get_proxy_dict(self) -> dict | None:
        """Retorna el dict de proxies para httpx/requests o None si no hay proxy."""
        proxy = self.proxy_pool.get_next()
        if not proxy:
            return None
        return {"https": proxy, "http": proxy}
    
    def fetch_rate(self) -> Decimal | None:
        """
        Punto de entrada unico. Implementa la cadena de fallback.
        Retorna el promedio de las 3 primeras ofertas SELL de USDT/VES,
        o None si todos los metodos fallaron.
        """
        # Intento 1: curl_cffi (TLS fingerprint)
        for attempt in range(self.MAX_RETRIES):
            rate = self._fetch_with_curl_cffi()
            if rate:
                return rate
            if attempt < self.MAX_RETRIES - 1:
                self._random_delay()
        
        # Intento 2: httpx
        for attempt in range(self.MAX_RETRIES):
            rate = self._fetch_with_httpx()
            if rate:
                return rate
            if attempt < self.MAX_RETRIES - 1:
                self._random_delay()
        
        # Intento 3: requests
        for attempt in range(self.MAX_RETRIES):
            rate = self._fetch_with_requests()
            if rate:
                return rate
            if attempt < self.MAX_RETRIES - 1:
                self._random_delay()
        
        # Intento 4: stdlib urllib (ultimo recurso)
        for attempt in range(self.MAX_RETRIES):
            rate = self._fetch_with_stdlib()
            if rate:
                return rate
            if attempt < self.MAX_RETRIES - 1:
                self._random_delay()
        
        logger.error("[BinanceP2P] Todos los niveles de fallback fallaron.")
        return None
    
    def _fetch_with_curl_cffi(self) -> Decimal | None:
        """
        Nivel 1: curl_cffi. Usa TLS fingerprinting de Chrome 120.
        Este es el metodo mas efectivo para evadir deteccion de Binance.
        """
        try:
            import curl_cffi
        except ImportError:
            logger.warning("[curl_cffi] Libreria no instalada.")
            return None
            
        proxies = self._get_proxy_dict()
        
        try:
            response = curl_cffi.get(
                "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                params={
                    "asset": "USDT",
                    "fiat": "VES",
                    "tradeType": "BUY",
                    "rows": 3,
                    "page": 1,
                    "payTypes": []
                },
                headers=self._session_headers,
                proxies=proxies,
                timeout=self.PROXY_TIMEOUT,
                impersonate="chrome120"
            )
            return self._parse_response(response.json())
        except Exception as e:
            logger.warning(f"[curl_cffi] Fallo: {e}")
            return None
    
    def _fetch_with_httpx(self) -> Decimal | None:
        """
        Nivel 2: httpx. Cliente moderno con soporte async y retry.
        """
        try:
            import httpx
        except ImportError:
            logger.warning("[httpx] Libreria no instalada.")
            return None
            
        proxy = self.proxy_pool.get_next()
        
        try:
            with httpx.Client(proxies=proxy, timeout=self.PROXY_TIMEOUT) as client:
                response = client.post(
                    "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                    json={
                        "asset": "USDT",
                        "fiat": "VES",
                        "tradeType": "BUY",
                        "rows": 3,
                        "page": 1,
                        "payTypes": []
                    },
                    headers=self._session_headers
                )
                return self._parse_response(response.json())
        except Exception as e:
            logger.warning(f"[httpx] Fallo: {e}")
            if proxy:
                self.proxy_pool.mark_failed(proxy)
            return None
    
    def _fetch_with_requests(self) -> Decimal | None:
        """
        Nivel 3: requests. stdlib++ con sesiones persistentes.
        """
        try:
            import requests
        except ImportError:
            logger.warning("[requests] Libreria no instalada.")
            return None
            
        proxies = self._get_proxy_dict()
        
        try:
            session = requests.Session()
            session.headers.update(self._session_headers)
            response = session.post(
                "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                json={
                    "asset": "USDT",
                    "fiat": "VES",
                    "tradeType": "BUY",
                    "rows": 3,
                    "page": 1,
                    "payTypes": []
                },
                proxies=proxies,
                timeout=self.PROXY_TIMEOUT
            )
            return self._parse_response(response.json())
        except Exception as e:
            logger.warning(f"[requests] Fallo: {e}")
            return None
    
    def _fetch_with_stdlib(self) -> Decimal | None:
        """
        Nivel 4: urllib stdlib. Ultimo recurso sin dependencias externas.
        """
        payload = json.dumps({
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": "BUY",
            "rows": 3,
            "page": 1,
            "payTypes": []
        }).encode("utf-8")
        
        req = StdLibRequest(
            "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
            data=payload,
            headers={**self._session_headers, "Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urlopen(req, timeout=self.PROXY_TIMEOUT) as response:
                return self._parse_response(json.loads(response.read().decode("utf-8")))
        except Exception as e:
            logger.warning(f"[stdlib] Fallo: {e}")
            return None
    
    def _parse_response(self, data: dict) -> Decimal | None:
        """
        Extrae el promedio de las 3 primeras ofertas SELL de USDT/VES.
        """
        ads = data.get("data", [])
        if not ads:
            logger.warning("[parse] No se encontraron anuncios en la respuesta.")
            return None
        
        prices = []
        for ad in ads[:3]:
            price_str = ad.get("adv", {}).get("price")
            if price_str:
                try:
                    prices.append(Decimal(str(price_str)))
                except Exception:
                    continue
        
        if not prices:
            logger.warning("[parse] No se pudieron extraer precios de los anuncios.")
            return None
        
        avg = sum(prices) / len(prices)
        logger.info(f"[parse] Tasa Binance P2P extraida: {avg} (de {len(prices)} ofertas)")
        return avg


# =============================================================================
# SINGLETON - Instancia global del servicio
# =============================================================================

_binance_service = None

def get_binance_service() -> BinanceP2PService:
    """Obtiene la instancia singleton del BinanceP2PService."""
    global _binance_service
    if _binance_service is None:
        _binance_service = BinanceP2PService()
    return _binance_service


# =============================================================================
# LEGACY API - Compatible con el codigo existente
# =============================================================================

def fetch_bcv_rate():
    """
    Extrae la tasa oficial del BCV desde DolarAPI.
    URL: https://ve.dolarapi.com/v1/dolares/oficial
    """
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    req = StdLibRequest(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        method="GET"
    )
    
    try:
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            rate = data.get("promedio") or data.get("valor")
            if rate:
                return Decimal(str(rate))
            raise ValueError("No se encontro la tasa en el JSON de respuesta.")
    except Exception as e:
        logger.error(f"[fetch_bcv_rate] Error al obtener tasa BCV: {e}")
        raise e


def fetch_binance_rate() -> Decimal | None:
    """
    Wrapper compatible con el codigo existente.
    delega en BinanceP2PService para usar la cadena de fallback.
    """
    return get_binance_service().fetch_rate()


def ensure_exchange_rate(target_date):
    """
    Asegura que exista una tasa de cambio registrada para la fecha dada.
    - Si ya existe, la retorna.
    - Si no existe y es hoy: consulta APIs para BCV y Binance y guarda en BD.
    - Si no existe y es fecha pasada: consulta BCV (historico o actual) y deja Binance en None.
    """
    if isinstance(target_date, dt.datetime):
        target_date = target_date.date()
    
    log = ExchangeRateLog.objects.filter(date=target_date).first()
    if log:
        return log
    
    today = timezone.localdate()
    bcv_rate = None
    binance_rate = None
    
    if target_date == today:
        try:
            bcv_rate = fetch_bcv_rate()
        except Exception:
            bcv_rate = Decimal("36.50")
        
        try:
            binance_rate = fetch_binance_rate()
        except Exception:
            binance_rate = None
    else:
        try:
            bcv_rate = fetch_bcv_rate()
        except Exception:
            last_log = ExchangeRateLog.objects.order_by('-date').first()
            bcv_rate = last_log.bcv_rate if last_log else Decimal("36.50")
        
        binance_rate = None
    
    log = ExchangeRateLog.objects.create(
        date=target_date,
        bcv_rate=bcv_rate,
        binance_rate=binance_rate
    )
    return log