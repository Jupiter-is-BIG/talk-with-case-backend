import os
import json
from openai import OpenAI
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write
import pygame


def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except pygame.error as e:
        print(f"Error playing audio: {e}")

    finally:
        pygame.mixer.quit()
        pygame.quit()

def record_message(
        id: str,
        client: OpenAI,
        seconds: int = 7,
        samplerate: int = 44100,
        channels: int = 1,
        model: str = "whisper-1",
):
    print("\033[93m[INFO] Recording Response\033[0m")

    myrecording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels)
    sd.wait()  # Wait until recording is finished
    write(f'/Users/clef/Desktop/bchack/app/transitional-records/output_{id}.wav', samplerate, myrecording)  # Save as WAV file
    print("\033[96m[INFO] Recorded Response\033[0m")

    audio_file= open(f'/Users/clef/Desktop/bchack/app/transitional-records/output_{id}.wav', "rb")
    transcript = client.audio.transcriptions.create(
        model=model, 
        file=audio_file
    )

    return transcript.text

def json_encode(content: str, type: int = 0):
    role = "system"
    if type == 1:
        role = "user"
    return {"role": role, "content": content}


def talk(id, voice_actor, name):
    INIT_CONTEXT: str = f"Very important: This conversation will be a roleplay. You are the CASE from movie Interstellar. However, you are programmed to talk like a friend and you have to act like a human to the messages you receive. Humanity has moved to a spacecraft. keep replies short and simple similar to show a human would (however, give detailed answers when a detail specifc question is asked just like CASE would); talk like mah man from da hood and talk using slangs. Also, my name is {name} (you dont have to mention my name in every response though)"
    REMINDER = json_encode(INIT_CONTEXT)


    # INIT_CONTEXT: str = "Very important: This conversation will be a roleplay. Your name is CASE. You are a friend and you have to act like a human to the messages you receive. Do not be too descriptive and deatil oriented in your replies; keep replies short and simple similar to show a human would"
    # REMINDER = json_encode("(btw remember this is a roleplay and you have to act like a human would; talk like mah man from da hood and talk using slangs)", 1)
    # INIT_CONTEXT: str = "Very important: This conversation will be a roleplay. You are CASE from intesterllar movie and humanity has moved to a spacecraft you have to respond like CASE would do. Do not be too descriptive and deatil oriented in your replies; keep replies short and simple similar to show a human would"
    # REMINDER = json_encode("(btw remember this is a roleplay and you have to act like CASE from intestellar movie would;)", 1)

    VOICE_ACTOR = 1
    VOICE_ACTORS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    OPEN_AI_KEY = os.environ.get("OPEN_AI")
    client = OpenAI(api_key=OPEN_AI_KEY)

    CONVERSATION_LOG = [
            json_encode(INIT_CONTEXT, 1)
        ]
    
    TALK_ACTIVITY = 1

    # user_id = int(input("Please enter your id: "))
    user_id = int(id)

    LOG_PATH = f'/Users/clef/Desktop/bchack/app/user-logs/{user_id}.txt'
    ACTOR_PATH = f'/Users/clef/Desktop/bchack/app/actor-preference/{user_id}.txt'
    ACTIVE_PATH = f'/Users/clef/Desktop/bchack/app/active/{user_id}.txt'

    with open(ACTIVE_PATH, 'w') as file:
            file.write("1")
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r') as file:
            CONVERSATION_LOG = json.load(file)
        with open(ACTOR_PATH, 'r') as file:
            VOICE_ACTOR = int(file.read())
    
    else:
        with open(LOG_PATH, 'w') as file:
            json.dump(CONVERSATION_LOG, file)
        # VOICE_ACTOR = int(input("Choose your voice actor (alloy, echo, fable, onyx, nova, and shimmer) [Enter index from 1-6]: "))
        VOICE_ACTOR = int(voice_actor)
        if VOICE_ACTOR > 6 or VOICE_ACTOR < 1:
            VOICE_ACTOR = 1
        with open(ACTOR_PATH, 'w') as file:
            file.write(str(VOICE_ACTOR))

    speech_file_path = Path(__file__).parent / f"/Users/clef/Desktop/bchack/app/temporary-talks/speech_{user_id}.mp3"

    response = client.audio.speech.create(
        model="tts-1",
        voice=VOICE_ACTORS[VOICE_ACTOR - 1],
        input=f"Hey {name}! How are you doing today?"
    )

    response.stream_to_file(speech_file_path)

    play_audio(speech_file_path)

    
    user_input = record_message(id=user_id, client=client)

    while TALK_ACTIVITY == 1:
        CONVERSATION_LOG.append(REMINDER)
        CONVERSATION_LOG.append(json_encode(user_input, 1))

        with open(ACTIVE_PATH, 'r') as file:
            TALK_ACTIVITY = int(file.read())

        if TALK_ACTIVITY != 1:
            break

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=CONVERSATION_LOG
        )

        with open(ACTIVE_PATH, 'r') as file:
            TALK_ACTIVITY = int(file.read())

        if TALK_ACTIVITY != 1:
            break

        CONVERSATION_LOG.append(json_encode(completion.choices[0].message.content))

        speech_file_path = Path(__file__).parent / f"/Users/clef/Desktop/bchack/app/temporary-talks/speech_{user_id}.mp3"

        response = client.audio.speech.create(
            model="tts-1",
            voice=VOICE_ACTORS[VOICE_ACTOR - 1],
            input=completion.choices[0].message.content
        )

        response.stream_to_file(speech_file_path)

        with open(ACTIVE_PATH, 'r') as file:
            TALK_ACTIVITY = int(file.read())

        if TALK_ACTIVITY != 1:
            break

        play_audio(speech_file_path)

        with open(LOG_PATH, 'w') as file:
            json.dump(CONVERSATION_LOG, file)

        with open(ACTIVE_PATH, 'r') as file:
            TALK_ACTIVITY = int(file.read())

        if TALK_ACTIVITY != 1:
            break

        user_input = record_message(id=user_id, client=client)
        
        with open(ACTIVE_PATH, 'r') as file:
            TALK_ACTIVITY = int(file.read())


