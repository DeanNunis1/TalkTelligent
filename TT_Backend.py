import pyaudio
import asyncio
import websockets
import json
import openai
import re

class Answers:
    def __init__(self):
        openai.api_key = ""
        self.DEEPGRAM_API_KEY = ""
        self.sound = True
        self.audio = pyaudio.PyAudio()
        self.audio_queue = asyncio.Queue()
        self.device = self.audio.get_default_output_device_info()
        self.RATE = int(self.device['defaultSampleRate'])
        self.INDEX = self.search_audio_device()
        self.question_queue = asyncio.Queue()  # create a queue for questions

    def search_audio_device(self):
        # Search for Stereo Mix audio index
        device_name = re.compile(".*Stereo Mix.*", re.IGNORECASE)
        # Loops through audio devices
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if device_name.match(info["name"]):
                return info["index"]
        print(f"Could not find audio device with name matching '{device_name.pattern}'")
        return None

    async def audio_source(self):
        def callback(input_data, frame_count, time_info, status_flags):
            self.audio_queue.put_nowait(input_data)
            return (input_data, pyaudio.paContinue)

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=self.RATE,
            input=True,
            input_device_index=self.INDEX,
            frames_per_buffer=1024,
            stream_callback=callback
        )
        stream.start_stream()
        while stream.is_active():
            await asyncio.sleep(2.1)

        stream.stop_stream()
        stream.close()

    async def process(self):
        async with websockets.connect(
                'wss://api.deepgram.com/v1/listen?model=nova&punctuate=true&endpointing=true&encoding=linear16&sample_rate=' +
                str(self.RATE) + '&channels=2',
                extra_headers={'Authorization': 'token ' + self.DEEPGRAM_API_KEY}) as ws:
            async def sender(ws):  # sends audio to websocket
                try:
                    while True:
                        data = await self.audio_queue.get()
                        await ws.send(data)
                except Exception as e:
                    print('Error while sending: ', str(e))  # remove unary + before str(e)
                raise

            async def receiver(ws):
                async for msg in ws:
                    msg = json.loads(msg)
                    transcript = msg['channel']['alternatives'][0]['transcript']
                    for line in transcript.splitlines():
                        if self.has_question_word(line):
                            await self.question_queue.put(line)  # enqueue question and continue
            
            
            sender_task = asyncio.create_task(sender(ws))
            receiver_task = asyncio.create_task(receiver(ws))

            await asyncio.gather(sender_task, receiver_task)

    
    def has_question_word(self, line):
        question_words = ["what", "when", "where", "why", "how", "who", "which", "whom", "whose", 
                              "can you", "will you", "would you", "are you"]
        line = line.strip().lower()
        if any(line.startswith(starting) for starting in question_words):
            return True
        return False
    
       
    def answer_question(self, question):
        completion = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(question + '. Make it concise'),
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        message = completion.choices[0].text
        ans = message.strip()
        return ans


async def handle_questions(a: Answers):
    while True:
        question = await a.question_queue.get()
        print(question)


async def main():
    a = Answers()
    await asyncio.gather(a.audio_source(), a.process(), handle_questions(a))


if __name__ == '__main__':
    asyncio.run(main())
