import whisper
from transformers import pipeline, AutoTokenizer
import opencc
import re

def speech_to_text(audio_file):
    """轉換語音到文字"""
    model = whisper.load_model("medium.en")
    result = model.transcribe(audio_file)
    return result["text"]

def clean_text(text):
    """清理和標準化文本"""
    # 移除多餘的空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 確保標點符號前沒有空格
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    return text

def split_into_sentences(text):
    """智能分句"""
    # 在常見的句子結束符號後分割
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # 過濾空句子並清理
    return [clean_text(s) for s in sentences if s.strip()]

def translate_chunk(chunk, translator):
    """翻譯單個文本塊"""
    try:
        result = translator(chunk, max_length=512)
        return result[0]['translation_text']
    except Exception as e:
        print(f"翻譯錯誤: {str(e)}")
        print(f"問題文本: {chunk}")
        return chunk

def translate_to_traditional_chinese(english_text):
    """將英文翻譯成繁體中文"""
    try:
        # 初始化翻譯器
        translator = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-en-zh",
            device="mps"  # 在 Mac 上使用 MPS 加速
        )
        
        # 分句
        sentences = split_into_sentences(english_text)
        
        # 分批翻譯
        translated_parts = []
        batch_size = 3  # 每次翻譯3個句子
        
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            batch_text = " ".join(batch)
            translation = translate_chunk(batch_text, translator)
            translated_parts.append(translation)
        
        # 合併翻譯結果
        simplified_text = "".join(translated_parts)
        
        # 後處理
        simplified_text = post_process_chinese(simplified_text)
        
        # 轉換成繁體中文
        converter = opencc.OpenCC('s2t')
        traditional_text = converter.convert(simplified_text)
        
        return traditional_text
        
    except Exception as e:
        print(f"翻譯過程發生錯誤: {str(e)}")
        return None

def post_process_chinese(text):
    """後處理中文文本"""
    # 移除不必要的空格
    text = re.sub(r'\s+', '', text)
    # 修正標點符號
    text = text.replace(' ,', '，')
    text = text.replace(' .', '。')
    text = text.replace(' ?', '？')
    text = text.replace(' !', '！')
    text = text.replace('，', '，\n')  # 在逗號後添加換行
    text = text.replace('。', '。\n')  # 在句號後添加換行
    text = text.replace('？', '？\n')  # 在問號後添加換行
    text = text.replace('！', '！\n')  # 在驚嘆號後添加換行
    return text

def format_output(text):
    """格式化輸出文本"""
    return text.strip()

if __name__ == "__main__":
    # 指定音訊檔案路徑
    audio_file = "/Users/dylan/Documents/python/新錄音 7.m4a"
    
    # 語音轉文字
    print("正在進行語音辨識...")
    english_text = speech_to_text(audio_file)
    print("\n語音辨識結果 (英文):")
    print(format_output(english_text))
    print("\n正在翻譯...")
    
    # 翻譯成繁體中文
    traditional_chinese_text = translate_to_traditional_chinese(english_text)
    print("\n翻譯後的繁體中文:")
    if traditional_chinese_text:
        print(format_output(traditional_chinese_text))
    else:
        print("翻譯失敗")