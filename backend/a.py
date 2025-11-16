from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='vi')
translated_text = translator.translate(text="Hello world")
print(translated_text)