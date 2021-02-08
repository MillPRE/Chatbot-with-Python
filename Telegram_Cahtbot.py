from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters, MessageHandler
import telegram
import json
import requests
from urllib.parse import urlencode
from urllib.parse import unquote
from datetime import date


token = "1658456550:AAETklKoKSPTdh8sdtw2A1UuPikxxyyWi0E"
bot = telegram.Bot(token)

dictionary = {"서울":'060127',
	'부산':'098076',
	'대구':'080090',
	'인천':'055124',
	'광주':'058074',
	'대전':'067100',
	'울산':'102084',
	'세종':'066103',
	'제주도':'052038',
	'춘천':'073134',
	'강릉':'092131',
	'울릉':'127127',
	'수원':'061120',
	'청주':'067106',
	'안동':'091106',
	'전주':'063089',
	'목포':'050067',
	'창원':'090077',
	'여수':'073066',
	}

# 19개
dic_list = ['서울','부산','대구','인천','광주','대전','울산','세종','제주도','춘천','강릉','울릉','수원','청주','전주','안동','목포','창원','여수']

# updater, dispatcher
updater = Updater(token = token , use_context = True)
dispatcher = updater.dispatcher

# commandHandler
def start(update, context):
	context.bot.send_message(chat_id =update.message.chat.id, text="*** Weather ChatBot Command ***\n- /start : 챗봇 명령어 설명\n- /nation : 전국 날씨 알림 명령어\n- /도시 : 각 도시별 날씨 알림 명령어\n - ex) /서울")

# parser 
def parser(update, context):
	chat_id = update.message.chat.id
	chat_text = update.message.text

	if(chat_text[0] == "/"):
		command = chat_text.split("/")[1]
		for i in range(19):
			if(dic_list[i] == command):
				xy = dictionary[command]
				x = int(xy[0:3])
				y = int(xy[3:])
				msg = "*** 오늘 "+command+"의 날씨 ***"
				msg = msg + getAPI(command,x,y)
				context.bot.send_message(chat_id = chat_id, text = msg)
				break



	else:
		context.bot.send_message(chat_id = chat_id,text = "Plz Input Command.")
		start(update,context)

	

# 기상청 API GET
def getAPI(keyword, x, y):
	url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtNcst"

	now_dt = date.today().strftime('%Y%m%d')

	queryString = "?" + urlencode(
	{
		"ServiceKey": unquote("h%2BlThqku8jtCoWqMW5dC0X5b%2BPBPNOzI5eWlCoEZSBcsDZFZ04KvSFthtKG%2Fd6sw9Rt56s2hO%2F7Ph1Y4mGNt6Q%3D%3D"),
  		"base_date": now_dt,
  		"base_time": "1200",
  		"nx": x,
  		"ny": y,
	  	"numOfRows": "10",
  		"pageNo": 1,
  		"dataType": "JSON" 
		}
	)

	
	queryURL =url + queryString
	response = requests.get(queryURL)
	msg = response.text

	r_text = json.loads(response.text)
	r_response = r_text.get("response")
	r_body = r_response.get("body")
	r_items = r_body.get("items")
	r_item = r_items.get("item")

	result = {}

	for i in r_item :
		if(i.get("category") == "T1H"):
			result["T1H"] = i
			break

	for i in r_item :
		if(i.get("category") == "RN1"):
			result["RN1"] = i
			break

	for i in r_item :
		if(i.get("category") == "REH"):
			result["REH"] = i
			break
	
	result_msg = "\n"+keyword+" "+result["T1H"].get("obsrValue")+"C "+result["RN1"].get("obsrValue")+"mm "+result["REH"].get("obsrValue")+"%\n"
	return result_msg

# 전국 날씨 ( /nation )
def nation(update,context):
	chat_id = update.message.chat.id
	print_msg = "***** 전국 날씨 *****\n\n지역 온도 강수량 습도\n"

	for i in dic_list :
		Txy = dictionary[i]
		Tx = int(Txy[0:3])
		Ty = int(Txy[3:])
		tmp_msg = getAPI(i,Tx,Ty)
		print_msg = print_msg + tmp_msg
	
	context.bot.send_message(chat_id = chat_id, text = print_msg)

# 메인 함수
def main():
	start_handler = CommandHandler('start',start)
	parser_handler = MessageHandler(Filters.text & (~Filters.command),parser)
	nation_handler = CommandHandler('nation',nation)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(parser_handler)
	dispatcher.add_handler(nation_handler)

	# polling
	updater.start_polling()



if __name__ == "__main__":
	main()
