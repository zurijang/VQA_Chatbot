from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from telegram_webhook import bot
from .tasks import is_json_key_present
from .models import DATA_IMAGE, DATA_WORKER, QUESTION, ANSWER
from .text import start, regist, pause, usage
import telegram
import json

def index(request):
    return HttpResponse('ok')

@csrf_exempt # 외부에서 직접적으로 포스트 요청을 받을 수 있게 함
def webhook(request):
    print(request)
    base_path = 'data/' # 이미지 저장되는 기본 경로
    json_string=request.body # 사용자로부터 요청받은 객체 (이미지, 질문, 답)
    telegram_update = json.loads(json_string) # request 객체 -> json 변환
    chatID = telegram_update['message']['chat']['id'] # 채팅방 ID

    try: # 사용자가 userName을 입력안했을 경우 (사용자를 구분하기 힘듬)
        userName = telegram_update['message']['from']['username'] # 사용자 ID
    except KeyError: # userName 미설정 시 이름으로 대체
        userName = telegram_update['message']['from']['last_name'] + telegram_update['message']['from']['first_name']
        print(userName)

    fileName_list = [] # 파일 저장명

    if ((is_json_key_present(telegram_update['message'], 'document')) and (telegram_update['message']['document']['mime_type'] == "image/jpeg" \
        or telegram_update['message']['document']['mime_type'] == "image/png")): # 압축되지않은 Image 형식, 'document' key가 있는지 확인 (True, False)
        
        print('document/image')
        fileID = telegram_update['message']['document']['file_id'] # document의 file_id 추출, 이미지 저장에 활용
        fileUniqueID = telegram_update['message']['document']['file_unique_id'] # document의 file_unique_id 추출, 파일명에 활용

        # 파일명 전처리
        fileName_list.append(base_path)
        fileName_list.append(fileUniqueID)
        fileName_list.append(userName)

        fileName = '_'.join(fileName_list) + '.jpg'

        # 사용자 정보 조회 및 저장
        try:
            print('get worker')
            create_worker = DATA_WORKER.objects.get(WORKER_ID=userName)

        except DATA_WORKER.DoesNotExist:
            print('regist worker')
            create_worker = DATA_WORKER.objects.create(WORKER_ID = userName,
                WORKER_NAME = userName)

        try: # 초기 등록 이미지에 대한 예외처리
            # 사용자가 등록한 이미지 조회
            load_image = DATA_IMAGE.objects.filter(WORKER_ID=userName).order_by('-IMAGE_ID')
            print('image loading')
            print(load_image[0]) # 예외 걸리는 부분

            try: # 연속 이미지 등록에 대한 예외 처리 
                # 조회된 이미지에 대한 질문 조회
                print('question loading')
                load_question = QUESTION.objects.filter(IMAGE_ID=load_image[0]).order_by('-QUESTION_CNT')
                
                # 등록된 질문이 7개이고, 7번째 질문에 답변이 되어있어야 이미지 등록 가능, 혹은 /중지 입력시 (STATUS = 9)
                if ((QUESTION.objects.filter(IMAGE_ID=load_image[0]).count()>=7) and (ANSWER.objects.filter(QUESTION_ID=load_question[0]).count()==1)) \
                    or (load_image[0].STATUS=='9'):
                    # 질문 답 7개 이상 등록 후 이미지 등록할 경우 
                    if QUESTION.objects.filter(IMAGE_ID=load_image[0]).count()>=7:
                        print('CHANGE STATUS to 1')
                        DATA_IMAGE.objects.filter(IMAGE_ID=load_image[0].IMAGE_ID).update(STATUS=1)
                        QUESTION.objects.filter(IMAGE_ID=load_image[0]).update(STATUS=1)

                    # 이미지 경로 DB 저장
                    DATA_IMAGE.objects.create(
                        WORKER_ID = create_worker,
                        IMAGE = fileName)

                    print('이미지 DB 저장 완료')
                    
                    # 이미지 저장
                    file = bot.getFile(fileID)
                    file.download(fileName)
                    text = '데이터 등록을 시작합니다. 1번째 질문을 입력해주세요.'
                    print(fileName)
                    print('이미지 저장 완료')

                else:
                    print('Aleardy regist Image : 이미지 저장 실패')
                    # 요건(7가지 이상의 질답을 넣었거나 /중지를 입력)에 충족되지 않고 이미지를 추가 전송 시 
                    if ANSWER.objects.filter(QUESTION_ID=load_question[0]).count()==1:
                        text = '7개 질문과 그에대한 답을 모두 입력해주세요.\n' + str(load_question[0].QUESTION_CNT + 1) + '번째 질문을 입력하세요.'
                    else:
                        text = '7개 질문과 그에대한 답을 모두 입력해주세요.\n' + str(load_question[0].QUESTION_CNT) + '번째 답을 입력하세요.'
            except IndexError:
                print('Aleardy regist Image : 이미지 연속 등록')
                text = "진행중인 이미지에 대한 질문 답을 모두 입력해주세요."
        
        except IndexError:
            # try:
            print('Regist Image : 사용자 첫 이미지 등록')
            DATA_IMAGE.objects.create(
                    WORKER_ID = create_worker,
                    IMAGE = fileName)
            # 이미지 저장
            file = bot.getFile(fileID)
            file.download(fileName)
            text = '데이터 등록을 시작합니다. 1번째 질문을 입력해주세요.'
            print(fileName)
            print('Succeess Write : 이미지 저장 완료')

            # except IndexError:
            #     print('Not regist Q&A : 사용자 첫 이미지 등록 실패')
            #     text = "7개 질문과 그에대한 답을 모두 입력해주세요."
        
        bot.send_message(chat_id=chatID, text=text)

        # 저장 완료되었을 때 질문 요구
        
    else: # Text 형식, 질문, 답
        if is_json_key_present(telegram_update['message'], 'text'): # TEXT만 받도록, IMAGE 외의 documnet (파일) 거름
            print('TEXT')
            try: # 처음 등록하는 유저가 이미지 등록되지 않은 상태로 질문, 답 할때 예외처리

                print('image loading')
                recent_image = DATA_IMAGE.objects.filter(WORKER_ID=userName)\
                        .order_by('-IMAGE_ID')[0] # 사용자가 등록한 이미지 중 가장 최근 것
                print('question loading')
                load_question = QUESTION.objects.filter(IMAGE_ID=recent_image)\
                        .order_by('-QUESTION_ID') # 사용자가 가장 최근에 등록한 이미지에 대한 질문들

                received_text = telegram_update['message']['text'] # 사용자로부터 입력받은 메시지
                
                # 중간에 사용방법 요청
                if received_text=='/사용방법':
                    print('사용방법')
                    bot.send_message(chat_id=chatID, text=usage)
                    bot.send_message(chat_id=chatID, text='이어서 등록해주세요.')
                    return HttpResponse("사용방법")

                print(type(recent_image.STATUS))

                if recent_image.STATUS=='9':
                    print('중지상태 질문 답 입력')
                    bot.send_message(chat_id=chatID, text="중지되었습니다. 새로운 이미지를 등록해주세요.")
                    return HttpResponse('중지됨')
                
                # 사용자가 질문 답변 입력도중 중지하기를 원할 때
                if received_text=='/중지':
                    print('CHANGE STATUS to 9')
                    DATA_IMAGE.objects.filter(IMAGE_ID=recent_image.IMAGE_ID).update(STATUS=9)
                    QUESTION.objects.filter(IMAGE_ID=recent_image).update(STATUS=9)
                    text = '중지되었습니다. 새로운 이미지를 등록해주세요.'
                    bot.send_message(chat_id=chatID, text=text)
                    return HttpResponse("중지됨")
                
                if received_text[-1] == '?': # 질문 입력받음
                    print('question')
                    try:
                        if load_question.count()==0: # 이미지에 대한 질문 유무확인
                            print('첫 번째 질문 등록')
                            question_cnt = 1 # 질문이 없을 경우 첫 번째 질문
                            # 이미지에 대한 질문 등록 (처음)
                            QUESTION.objects.create(
                                IMAGE_ID=recent_image, # 사용자가 가장 최근에 등록한 이미지
                                QUESTION=received_text, # 입력받은 질문
                                QUESTION_CNT=question_cnt # 이미지에 대한 질문 수
                            )
                            text = str(question_cnt) + '번째 질문에 대한 답변을 입력해주세요.' 
                        else:
                            question_cnt = load_question[0].QUESTION_CNT + 1 # 이미지에 대한 질문이 있을 경우, 기존에 등록된 QUESTION_CNT에서 + 1
                            if ANSWER.objects.filter(QUESTION_ID=load_question[0].QUESTION_ID).count() == 0:
                                print('질문에 대한 답변 없음')
                                text = str(question_cnt-1) + '번째 질문에 대한 답변을 먼저 입력해주세요.' 
                            else:
                                print('질문 등록')
                                # 이미지에 대한 질문 등록 (두번째 이후)
                                QUESTION.objects.create(
                                    IMAGE_ID=recent_image, # 사용자가 가장 최근에 등록한 이미지
                                    QUESTION=received_text, # 입력받은 질문
                                    QUESTION_CNT=question_cnt # 이미지에 대한 질문 수
                                )
                                text = str(question_cnt) + '번째 질문에 대한 답변을 입력해주세요.'

                    except IndexError: # 사용자가 등록한 이미지가 없을 경우
                        print('진행중인 사진 없음')
                        text = '등록된 사진이 없습니다.'

                    bot.send_message(chat_id=chatID, text=text)  

                else:   # 답 입력받음
                    print("answer")
                    try:
                        if ANSWER.objects.filter(QUESTION_ID=load_question[0].QUESTION_ID).count() == 0: # 가장 최근 이미지에 대한 질문의 답을 했는지 확인
                            print('답변 등록')
                            ANSWER.objects.create( # 질문에 대해 등록된 답이 없을 경우 입력받은 답변 등록
                                QUESTION_ID=load_question[0],
                                ANSWER=received_text
                            )

                            # 가장 최근에 등록된 질문수가 7개 이상이면 요구 충족, 추가 이미지 가능 여부 확인
                            if load_question[0].QUESTION_CNT >= 7:
                                print("등록 조건 만족")
                                text = '조건이 충족되었습니다. 추가 질문 입력을 원하시면 ' + str(load_question[0].QUESTION_CNT+1) +'번째 질문을 입력하세요.\n이미지를 업로드하면 새로운 등록이 시작됩니다.'
                            else:
                                print("답변 등록 성공")
                                text = str(load_question[0].QUESTION_CNT+1) + '번째 질문을 입력하세요.'

                        else:
                            print("답변이 이미 존재")
                            text = '새로운 질문을 입력하세요.'
                        
                    except IndexError:
                        print("등록된 질문 아예 없음")
                        text = '등록된 질문이 없습니다.'

                    bot.send_message(chat_id=chatID, text=text)  

            except IndexError: # 등록되지 않은 사용자가 텍스트 입력한 경우
                # text = start
                bot.send_message(chat_id=chatID, text=start)
                bot.send_message(chat_id=chatID, text=regist)
                bot.send_message(chat_id=chatID, text=pause)
        else: # 텍스트, 이미지 외의 파일 전송
            print('압축된 파일 전송')
            text = '''이미지를 전송해주세요.
            android)첨부파일→파일→갤러리(압축 없이 사진 보내기)
            ios)첨부파일→파일→사진및동영상
            web)'send file'통해서 이미지 전송'''
            bot.send_message(chat_id=chatID, text=text)

    return HttpResponse("webhook")