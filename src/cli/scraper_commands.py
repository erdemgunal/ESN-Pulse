"""
ESN PULSE Scraper Commands

Bu modül, scraper komutlarını içerir.
"""

import asyncio
import logging
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.database.connection import get_db_connection
from src.scrapers.accounts_scraper import AccountsScraper
from src.scrapers.activities_statistics_scraper import ActivitiesAndStatisticsScraper

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="ESN PULSE Scraper Komutları")

@app.command()
def accounts():
    """accounts.esn.org'dan ülke ve şube verilerini çeker."""
    try:
        console.print("🔄 AccountsScraper başlatılıyor...")
        asyncio.run(_run_accounts_scraper())
        console.print("✅ AccountsScraper başarıyla tamamlandı")
    except Exception as e:
        console.print(f"❌ AccountsScraper hatası: {str(e)}", style="red")
        raise typer.Exit(1)

@app.command()
def activities(section: Optional[str] = typer.Option(
    None,
    "--section",
    "-s",
    help="Belirli bir şube için scraping yapmak için şube slug'ı (örn. esn-yildiz)"
)):
    """activities.esn.org'dan etkinlik ve istatistik verilerini çeker."""
    try:
        console.print("🔄 ActivitiesAndStatisticsScraper başlatılıyor...")
        asyncio.run(_run_activities_scraper(section))
        console.print("✅ ActivitiesAndStatisticsScraper başarıyla tamamlandı")
    except Exception as e:
        console.print(f"❌ ActivitiesAndStatisticsScraper hatası: {str(e)}", style="red")
        raise typer.Exit(1)

@app.command()
def all():
    """Tüm scraper'ları çalıştırır."""
    try:
        # Önce AccountsScraper çalıştırılır
        console.print("🔄 AccountsScraper başlatılıyor...")
        asyncio.run(_run_accounts_scraper())
        console.print("✅ AccountsScraper başarıyla tamamlandı")
        
        # Sonra ActivitiesAndStatisticsScraper çalıştırılır
        console.print("🔄 ActivitiesAndStatisticsScraper başlatılıyor...")
        asyncio.run(_run_activities_scraper())
        console.print("✅ ActivitiesAndStatisticsScraper başarıyla tamamlandı")
    except Exception as e:
        console.print(f"❌ Scraper'lar çalışırken hata: {str(e)}", style="red")
        raise typer.Exit(1)

async def _run_accounts_scraper():
    """AccountsScraper'ı çalıştırır."""
    async with get_db_connection() as conn:
        scraper = AccountsScraper(conn)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Ülke ve şube verileri çekiliyor...", total=None)
            await scraper.run()

async def _run_activities_scraper(section_slug: Optional[str] = None):
    """ActivitiesAndStatisticsScraper'ı çalıştırır."""
    async with get_db_connection() as conn:
        scraper = ActivitiesAndStatisticsScraper(conn)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            if section_slug:
                progress.add_task(
                    f"{section_slug} şubesi için etkinlik ve istatistik verileri çekiliyor...",
                    total=None
                )
                await scraper.run_for_section(section_slug)
            else:
                progress.add_task(
                    "Tüm şubeler için etkinlik ve istatistik verileri çekiliyor...",
                    total=None
                )
                await scraper.run() 