import uuid
from pathlib import Path
from google.cloud import texttospeech
import oss2
from wordentity import Sentence,VocabularyExtend
from oss2.headers import OSS_OBJECT_TAGGING

class UtteranceController:
    def __init__(self):
        self.dest_directory = Path('/root/baidupan_selenium/uterance/')
        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient()
        self.auth = oss2.Auth('LTAI4FcjbgijZZqQbrug1xPZ', 'Yu82TyUl9zOBpgmrFlQVSOjG8l9h4t')
        self.endpoint = 'oss-cn-shanghai.aliyuncs.com'
        # 设置连接超时时间为30秒。
        self.bucket = oss2.Bucket(self.auth, self.endpoint, 'voice-cbtai-com', connect_timeout=30)
        self.do_init()

    def do_init(self):
        pass

    # 把特定文本文件转换为对应的声音文件
    def text_to_speech(self):
        index = 0
        for sentence in Sentence.select():
            outname = self.get_speech(sentence.sent_content)
            sentence.sent_voic_id = outname
            sentence.save()
            index +=1

    # 把特定单词转换为对应的声音文件
    def word_to_speech(self):
        index = 0
        for vocabusExtend in VocabularyExtend.select():
            forms = vocabusExtend.forms.split(',')
            outnames = []
            # 所有的单词变体
            for word in forms:
                outname = self.get_speech(word)
                outnames.append(outname)
                print('.', end='')
            speakuuids = ','.join(outnames)
            vocabusExtend.speakvoiceids = speakuuids
            vocabusExtend.save()
            index +=1
            print(str(index))

    def get_speech(self,inputText):
        # Set the text input to be synthesized
        synthesis_input = texttospeech.types.SynthesisInput(text=inputText)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

        # Select the type of audio file you want returned
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(synthesis_input, voice, audio_config)
        # http header中设置标签信息。
        headers = dict()
        headers["Content-Type"] = "audio/mp3"
        outname = str(uuid.uuid1())
        self.bucket.put_object(outname +'.mp3',response.audio_content)
        return outname
