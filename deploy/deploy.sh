python cli_main.py douyin ycp login

noglob yt-dlp -a ~/work/temp/video/urls.txt \
   -o ~/work/temp/video/tiktok/$(date +%Y-%m-%d)/%(uploader)s-%(id)s.%(ext)s
   
./deploy/upload_today_videos.sh