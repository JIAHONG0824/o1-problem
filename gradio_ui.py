from datetime import datetime
import pytz
import os
import openai
import pandas as pd
import re
import gradio as gr
def openai_api(prompt, key):
    openai.api_key = key
    completion = openai.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": prompt}]
        )
    return completion.choices[0].message.content
def extract_option(text):
    # 使用正規表達式來尋找模式 "|sel-D:| 選項D"
    match = re.search(r'\|sel-D:\|\s*(.*?)\s*(?:\||\.$|$)', text)
    if match:
        return match.group(1)  # 返回匹配的部分
    else:
        return "No match found"
def extract_letter(s):
    # 使用正則表達式匹配單獨的A、B、C或D，或括號中的A、B、C或D
    match = re.search(r'\b([A-D])\b|\(([A-D])\)', s)
    # 如果匹配成功，返回匹配的字符
    if match:
        return match.group(1) if match.group(1) else match.group(2)
    return None
def generation(course_name, keywords, num, filename, key):
        q_num = int(num)
        # CSV標題列 題型*  題幹* 難易度* 答案* 正確答案解釋 選項-A 選項-B 選項-C 選項-D
        columns = ['題型*', '題幹*', '難易度*', '答案*', '正確答案解釋', '選項-A', '選項-B', '選項-C', '選項-D', '考生一作答', '考生二作答', '考生三作答', '驗證通過']
        data = {}
        df = pd.DataFrame()

        for num in range(1, q_num+1) :
                # 第一階段：「生考題」提問
                prompt1 = "請扮演命題專家，並注意下列原則與命題關鍵字，請挑選適合關鍵字以出題一題，\
                原則1：單選題四個選項包含：A、B、C、D。難易度為難、中、易。\
                原則2：考試目標屬於初階認證考試，通過考試者，代表理解初步概念，同時要有專業程度。\
                原則3：禁止命題否定問句，禁止選項出現「以上皆是」或「以上皆非」。\
                原則4：輸出格式(但不用出現本句)：|type:| 題型 |quiz:| 題幹 |level:| 難易度 |answer:| 答案 |solution:| 正確答案解釋 |sel-A:| 選項A |sel-B:| 選項B |sel-C:| 選項C |sel-D:| 選項D \
                原則5：以提升題目難度方式，採多層推理、情境題、結合多個概念、精確理解的干擾選項設計。\
                原則6：以繁體中文來命題。\
                原則7：課程名稱：" + course_name + "。命題關鍵字： " + keywords
                response = openai_api(prompt1, key)
                #出題
                quiz = response.split("|quiz:|")[1].split("|level:|")[0].strip() + " (A) " + response.split("|sel-A:|")[1].split("|sel-B:|")[0].strip() +" (B) " + response.split("|sel-B:|")[1].split("|sel-C:|")[0].strip() +" (C) " + response.split("|sel-C:|")[1].split("|sel-D:|")[0].strip() +" (D) " + extract_option(response)
                #正確答案
                qanswer = extract_letter(response.split("|answer:|")[1].split("|solution:|")[0].strip())
                qtype = response.split("|type:|")[1].split("|quiz:|")[0].strip()
                qlevel = response.split("|level:|")[1].split("|answer:|")[0].strip()
                qsolution = response.split("|solution:|")[1].split("|sel-A:|")[0].strip()

                # 第二階段：「考題審查」提問
                #prompt2="依下列原則，請扮演審題專家，檢查考題內容及選項並符合格式輸出。\
                #原則1：盡量少用「否定問句」或「否定敘述選項」。\
                #原則2：不要使用「以上皆是」和「以上皆非」的答案。\
                #原則3：請避免爭議題，混淆、主觀、誤導、描述不清、定義不明、多個選項皆可算分。\
                #原則4：請避免送分題，考同樣的知識點，只是換句話說的題目。\
                #考題內容："+quiz+"。\
                #輸出格式：若「違背」出題原則，請提供「專家建議」，若「未違背」可以直接回覆「No」不用多以解釋";
                #quiz_suggest = openai_api(prompt2, key);

                # 第三階段：「依專家建議調整」提問
                #prompt3="請扮演出題專家，依據下列「專家意見」更新「考題內容」並依格式輸出。\
                #原則1：題型出單選題，即以「單選題」回覆。\
                #原則2：答案以「A、B、C、D」依題幹作回覆。難易度以「難、中、易」擇一回覆。\
                #原則3：輸出格式(但不用出現本句)：|type:| 題型 |quiz:| 題幹 |level:| 難易度 |answer:| 答案 |solution:| 正確答案解釋 |sel-A:| 選項A |sel-B:| 選項B |sel-C:| 選項C |sel-D:| 選項D \
                #原則4：以繁體中文來命題。考題內容："+ quiz +"。\
                #原則5；專家意見："+ quiz_suggest;

                #if quiz_suggest != "No" :
                #      response2 = openai_api(prompt3, key);
                #else:
                #      response2 = response

                #quiz = response2.split("|quiz:|")[1].split("|level:|")[0].strip() + " (A) " + response2.split("|sel-A:|")[1].split("|sel-B:|")[0].strip() +" (B) " + response2.split("|sel-B:|")[1].split("|sel-C:|")[0].strip() +" (C) " + response2.split("|sel-C:|")[1].split("|sel-D:|")[0].strip() +" (D) " + extract_option(response2)
                #qanswer = extract_letter(response2.split("|answer:|")[1].split("|solution:|")[0].strip())
                #qtype = response2.split("|type:|")[1].split("|quiz:|")[0].strip()
                #qlevel = response2.split("|level:|")[1].split("|answer:|")[0].strip()
                #qsolution = response2.split("|solution:|")[1].split("|sel-A:|")[0].strip()
                #if qanswer == None :   qanswer = "E"

                print("第"+str(num)+"題：")
                print(quiz)
                print("答案："+qanswer)

                # 第四階段：「考生一號試考」提問
                prompt4="請回覆答案(A、B、C、D)即可不用解釋，請扮演「機器學習」考題專家並注意下列原則。\
                原則1：考題專家具了解演算法、數據前處理、模型訓練、評估方法以及機器學習的最新進展。\
                原則2：教育背景具統計分析、人工智慧、數據分析，可持續發展或相關領域的高等教育背景。\
                原則3：考試的常勝軍，每次都可以考第一名，都可以考滿分。\
                原則4：考題內容："+quiz
                ans_tester1= openai_api(prompt4, key)

                # 第五階段：「考生二號試考」提問
                prompt5="請回覆答案(A、B、C、D)即可不用解釋，請扮演「人工智慧」考題專家並注意下列原則。\
                原則1：考題專家具人工智慧的專業知識（包括機器學習、自然語言處理、計算機視覺等），包括對基本理論、算法、實踐應用和行業趨勢的全面掌握。\
                原則2：教育背景具備人工智慧知識，該領域為一個快速發展的領域，專家需要不斷學習和更新知識，以确保考题内容的时效性和前瞻性。\
                原則3：考試的常勝軍，每次都可以考第一名，都可以考滿分。\
                原則4：考題內容："+ quiz
                ans_tester2= openai_api(prompt5, key)

                # 第六階段：「考生三號試考」提問
                prompt6="請回覆答案(A、B、C、D)即可不用解釋，請扮演「數據分析」考題專家並注意下列原則。\
                原則1：考題專家具擁有數據分析深厚知識，包括數據處理、統計分析、機器學習、數據視覺化等。\
                原則2：教育背景具備數據分析領域的最新發展和趨勢，並保證考題的邏輯性和合理性。\
                原則3：考試的常勝軍，每次都可以考第一名，都可以考滿分。\
                原則4：考題內容："+ quiz
                ans_tester3= openai_api(prompt6, key)

                print("考生一作答："+ans_tester1+"\n"+"考生二作答："+ans_tester2+"\n"+"考生三作答："+ans_tester3)

                data[num] = {'題型*': qtype,'題幹*': response.split("|quiz:|")[1].split("|level:|")[0].strip(),'選項-A': response.split("|sel-A:|")[1].split("|sel-B:|")[0].strip(),
                      '選項-B': response.split("|sel-B:|")[1].split("|sel-C:|")[0].strip(),'選項-C': response.split("|sel-C:|")[1].split("|sel-D:|")[0].strip(),
                      '選項-D': extract_option(response),'答案*': qanswer,'正確答案解釋': qsolution,'難易度*': qlevel,
                      '驗證通過': extract_letter(ans_tester1) == extract_letter(ans_tester2) == extract_letter(ans_tester3) == extract_letter(qanswer),'考生一作答': ans_tester1,'考生二作答': ans_tester2,'考生三作答': ans_tester3}
                print(extract_letter(ans_tester1))
                print(extract_letter(ans_tester2))
                print(extract_letter(ans_tester3))

        taipei_tz = pytz.timezone('Asia/Taipei')
        current_time_taipei = datetime.now(taipei_tz)
        current_time_taipei
        data_list = [value for key, value in data.items()]
        df = pd.DataFrame(data_list, columns=columns)
        df = df.applymap(lambda x: x.replace('|', '') if isinstance(x, str) else x)
        filename = current_time_taipei.strftime("%Y%m%d%H%M%S")+"_"+filename + ".csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
with gr.Blocks() as demo:
    with gr.Row():
        api_key_input = gr.Textbox(label="Enter OpenAI API Key", placeholder="OpenAI API 金鑰")
        filename_input = gr.Textbox(label="考題檔案名稱", placeholder="檔案名稱")
        course_input = gr.Textbox(label="課程名稱", placeholder="課程名稱")
        keywords_input = gr.Textbox(label="生題關鍵字", placeholder="關鍵字")
        q_num_input = gr.Textbox(label="生成題數", placeholder="題數")
        submit_button = gr.Button("生成考題")
    file_output = gr.File(label="Download CSV")

    submit_button.click(
        generation,
        inputs=[course_input, keywords_input, q_num_input, filename_input, api_key_input],
        outputs=[file_output]
    )