from computers.models import Computer
from booking.models import TimePeriod, Session
from config.settings import DEBUG
from config.config import AMOUNT_OF_SESSIONS_IN_A_DAY_FOR_ONE_USER


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
        from time import time as time_lib
        start_lib_time = time_lib()
        ready_to_book_dict = self.__ready_to_book_dict.copy()
        now_time_index = 0
        if not(DEBUG):
            now_time_str = TimePeriod.get_now_time_str() # текущее время в виде "16:45"
            if DEBUG: print(TimePeriod.get_closest_time_div_15(now_time_str))
            try: 
                if DEBUG: print("Ближайший временной промежуток, делящийся на 15:",TimePeriod.get_closest_time_div_15(now_time_str))
                now_time_index = self.__ready_to_book_list.index(TimePeriod.get_closest_time_div_15(now_time_str))
            except ValueError: # времени уже больше, чем крайняя граница 
                if not(TimePeriod.compare_two_str_time(now_time_str, self.__ready_to_book_list[0])):
                    if DEBUG: print('Времени еще меньше, чем крайняя левая граница.')
                    now_time_index = 0
                else:
                    if DEBUG: print('Времени уже больше, чем крайняя правая граница.')
                    now_time_index = len(self.__ready_to_book_list) - 1 
        if DEBUG: print(f"Ближайшее время к текущему - {self.__ready_to_book_list[now_time_index]}")
        for time_i in range(now_time_index, len(self.__ready_to_book_list)-4): # идем от индекса текущего времени(чтобы нельзя было забронировать на прошлое)
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
    
    def get_right_edge_yellow(self, time:str) -> str:
        """ Получает 16:45, возвращает 18:00 """
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

    def is_possible_to_book(self, user_vk_id:int, start_test_time:str) -> bool:

        # !!!!! добавить отчет об отказе брони

        """ Проверяет, можно ли забронировать эту сессию юзеру(подряд 2 нельзя). И соседние сессии тоже бранировать нельзя."""
        sessions = Session.objects.filter(vk_id=user_vk_id).values('time_start')
        
        if DEBUG: print(f" Сессии пользователя {user_vk_id} = {sessions}")
        for s in sessions:
            if abs(self.__ready_to_book_list.index(s['time_start']) - self.__ready_to_book_list.index(start_test_time)) <= 4:
                if DEBUG: print(f"Сессию {s.time_start}:{s.time_end} НЕЛЬЗЯ забронировать! (Пользователь: {user_vk_id})")
                return False
            
            elif sessions.count() >= AMOUNT_OF_SESSIONS_IN_A_DAY_FOR_ONE_USER:
                if DEBUG: print(f"Ограничение по кол-ву сессий для одного юзера в день. (Пользователь: {user_vk_id})")
                return False 
            
        if DEBUG: print(f"Сессию {start_test_time} МОЖНО забронировать! (Пользователь: {user_vk_id})")
        return True
    
    def is_possible_to_book_one_more(self, user_vk_id:int) -> bool:
        """ 
        Функция возвращает False, если пользователь уже забронировал сессию сегодня и его забронированная сессия еще не подошла к концу. 
        True в обратном случае.
        """
        pass

    def get_my_session(self, user_vk_id:int) -> dict:
        """ Возвращает словарь с инфо о забронированной сессии юзера и наличии забронированной сессии. \n {'text':word_session, "status": status} """
        if Session.objects.filter(vk_id=user_vk_id).exists():
            sess = Session.objects.filter(vk_id=user_vk_id).first() ### Потом поменять или добавить проверку на сессий > 1
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
