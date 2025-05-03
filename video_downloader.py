import os
import sys
import re
from pytube import YouTube  # Geriye dönük uyumluluk için tutuyoruz
import yt_dlp
import instaloader

def create_download_dir():
    """İndirilen videolar için klasör oluşturur."""
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indirilen_videolar")
    os.makedirs(download_dir, exist_ok=True)
    return download_dir

def download_youtube_video(url, download_path):
    """YouTube videolarını indirir. yt-dlp kütüphanesi kullanılarak güncellenmiştir."""
    try:
        print(f"YouTube videosu indiriliyor: {url}")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,  # Sadece video, oynatma listesi değil
            'quiet': False,  # İlerleme göstergesi görünür
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Video başarıyla indirildi: {info.get('title', 'Bilinmeyen video')}")
            print(f"Video dosya yolu: {os.path.join(download_path, info.get('title', 'video') + '.' + info.get('ext', 'mp4'))}")
        return True
    except Exception as e:
        print(f"YouTube videosu indirilirken bir hata oluştu: {str(e)}")
        print("Alternatif indirme yöntemi deneniyor...")
        
        try:
            # İlk metot başarısız olursa, farklı format seçenekleri deneyelim
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"Video başarıyla indirildi: {info.get('title', 'Bilinmeyen video')}")
            return True
        except Exception as e2:
            print(f"Alternatif indirme yöntemi de başarısız oldu: {str(e2)}")
            return False

def download_twitter_video(url, download_path):
    """Twitter videolarını indirir."""
    try:
        print(f"Twitter videosu indiriliyor: {url}")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Video başarıyla indirildi: {info.get('title', 'Bilinmeyen video')}")
        return True
    except Exception as e:
        print(f"Twitter videosu indirilirken bir hata oluştu: {str(e)}")
        return False

def download_instagram_video(url, download_path):
    """Instagram videolarını indirir."""
    try:
        print(f"Instagram videosu indiriliyor: {url}")
        
        # Instagram URL'inden post ID'yi ayıklayalım
        match = re.search(r'instagram.com/(?:p|reel)/([^/?]+)', url)
        
        if not match:
            print("Geçerli bir Instagram video URL'si değil.")
            return False
        
        shortcode = match.group(1)
        
        # Instaloader'ı yapılandıralım
        L = instaloader.Instaloader(
            dirname_pattern=download_path,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Post'u indirelim
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=shortcode)
        print(f"Instagram videosu başarıyla indirildi.")
        return True
    except Exception as e:
        print(f"Instagram videosu indirilirken bir hata oluştu: {str(e)}")
        return False

def detect_platform(url):
    """URL'ye bakarak hangi platformdan video indirileceğini belirler."""
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "instagram.com" in url:
        return "instagram"
    else:
        return None

def main():
    # İndirme klasörünü oluştur
    download_path = create_download_dir()
    print(f"Videolar şu klasöre indirilecek: {download_path}")
    
    while True:
        print("\n=== Video İndirme Uygulaması ===")
        print("Çıkmak için 'q' yazın")
        
        url = input("\nLütfen video URL'sini girin: ").strip()
        
        if url.lower() == 'q':
            print("Program sonlandırılıyor...")
            break
        
        platform = detect_platform(url)
        
        if platform == "youtube":
            download_youtube_video(url, download_path)
        elif platform == "twitter":
            download_twitter_video(url, download_path)
        elif platform == "instagram":
            download_instagram_video(url, download_path)
        else:
            print("Desteklenmeyen platform veya geçersiz URL. Sadece YouTube, Twitter ve Instagram desteklenmektedir.")

if __name__ == "__main__":
    main()