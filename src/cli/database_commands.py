"""
ESN PULSE Database Commands

Bu modül, veritabanı yönetimi komutlarını içerir.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.database.connection import get_db_connection

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="ESN PULSE Veritabanı Komutları")

@app.command()
def backup():
    """Veritabanının yedeğini alır."""
    try:
        # Yedekleme dizinini oluştur
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Yedek dosya adını oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"esn_pulse_{timestamp}.sql"
        
        # pg_dump komutunu oluştur
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-p", "5433",
            "-U", "postgres",
            "-d", "esn_pulse",
            "-F", "p",  # plain text format
            "-f", str(backup_file)
        ]
        
        # Yedekleme işlemini başlat
        console.print("🔄 Veritabanı yedekleniyor...")
        env = os.environ.copy()
        env["PGPASSWORD"] = "password"
        subprocess.run(cmd, env=env, check=True)
        
        console.print(f"✅ Yedekleme başarıyla tamamlandı: {backup_file}")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Yedekleme hatası: {str(e)}", style="red")
        raise typer.Exit(1)

@app.command()
def restore(
    backup_file: str = typer.Argument(
        ...,
        help="Geri yüklenecek yedek dosyasının yolu"
    )
):
    """Veritabanını yedekten geri yükler."""
    try:
        # Yedek dosyasının varlığını kontrol et
        backup_path = Path(backup_file)
        if not backup_path.exists():
            console.print(f"❌ Yedek dosyası bulunamadı: {backup_file}", style="red")
            raise typer.Exit(1)
        
        # psql komutunu oluştur
        cmd = [
            "psql",
            "-h", "localhost",
            "-p", "5433",
            "-U", "postgres",
            "-d", "esn_pulse",
            "-f", str(backup_path)
        ]
        
        # Geri yükleme işlemini başlat
        console.print("🔄 Veritabanı geri yükleniyor...")
        env = os.environ.copy()
        env["PGPASSWORD"] = "password"
        subprocess.run(cmd, env=env, check=True)
        
        console.print("✅ Geri yükleme başarıyla tamamlandı")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Geri yükleme hatası: {str(e)}", style="red")
        raise typer.Exit(1)

@app.command()
def cleanup():
    """Eski yedekleri ve geçersiz kayıtları temizler."""
    try:
        console.print("🔄 Temizleme işlemi başlatılıyor...")
        asyncio.run(_run_cleanup())
        console.print("✅ Temizleme işlemi başarıyla tamamlandı")
    except Exception as e:
        console.print(f"❌ Temizleme hatası: {str(e)}", style="red")
        raise typer.Exit(1)

async def _run_cleanup():
    """Temizleme işlemini gerçekleştirir."""
    async with get_db_connection() as conn:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Geçersiz kayıtlar temizleniyor...", total=None)
            
            # Geçersiz etkinlikleri temizle
            await conn.execute("""
                DELETE FROM activities
                WHERE is_valid = FALSE
                AND updated_at < NOW() - INTERVAL '30 days'
            """)
            
            # Eski hata kayıtlarını temizle
            await conn.execute("""
                DELETE FROM validation_errors
                WHERE created_at < NOW() - INTERVAL '30 days'
            """)
            await conn.execute("""
                DELETE FROM failed_scrapes
                WHERE last_attempt < NOW() - INTERVAL '30 days'
            """)
            
            # Eski scraper durumlarını temizle
            await conn.execute("""
                DELETE FROM scraper_status
                WHERE completed_at < NOW() - INTERVAL '30 days'
            """)
            
            progress.update(task, completed=True) 