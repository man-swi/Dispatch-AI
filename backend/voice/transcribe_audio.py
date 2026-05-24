import whisper

model = whisper.load_model("base")

result = model.transcribe("driver_response.mp3")

print(result["text"])