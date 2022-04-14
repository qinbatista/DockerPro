#pip3 install SpeechRecognition pydub

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import shutil
class VoiceManager:
	def __init__(self,path):
		self.__recognizer = sr.Recognizer()
		self.__file_path = path
		self.__file_path_name = self.__file_path[:self.__file_path.rfind("/")]
		self.__file_name = os.path.splitext(self.__file_path)[0][os.path.splitext(self.__file_path)[0].rfind("/")+1:]
		self.__translated_txt = self.__file_path_name+"/"+self.__file_name+".txt"
	def _cover_m4a_to_txt(self):
		wav_file_path = self._cover_m4a_to_mp3(self.__file_path)
		sound = AudioSegment.from_wav(wav_file_path)
		os.remove(wav_file_path)
		chunks = split_on_silence(sound,min_silence_len = 500,silence_thresh = sound.dBFS-14,keep_silence=500,)
		folder_name = "audio-chunks"
		if not os.path.isdir(folder_name):
			os.mkdir(folder_name)
		whole_text = ""
		for i, audio_chunk in enumerate(chunks, start=1):
			chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
			audio_chunk.export(chunk_filename, format="wav")
			with sr.AudioFile(chunk_filename) as source:
				audio_listened = self.__recognizer.record(source)
				try:
					text = self.__recognizer.recognize_google(audio_listened)
				except sr.UnknownValueError as e:
					print("Error:", str(e))
				else:
					text = f"{text.capitalize()}. "
					print(chunk_filename, ":", text)
					whole_text += text
		shutil.rmtree(folder_name)
		print(self.__translated_txt)
		with open(self.__translated_txt, 'w+') as out:
			out.write(whole_text + '\n')
		return whole_text

	def _cover_m4a_to_mp3(self,_path):
		os.system("ffmpeg -i "+_path+"  "+self.__file_path_name+"/"+self.__file_name+".wav")
		print(self.__file_path_name+"/"+self.__file_name+".wav")
		return self.__file_path_name+"/"+self.__file_name+".wav"

if __name__ == '__main__':
	vm = VoiceManager("/root/abc.m4a")
	vm._cover_m4a_to_txt()