import vk_api
from random import randint
import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from config.settings import DEBUG
from config.config import TOKEN, CONFIRMATION_TOKEN, SECRET_KEY
from booking.models import TimePeriod, Computer
from booking.bot import Bot
from booking.models import Session

### git add . ; git commit -m "replace 1 to not(debug)"; git push origin main

bot = Bot()

phrase1 = "Приветствую! Я бот, через которого можно забронировать место в киберспортивном компьютерном клубе по адресу СПб, Дальневосточный пр-кт, 71. Вход рядом со входом в общежитие."
phrase2 = "https://vk.com/id756821329 \n Администратор работает с 16:00 до 20:00"

def _get_random_id() -> int:
    """ Требуется для отправки сообщений vk. """
    return randint(0, 9999)

def send_message(user_id: int, message: str, keyboard=None):
    api = vk_api.VkApi(token=TOKEN)
    response = api.method(
        'messages.send',
        {
            'user_id': user_id,
            'message': message,
            'v': '5.131',
            'random_id': _get_random_id(),
            'keyboard': keyboard
        }
    )
    return response

def get_good_response(message="ok") -> HttpResponse:
    """ Возвращает положительный ответ ok, требуемый VK."""
    return HttpResponse(message, content_type="text/plain", status=200)

def create_kb_book(can_book:bool) -> VkKeyboard:
    """ Возвращает клавиатуру с главным меню.\n can_book - может ли пользователь бронировать новые сессии."""
    keyboard = VkKeyboard(one_time=True)
    if can_book: 
        keyboard.add_button("Забронировать ПК", color=VkKeyboardColor.POSITIVE, payload=json.dumps({"button_text": "Забронировать ПК"}))
        keyboard.add_line()
    keyboard.add_button("Мои сессии", color=VkKeyboardColor.POSITIVE, payload=json.dumps({"button_text": "Мои сессии"}))
    keyboard.add_line()
    keyboard.add_button("Связаться с администратором", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"button_text": "Связаться с администратором"}))
    return keyboard.get_keyboard()

def create_choose_time() -> tuple:
    """ 
    Генерирует клавиатуру с доступными для брони временами.\n
    Возвращает: (VkKeyboard, bool) \n 
    bool - True, если есть места для бронирования. False в обратном случае.
    """

    ######## Кэширование ########
    amount_of_sessions = Session.objects.count() # получаем кол-во сессий
    if DEBUG: print(f"Кол-во сессий: {amount_of_sessions}")
    amount_of_sessions_cache = cache.get('amount_of_sessions', default=None)
    if DEBUG: print(f"Кол-во сессий в кэше: {amount_of_sessions_cache}")
    if amount_of_sessions != amount_of_sessions_cache: # Если появились новые сессии, то обновляем список доступных временных промежутков
        if DEBUG: print(f"В базе данных появились новые сессии.")
        free_times = bot.find_free_time_to_book()
        cache.set('free_times', free_times, 60*60)
        cache.set('amount_of_sessions', amount_of_sessions, 60*60)
    else:
        value = cache.get('free_times', default=None)
        if DEBUG: print(f"Беру free_times из кэша."); print(f'Значение по ключу free_times в кешэ: {value}')
        if value is None:
            free_times = bot.find_free_time_to_book()
            cache.set('free_times', free_times, 60*60)
        else:
            free_times = cache.get('free_times') # get_or_set(key, default, timeout=DEFAULT_TIMEOUT): Возвращает значение, если оно существует в кэше. Если значение не существует, устанавливает и возвращает значение по умолчанию.
    #############################
    
    keyboard = VkKeyboard(one_time=True)
    all_times_list = bot.get_ready_to_book_list()
    count = 0
    for t in range(len(all_times_list)-4): # проходимся по списку всех возможных времен
        if free_times[all_times_list[t]] != None: # если есть компьютер, который на данное время не занят
            keyboard.add_button(f"{all_times_list[t]}-{all_times_list[t+4]}", color=VkKeyboardColor.POSITIVE, payload=json.dumps({"button_text": all_times_list[t]}))
            count += 1
            if count % 3 == 0 and count != 0:
                if t == (len(all_times_list)-5): 
                    break
                keyboard.add_line()
    if count != 0: 
        keyboard.add_line()
    keyboard.add_button("Главное меню", color=VkKeyboardColor.NEGATIVE, payload=json.dumps({"button_text": "Главное меню"}))
    return keyboard.get_keyboard(), not(bool(count)) 

def create_choose_pc(time:str) -> VkKeyboard:
    """ 
    Генерирует клавиатуру с доступными для брони компами. \n
    Принимает time в формате 16:00. 
    """
    computers = bot.get_computer_list(time)
    line_above = False 
    keyboard = VkKeyboard(one_time=True)
    count = 0
    for pc in computers:
        keyboard.add_button(str(pc), color=VkKeyboardColor.POSITIVE, payload=json.dumps(f"{str(pc.number)}+{time}"))
        line_above = False
        if DEBUG: print(f"Кнопка{count+1} Строка {count//3 + 1}")
        count += 1
        if count % 3 == 2 and not(line_above):
            keyboard.add_line() 
            line_above = True
    if not(line_above):
        keyboard.add_line()
    keyboard.add_button("Главное меню", color=VkKeyboardColor.NEGATIVE, payload=json.dumps({"button_text": "Главное меню"}))
    return keyboard.get_keyboard()

def get_clear_keyboard() -> VkKeyboard:
    """ Возвращает пустую клавиатуру. \n 
    Используется для удаления клавиатуры. """
    keyboard = VkKeyboard(one_time=True)
    return keyboard.get_empty_keyboard()

def get_message_text(data) -> str:
    """Получение текста сообщения."""
    return data['object']['message']['text']

def get_button_text(data) -> str:
    """Получение текста из payload кнопки."""
    return data['object']['message']['payload'].replace('"','')

def get_vk_id(data) -> int:
    """ Получение vk id из сообщения, присланного пользователем. """
    try:
        return data['object']['message']['from_id']
    except KeyError: # когда пришло событие от callback кнопки
        return data['object']['peer_id']

def create_keyboard_my_session() -> VkKeyboard:
    """ 
    Генерирует клавиатуру с кнопками и текстом: 
    а) Описание забронированной сессии
    б) Главное меню
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Отменить бронь", color=VkKeyboardColor.NEGATIVE, payload=json.dumps({"button_text": "Отменить бронь"}))
    keyboard.add_line()
    keyboard.add_button("Главное меню", color=VkKeyboardColor.PRIMARY, payload=json.dumps({"button_text": "Главное меню"}))
    return keyboard.get_keyboard()

def handle_computer_booking(data, user_vk_id:int, can_book:bool) -> None:
    """ Срабатывает, когда пользователь нажимает на кнопку с номером компьютера."""
    payload = get_button_text(data)
    start_time = payload.split('+')[1]
    pc_number = int(payload.split('+')[0])
    end_time = bot.get_right_edge(start_time)
    computer = Computer.objects.get(number=pc_number)
    if bot.is_pc_available(start_time, computer):
        session = Session.objects.create(time_start=start_time, time_end=end_time, computer=computer, vk_id=user_vk_id)
        bot.upload_session_to_timeperiods(session)
        send_message(user_vk_id, f'Время забронировано! Твой сеанс: {start_time}-{end_time}.\n Компьютер №{pc_number}. \nДанные для входа в систему компьютера: \n<login> \n<password>', create_kb_book(can_book=False))
    else:
        send_message(user_vk_id, f'Упс... Этот сеанс уже забронировал кто-то другой', create_kb_book(can_book))
   
@csrf_exempt
def index(request):
    if request.method != "POST":
        return get_good_response()
    
    data = json.loads(request.body)

    if data['type'] == 'confirmation': 
        return confirm(request)
    
    user_vk_id = get_vk_id(data) # получение VK ID пользователя
    can_book = bot.is_possible_to_book(user_vk_id) # Может ли пользователь бронировать сессии

    if DEBUG:
        print("--------------------КЭШ--------------------")
        print(f"amount_of_sessions = {cache.get('amount_of_sessions')}")
        print(f"free_times = {cache.get('free_times')}")
        print("-------------------------------------------")

    if data['type'] == 'message_new':
        if not(DEBUG):
            if bot.is_message_was_writen(data):
                if DEBUG: print("Введено сообщение с клавиатуры.")
                send_message(user_vk_id, f'Используй кнопки, пожалуйста!', create_kb_book(can_book))
                return get_good_response()
        butt_text = get_message_text(data)
        if DEBUG:
            print("Новое сообщение с кнопки ", f"= '{butt_text}'")
            print('-------------------------------------------------------------------')
            print(data)
            print('-------------------------------------------------------------------')

        if butt_text == "Забронировать ПК":
            text = "Выбери время бронирования:"
            keyboard, no_places = create_choose_time()
            
            if no_places:
                text = "К сожалению, мест уже нет. Приходи завтра!"
            send_message(user_vk_id, text, keyboard) 
        
        if butt_text == "Главное меню":
            send_message(user_vk_id, "Главное меню", create_kb_book(can_book))
        
        if butt_text == "Отменить бронь":
            Session.objects.get(vk_id=user_vk_id).delete(bot=bot)
            can_book = True
            send_message(user_vk_id, "Бронь отменена! \nТеперь ты снова можешь забронировать сессию!", create_kb_book(can_book))
        
        if butt_text == "Мои сессии": 
            sesion_data = bot.get_my_session(user_vk_id)
            text = sesion_data['text']
            status = sesion_data['status']
            if not(status): # Если у пользователя нет забронированных сессий
                send_message(user_vk_id, text, create_kb_book(can_book))
            else: 
                send_message(user_vk_id, text, create_keyboard_my_session())

        if butt_text == "Связаться с администратором":
            send_message(user_vk_id, phrase2, create_kb_book(can_book))

        if butt_text == "Начать":
           send_message(user_vk_id, phrase1, create_kb_book(can_book))
        
        start_time = butt_text.split('-')[0]
        if start_time in bot.get_ready_to_book_list():
            if bot.is_possible_to_book(user_vk_id):
                send_message(user_vk_id, f'Выбери компьютер для бронирования:', create_choose_pc(start_time))
            else:
                send_message(user_vk_id, f'Извини, но у тебя уже есть сессия. Ждем тебя в XX:XX!', create_choose_time()[0])
        if 'ПК №' in butt_text:
            handle_computer_booking(data, user_vk_id, can_book)
        return get_good_response()

@csrf_exempt
def confirm(request):
    data = json.loads(request.body)
    if DEBUG: print("confirm вызван")

    if data['secret'] != SECRET_KEY:
        if DEBUG: print('SECRET_KEY неверен!')
        return HttpResponse("SECRET_KEY неверен!", content_type="text/plain", status=500) # !!!!!!!!!!!!!!!!!!!!!!!!

    if DEBUG: print("Удачная проверка токена!")
    return get_good_response(CONFIRMATION_TOKEN)

@login_required
def info(request):
    """ Страница для просмотра информации о забронированных компах. """
    if not(request.user.is_authenticated):
        return redirect('admin:index')
    computers = Computer.objects.all().iterator()
    context = {'computers':computers}
    return render(request, "booking/index.html", context)

@login_required
def free_sessions(request):
    """ Отменяет все брони и удаляет все сессии. """
    Session.objects.all().delete()
    times = TimePeriod.objects.all().iterator() # https://django.fun/ru/articles/tips/sovety-po-optimizacii-raboty-s-bazoj-dannyh-v-django/
    for time in times:
        if time.status != 'F':
            time.status = 'F'
            time.save()
    return HttpResponse("Все брони на этот день сброшены!")