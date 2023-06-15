from computers.models import Computer
from booking.models import TimePeriod, Session
from notifications.models import Notification
from config.settings import DEBUG
from config.config import AMOUNT_OF_SESSIONS_IN_A_DAY_FOR_ONE_USER, SESSION_START_TEXT

from time import time as time_lib


class Bot():
    """ Класс бота. Создается 1 раз при запуске скрипта. """

    def __init__(self):
        self.__ready_to_book_dict = self._generate_time_periods(output_type='dict') 
        self.__ready_to_book_list = self._generate_time_periods(output_type='list')
    
    def get_ready_to_book_dict(self):
        """ Возвращает словарь доступных для бронирования временных интервалов. """
        return self.__ready_to_book_dict
    
    def get_ready_to_book_list(self):
        """ Возвращает список доступных для бронирования временных интервалов. """
        return self.__ready_to_book_list
    
    def _generate_time_periods(self, output_type='dict'):
        """
        Генерирует временные интервалы в формате словаря или списка.
        
        Параметры:
        - output_type (str): Формат вывода временных интервалов. Допустимые значения: 'dict' (по умолчанию), 'list'.

        Возвращает:
        - Временные интервалы в указанном формате ('dict' или 'list').
        """
        times = [f'{hour}:{minute:02d}' for hour in range(16, 23) for minute in range(0, 46, 15)]
        return {time: None for time in times} if output_type == 'dict' else times
    
    def find_free_time_to_book(self) -> dict:
        """ Ищет свободные временные промежутки для бронирования"""
        
        start_lib_time = time_lib()
        ready_to_book_dict = self.__ready_to_book_dict.copy()
        now_time_index = -1
        if not(DEBUG):
            now_time_str = TimePeriod.get_now_time_str() # текущее время в виде "16:45"
            if DEBUG: print(TimePeriod.get_closest_time_div_15(now_time_str))
            try: 
                if DEBUG: print("Ближайший временной промежуток, делящийся на 15:",TimePeriod.get_closest_time_div_15(now_time_str))
                now_time_index = self.__ready_to_book_list.index(TimePeriod.get_closest_time_div_15(now_time_str))
            except ValueError: # времени уже больше, чем крайняя граница 
                if not(TimePeriod.compare_two_str_time(now_time_str, self.__ready_to_book_list[0])):
                    if DEBUG: print('Времени еще меньше, чем крайняя левая граница.')
                    now_time_index = -1
                else:
                    if DEBUG: print('Времени уже больше, чем крайняя правая граница.')
                    now_time_index = len(self.__ready_to_book_list) - 1 
        if DEBUG: print(f"Ближайшее время к текущему - {self.__ready_to_book_list[now_time_index]}")
        for time_i in range(now_time_index + 1, len(self.__ready_to_book_list)-4): # идем от индекса текущего времени(чтобы нельзя было забронировать на прошлое)
            time = self.__ready_to_book_list[time_i]
            if ready_to_book_dict[time] == None: # Свободный компьютер уже есть. Если None - то свободного компьютера нет.
                for pc in Computer.objects.filter(ready_to_use=True): # Проходимся по всем компьютерам
                    is_free = 1 # показывает, что стартовое время и времена +15, +30, +45, +60 минут тоже не забронированы.
                    for i in range(5):
                        tp = pc.time_periods.filter(time=self.__ready_to_book_list[time_i+i], status="F") # Просматриваем, свободен ли данный временной промежуток у этого компьютера.
                        is_free *= len(tp)
                    if is_free > 0: # Иначе смотрим следующий компьютер
                        ready_to_book_dict[time] = pc # Заносим в список компьютер как готовый приступить к работе в данное время
        print(f"Время выполнения функции find_free_time_to_book = {time_lib() - start_lib_time}")
        return ready_to_book_dict
    
    def get_right_edge(self, time:str) -> str:
        """ Получает 16:45, возвращает 17:45 """
        return self.__ready_to_book_list[(self.__ready_to_book_list.index(time) + 4)]
    
    def get_time_before_end(self, time:str, before_end:int) -> str:
        """ 
        Получает time=17:00, возвращает: 
            5 - 17:55
            10 - 17:50
            15 - 17:45
        """
        end_time_sec = TimePeriod.start_end_time_to_sec(self.get_right_edge(time)) 
        result_time_sec = end_time_sec - (before_end * 60)
        result_time_str = TimePeriod.to_readable(result_time_sec)
        
        return result_time_str
    
    def get_right_edge_yellow(self, time:str) -> str:
        """ Получает 16:45, возвращает 18:00 """
        if time == '21:45': # !!!!!!!!!!!!!!!!!!!!!!!!!!!УЬРАТЬУБРАТЬУБРАТЬУБРАТЬУБРАТЬУБРАТЬ!!!!!!!!!!!!!!!!!!!!!!!!!!
            return '22:45'
        return self.__ready_to_book_list[(self.__ready_to_book_list.index(time) + 5)]
    
    def get_computer(self, time:str):
        """ Получает 16:45, возвращает Computer.link..."""
        computer = self.find_free_time_to_book().get(time)
        if computer is None:
            raise ValueError("No computer available at this time.")
        return computer

    def get_computer_list(self, time:str) -> list: 
        """ Принимает "16:45", возващает список свободных компов на это время."""
        pcs = []
        start_time = time
        end_time = self.get_right_edge_yellow(start_time)
        if DEBUG: print(start_time, end_time)
        tm_check = TimePeriod.objects.filter(time=start_time, status='F')
        for tm in tm_check:
            if TimePeriod.objects.filter(time=end_time, status='F', computer=tm.computer).count() > 0: # крайняя правая граница 
                pcs.append(tm.computer)
        return pcs
        
    def is_message_was_writen(self, data):
        """ Проверяет, было ли сообщение напечатано юзером или отправлено через кнопку."""
        return 'payload' not in data['object']['message']

    def is_possible_to_book(self, user_vk_id:int) -> bool:
        """ 
        Проверяет, можно ли забронировать эту сессию юзеру - \n
        можно бронировать только одну сессию вперед. \n
        Потом бронь открывается только после конца сессии. """

        sessions = Session.objects.filter(vk_id=user_vk_id) 
        now_time = TimePeriod.get_now_time_str()

        if sessions.exists():
            if not(TimePeriod.compare_two_str_time(now_time, sessions.last().time_end)): #####!!!!!!!!1 переписать
                return False
            sessions.last().delete(self)
        return True
    
    def is_pc_available(self, time:str, pc:Computer) -> bool:
        """ 
        Проверяет, можно ли забронировать данный компьютер на данное время.
        """
        # проверяем левую границу временного промежутка
        if TimePeriod.objects.filter(time=time, computer=pc).values('status').first()['status'] == 'F': # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Пример использования values
            # проверяем правую границу временного промежутка
            if TimePeriod.objects.filter(time=self.get_right_edge(time), computer=pc).values('status').first()['status'] == 'F':
                return True
        return False

    def get_my_session(self, user_vk_id:int) -> dict:
        """ Возвращает словарь с инфо о забронированной сессии юзера и наличии забронированной сессии. \n {'text':word_session, "status": status} """
        if Session.objects.filter(vk_id=user_vk_id).exists():
            sess = Session.objects.filter(vk_id=user_vk_id).last() ### Потом поменять или добавить проверку на сессий > 1
            word_session = f"Сессия: \n С {sess.time_start} до {sess.time_end}. \n Компьютер №{sess.computer.number}."
            status = True
        else:
            word_session = "У тебя пока нет забронированных сессий. Давай скорее бронируй!"
            status = False
        return {'text':word_session, "status": status} 
    
    def upload_session_to_timeperiods(self, session):
        """ Обновляет TimePeriod`ы в соответствии с созданной сессией. """
        start_index = self.__ready_to_book_list.index(session.time_start)
        for i in range(6):
            time_period = TimePeriod.objects.filter(time=self.__ready_to_book_list[start_index + i], computer=session.computer).first()
            if time_period is not None:
                time_period.status = "B" if i < 5 else "TB"
                time_period.save()

    def is_session_in_progress(self, user_vk_id:int) -> bool:
        """ 
        True - если сессия пользователя идет сейчас. \n 
        False в обратном.
        """
        now_time = TimePeriod.get_now_time_str()
        if Session.objects.filter(vk_id=user_vk_id).exists():
            sess = Session.objects.filter(vk_id=user_vk_id).last()
            if TimePeriod.compare_two_str_time(sess.time_end , now_time) and TimePeriod.compare_two_str_time(now_time, sess.time_start):
                return True
        return False
    
    def __get_notific_times(self, time:str) -> dict:
        """ Получает time в формате 16:45 - возвращает словарь с данными об уведомлениях. """
        data = {}

        data['start_time'] = time
        data['before_15_end_time'] = self.get_time_before_end(time, 15)
        data['before_10_end_time'] = self.get_time_before_end(time, 10)
        data['before_5_end_time'] = self.get_time_before_end(time, 5)
        data['end_time'] = self.get_right_edge(time)

        return data

    def create_session_notions(self, user_vk_id:int, session:Session) -> None:
        """ 
        Создает уведомления для сессии:
            * О начале сессии
            * За 15 минут до конца
            * За 10 минут до конца
            * За 5 минут до конца
            * О конце сессии
        """
        times = self.__get_notific_times(session.time_start)
        start_time = times['start_time'] 
        before_15_end_time = times['before_15_end_time']
        before_10_end_time = times['before_10_end_time']
        before_5_end_time = times['before_5_end_time']
        end_time = times['end_time']

        ############# START #############
        text = f'{SESSION_START_TEXT}\n Напомню: \n{session.computer}\n{start_time}-{end_time}\n Удачной игры!'
        Notification.objects.create(start_time, text, user_vk_id, 'RTC', 'W', session)
        #################################
        ##### 15 MIN BEFORE THE END #####
        text = f'У тебя осталось 15 минут! Конец в {end_time}!'
        Notification.objects.create(before_15_end_time, text, user_vk_id, 'EW', 'W', session)
        #################################
        ##### 10 MIN BEFORE THE END #####
        text = f'У тебя осталось 10 минут! Конец в {end_time}!'
        Notification.objects.create(before_10_end_time, text, user_vk_id, 'EW', 'W', session)
        #################################
        ##### 5 MIN BEFORE THE END ######
        text = f'У тебя осталось 5 минут! Конец в {end_time}!'
        Notification.objects.create(before_5_end_time, text, user_vk_id, 'EW', 'W', session)
        #################################
        ##### 0 MIN BEFORE THE END ######
        text = 'Сессия окончена! Спасибо за игру! <комментарий, связанный с игрой>'
        Notification.objects.create(end_time, text, user_vk_id, 'EW', 'W', session)
        #################################

        