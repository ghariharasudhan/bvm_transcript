from fileinput import filename

from youtube_transcript_api import YouTubeTranscriptApi

# yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=33w57iC7f7Y"

# Inauguration | Tattvabodham in Chennai | 18th October	https://www.youtube.com/watch?v=C0Ii9wC0UEY
# Camp Introduction Tattva Bodham & Pooja | Acharya Shri. Rangaji |	https://www.youtube.com/watch?v=8mz8weuf5eg
# thathuva botham in tamil | Class 01 | 2024- 2025 CHE batch	https://www.youtube.com/watch?v=33w57iC7f7Y
# Tatvabodham | Class 02 | Acharya Shri Rangaji	https://www.youtube.com/watch?v=xTBuPYG-Rek
# Tatva Bodham | Class 03 | Acharya Rangaji	https://www.youtube.com/watch?v=t_6u4bS9VBk
# Tatva Bodham | Class 04 | Acharya Ranga ji	https://www.youtube.com/watch?v=Bj2haW0vDdw
# Tatva Bodham | Class 05 | Acharya Ranga ji	https://www.youtube.com/watch?v=HNlOAQ2ynsI
# Tattva Bodham | Class 06 | Acharya Shri Ranga Ji	https://www.youtube.com/watch?v=7iRg6pRS3PU
# Tatvabodham | Class 07 | Acharya Shri . Rangaji	https://www.youtube.com/watch?v=nsSwF80xUmA
# Tattva Bodham | Class 08 | Acharya Shri Ranga ji	https://www.youtube.com/watch?v=qUa_R0ED9tw
# Tattva Bodha | Class 09 | Acharya Shri Ranga ji	https://www.youtube.com/watch?v=gZnSZyMkeV0
# Tattva Bodha | Class 10 | Acharya Sri Ranga ji	https://www.youtube.com/watch?v=MHIvDjV1FiY
# Tattva Bodham | Class-11 | Acharya Ranga ji	https://www.youtube.com/watch?v=0lKnJPN_9aw
# Tattva Bodha |  Class-12 | Acharya Shri Ranga ji	https://www.youtube.com/watch?v=rIxQX38MFoU
# Satsang by Swamini Amma at AVG,  Anaikatti	https://www.youtube.com/watch?v=q1tShZZ1gH0
# Tattva Bodha | Class-13 | Acharya Shri Ranga ji	https://www.youtube.com/watch?v=K9Wq4BgaWUw
# SAMAROP	https://www.youtube.com/watch?v=Sg5T7GzMHPM
# Tattva Bodham | Class 14 after camp |	https://www.youtube.com/watch?v=DmmFoVvGJqo
# Tattva Bodham | Class 15	https://www.youtube.com/watch?v=79AMCb4o23I
# Tattva Bodham | Class 16	https://www.youtube.com/watch?v=HZFd2CzG0ZU
# Tattva Botham | Class 17	https://www.youtube.com/watch?v=GQ3a9otUIIo
# Tattva Bodham | Class 18	https://www.youtube.com/watch?v=d5zB4co3DpM
# Tattva Bodham | Class 19	https://www.youtube.com/watch?v=c5TKl2MqoFo
# Tattvabodham | Class 20	https://www.youtube.com/watch?v=0ooXCjBaqzA
# Tattvabodham | Class 21	https://www.youtube.com/watch?v=oP9yCvtUTlI
# Tattvabodham | Class 22	https://www.youtube.com/watch?v=otxAo4-Jtbo
# Tattvabhodham | Class 23	https://www.youtube.com/watch?v=APfJhzprys0
# Tattvabodham | Class 24	https://www.youtube.com/watch?v=vGiioogf6G8
# Tattvabodham | Class 25	https://www.youtube.com/watch?v=fxqn31e6LGU
# Tattvabodham | Class 26	https://www.youtube.com/watch?v=Zi4HT8WHBQo
# Tattvabodham | Class 27	https://www.youtube.com/watch?v=8C2-MGJNl3Q
# Tattvabhodham | Class 28	https://www.youtube.com/watch?v=QZtSRHW2HDo
# Tattvabodham | Class 29 	https://www.youtube.com/watch?v=9JtSiKIc4LM
# Tattvabodham | Class 30|	https://www.youtube.com/watch?v=cZKx9BKewNs
# Tattvabodham| class 31	https://www.youtube.com/watch?v=NszX7nlhCb4
# Tattvabodham | Class 32 | Summary	https://www.youtube.com/watch?v=X3eZlVikEA4
# iT-X5gymyR4	https://www.youtube.com/watch?v=iT-X5gymyR4

# https://www.youtube.com/live/yqcJPG8x1wo?si=J51cJduZAiNrcOTV
# https://www.youtube.com/live/tujWBB0mRUE?si=8coZvK8Fx3VwcOA-
# https://www.youtube.com/live/RpYlDIGMCoQ?si=_opi4jCtIKjEEcVc
# https://www.youtube.com/live/mdkeujvNUuM?si=6ekzkxseMG2a1x9j
# https://www.youtube.com/live/I2MaLILSKMw?si=eSUygIkuC66TvGDy
# https://www.youtube.com/live/SbGsmi8VjME?si=SMbKz2SuSouG8sDP
# https://www.youtube.com/live/dqX6y3LTOQ8?si=V0_e5QkVTt0Miln7
# https://www.youtube.com/live/rTE3d3mP5MA?si=SlEkZDuzue98Q-Bp
# https://www.youtube.com/live/BHdzavorB1M?si=buJ6ttN_vl35pneh
# https://www.youtube.com/live/xx3Ev13TMVk?si=v1udtorknTzHWbxe
# https://www.youtube.com/live/R6z54zgmCx0?si=jMqIwtIYulQBNxHc


video_id = "R6z54zgmCx0"  # Replace with the actual video ID    

ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id, languages=['ta'])

text = "\n".join(snippet.text for snippet in transcript)


print(text[:100]) 
filename="./Taittriya/Tait-CLASS-11"

# with open("transcript-K00-2.txt", "w", encoding="utf-8") as f:
with open(filename + ".txt", "w", encoding="utf-8") as f:
    f.write(text)

# with open(filename + "_cleaned .txt", "w", encoding="utf-8") as f:
#     f.write("")

# with open(filename + "_summary .txt", "w", encoding="utf-8") as f:
#     f.write("")

print(filename + ".txt file created successfully.")