from abc import ABC, abstractmethod
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showinfo, showerror
from threading import Thread, Lock
import time
import random
import os

class AbstractSnake(ABC):
    @abstractmethod
    def __init__(self, body: list, body_color: str, head_color: str, speed: int): pass

    @abstractmethod
    def move(self): pass

    @abstractmethod
    def create_snake(self): pass

    @abstractmethod
    def eat_apple(self): pass

    @abstractmethod
    def death(self): pass

class Snake(AbstractSnake):
    def __init__(self, x=8, y=15, body_color="#04859D", head_color="#5FBDCE", speed = 0.15):
        # Установление цветов змейки
        self.body_color = body_color
        self.head_color = head_color

        # Список со списками координат каждой части змеи (порядок: 1й - голова, и так далее)
        # То есть self.bodys_cords[0][0] - column/x, self.bodys_cords[0][1] - row/y
        self.bodys_cords = [[x, y], (x, y+1)]

        # Список виджетов tkinter с участками змеи (по порядку, от головы до её конца)
        self.body = [Label(background=self.head_color), Label(background=self.body_color)] 

        self.last_move = '' # Последнее направление движения (начать можно в любом направлении)

        # Координаты клетки перед последним участком тела
        # Нужно для того, чтобы при поедании яблока новый участок сразу появлялся
        self.last_cords = []

        # Флаг для контроля движения и потоков
        self.ismoving = True

        self.speed = speed # Скорость передвижения змейки

    # Первоначальное отображение змейки
    def create_snake(self):
        self.body[0].grid(row=self.bodys_cords[0][1], column=self.bodys_cords[0][0], sticky='nsew')
        self.body[1].grid(row=self.bodys_cords[1][1], column=self.bodys_cords[1][0], sticky='nsew')

    # Передвижение змейки, проверка мертва ли она и съела ли она яблоко
    def move(self, event, apple, root):
        while self.ismoving: # Движение только тогда, когда змейка двигается (self.ismoving = True)
            # Сохраняем значение координат головы змейки, чтобы на их место
            # Поставить другой участок тела змейки (последний)
            last_head_place = tuple(self.bodys_cords[0])

            # Изменение координат головы змейки в зависимости от направления движения
            match event.char.lower():
                case 'w':
                    self.last_move = 'up'
                    self.bodys_cords[0][1] -= 1 # Вертикаль инвертирована, самый верх - 0, самый низ - 16
                    if self.bodys_cords[0][1] < 0:
                        self.bodys_cords[0][1] += 17
                case 's':
                    self.last_move = 'down'
                    self.bodys_cords[0][1] += 1 # Вертикаль инвертирована, самый верх - 0, самый низ - 16
                    if self.bodys_cords[0][1] > 16:
                        self.bodys_cords[0][1] -= 17
                case 'a':
                    self.last_move = 'left'
                    self.bodys_cords[0][0] -= 1 # С горизонталью всё нормально
                    if self.bodys_cords[0][0] < 0:
                        self.bodys_cords[0][0] += 17
                case 'd':
                    self.last_move = 'right'
                    self.bodys_cords[0][0] += 1 # Вертикаль инвертирована, самый верх - 0, самый низ - 16
                    if self.bodys_cords[0][0] > 16:
                        self.bodys_cords[0][0] -= 17

            # Алгоритм перемещения тела змеи:
            # В last_cords записывается место этого участка
            # Последний участок змеи встаёт на место головы (до изменения, через last_head_place)
            # Перемещаем координаты последнего участка на 1 (самый ближний к змейке)
            # Удаляем старые координаты

            self.last_cords = self.bodys_cords[-1]
            self.bodys_cords[-1] = last_head_place
            self.bodys_cords.insert(1, self.bodys_cords[-1])
            self.bodys_cords.pop()

            # Отключаем отображение каждого элемента змеи (кроме головы, она отдельно)
            # После этого сразу включаем новый элемент с новыми координатами (кроме головы, она отдельно)
            for i in range(1, len(self.body)):
                self.body[i].destroy()
                self.body[i] = Label(root, background=self.body_color)
                self.body[i].grid(row=self.bodys_cords[i][1], column=self.bodys_cords[i][0], sticky='nsew')

            # Отключение, удаление старой головы, создание новой и её отображение
            self.body[0].destroy()
            self.body.pop(0)
            self.body.insert(0, Label(root, background=self.head_color))
            self.body[0].grid(row=self.bodys_cords[0][1], column=self.bodys_cords[0][0], sticky='nsew')

            # Проверка смерти (если координаты головы=координатам любого участка тела - смерть)
            for i in range(1, len(self.bodys_cords)):
                if self.bodys_cords[i] == tuple(self.bodys_cords[0]):
                    self.death(apple.count)
                    root.destroy()
                    break
            
            # Проверка съеденного яблока. Если да, у змейки увеличивается тело а яблоко пропадает
            # И появляется новое
            if self.bodys_cords[0][0] == apple.x and self.bodys_cords[0][1] == apple.y:
                self.eat_apple()
                apple.eat_apple(self.bodys_cords)
                root.title(f"Online Snake! Apples: {apple.count}")

            # Пауза, чтобы змейка не двигалась очень быстро
            time.sleep(self.speed)

    # Поедание яблока, увеличение тела змейки и сразу его отображение
    def eat_apple(self):
        self.body.append(Label(background=self.body_color))
        self.bodys_cords.append(self.last_cords)
        self.body[-1].grid(row=self.bodys_cords[-1][1], column=self.bodys_cords[-1][0], sticky='nsew')

    # Смерть змейки, отображение результатов и их сохранение
    def death(self, count):
        self.is_moving = False
        record = Save.get_stat('solo', 1)
        if count > int(record.split()[1]):
            showinfo("Game Over", f"Вы погибли!\nНовый рекорд - {count}!")
            Save.save_stat('solo', 1, f'Рекорд: {count}')
        else:
            showinfo("Game Over", f"Вы погибли!\nВаш результат - {count}\n{record}")
        Save.save_stat('solo', 0, f'Последний результат: {count}')

# Класс яблока (В игре используется только один объект)
class Apple:
    def __init__(self, x = random.randint(0, 16), y = random.randint(0, 16), color="#FF0D00", count=0):
        # Координаты яблока
        self.x = x
        self.y = y

        self.count = count # Количество съеденных яблок (или же созданных яблок) - очки
        self.color = color # Цвет яблока (красный по умолчанию)

        self.__apple = None # Здесь хранится Label с отображением яблока
    
    # Отображение яблока
    def create_apple(self):
        self.__apple = Label(background=self.color)
        self.__apple.grid(row=self.y, column=self.x, sticky='nsew')

    # Изменение координат яблока на случайные
    def new_place(self, coords):
        while True:
            self.x = random.randint(0, 16)
            self.y = random.randint(0, 16)
            for coord in coords:
                if (self.x, self.y) == coord:
                    break
            else:
                break
    
    # Действия, что происходят когда змея съедает яблоко (координаты головы змеи=координатам яблока)
    def eat_apple(self, snake_bodys_coords):
        self.__apple.destroy() # Отключаем отрисовку старого яблока
        self.count += 1 # Увеличивааем счёт
        self.new_place(snake_bodys_coords) # Задаём новые координаты яблока
        self.create_apple() # Отображаем новое яблока засчёт новых координат

# Класс игры, в котором происходит весь игровой процесс
class Game:
    # Игра в одиночку
    @staticmethod
    def start_solo_game(root, first_color, second_color):
        root.destroy() # Удаление окна главного меню игры

        root = Tk()

        # Создание игровых объектов
        snake = Snake() # Начальные координаты - низ по центру
        apple = Apple()

        root.geometry('340x340')
        root.resizable(False, False)

        root.title(f"Online Snake! Apples: 0")
        
        # Создание и конфигурация игровго поля

        for c in range(17): root.columnconfigure(c, weight=1)
        for r in range(17): root.rowconfigure(r, weight=1)

        color = first_color

        for r in range(17):
            for c in range(17):
                Label(background=color).grid(row=r, column=c, sticky='nsew')
                if color == first_color:
                    color = second_color # Тёмный
                else:
                    color = first_color # Яркий

        # Отображение яблока
        apple.create_apple()

        # Отображение змейки
        snake.create_snake()

        moving = None # Переменная с потоком
        def move(event):
            # Если была нажата недействительная клавиша, то ничего не происходит
            match event.char.lower():
                case 'w': pass
                case 's': pass
                case 'a': pass
                case 'd': pass
                case _: return
            # Двигаться в противоположную от движения змейки сторону нельзя
            if snake.last_move == 'up' and event.char.lower() == 's':
                return
            elif snake.last_move == 'down' and event.char.lower() == 'w':
                return
            elif snake.last_move == 'right' and event.char.lower() == 'a':
                return
            elif snake.last_move == 'left' and event.char.lower() == 'd':
                return
            snake.ismoving = False # Отключаем движение змеи, чтобы перейти в новую сторону
            nonlocal moving
            try:
                if moving.is_alive(): # Мы уже отключили ismoving, ждём пока поток в moving закончит свою работу
                    root.after(100, lambda: move(event))
                    return
                snake.ismoving = True # После завершения работы потока, нужно создать новый с новым направлением
                moving = Thread(target=snake.move, args=(event, apple, root, ), daemon=True)
                moving.start()
            except: # Изначально moving = None, в первый раз moving.is_alive возбудит исключение
                snake.ismoving = True
                moving = Thread(target=snake.move, args=(event, apple, root, ), daemon=True)
                moving.start()

        root.bind("<Key>", move) # Обработка нажатия клавиш

        # Безопасно завершаем программу, ставя is_moving на False
        def save_end():
            snake.is_moving = False
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", save_end)

        root.mainloop()

    # Игра онлайн
    @staticmethod
    def start_online_game(root): pass

class Save:
    # solo, 0 - последняя игра. 1 - рекорд
    # online, 0 - последняя игра (победитель), 1 - максимальный результат в онлайн игре
    # Получение статистики из файла file по индексу (0 или 1) index
    @staticmethod
    def get_stat(file: str, index: int):
        file = f'stats/{file}.txt'
        with open(f'{file}', encoding='utf-8') as f:
            return f.readlines()[index]

    # Сохранение статистики value в файл file по индексу (0 или 1) index
    @staticmethod
    def save_stat(file:  str, index: int, value: str):
        if index == 1: # Мы перезаписываем файл сохранения, нужно записать не перезаписываемую строку
            first_line = Save.get_stat(file, 0).strip() # Что мы делаем тут
            # А здесь перезаписываем file с новым значением 2й строки и старым 1й строки
            with open(f'stats/{file}.txt', 'w', encoding='utf-8') as f:
                f.write(f'{first_line}\n{value}')
        elif index == 0: # Тут похожая логика как и в первом условии
            second_line = Save.get_stat(file, 1).strip()
            with open(f'stats/{file}.txt', 'w', encoding='utf-8') as f:
                f.write(f'{value}\n{second_line}')

# Отрисовывает элементы главного меню игры
def main_menu():
    try:
        widgets['stats'].destroy()
        widgets['back'].destroy()
    except:
        pass
    create_text()
    create_buttons()

def show_stat():
    # Удаление старых виджетов
    widgets['title'].destroy()
    widgets['extras'].destroy()
    widgets['start_solo'].destroy()
    widgets['start_online'].destroy()
    widgets['stat'].destroy()

    last_solo_game = Save.get_stat('solo', 0) # Количество съеденных яблок в последней игре
    best_solo_game = Save.get_stat('solo', 1) # Самое большое количество съеденных яблок за историю игрока

    # Результаты последней онлайн игры в формате (победитель, съеденные яблоки|проигравший, съеденные яблоки)
    online_game_data = Save.get_stat('online', 0)
    winner_stat = online_game_data.split('|')[0]
    loser_stat = online_game_data.split('|')[1]
    best_online_game = Save.get_stat('online', 1) # Самое большое количество съеденных яблок в выигрышной онлайн игре

    widgets['stats'] = ttk.Label(text=f"{last_solo_game}\n{best_solo_game}\n\nПобедитель прошлой игры: {winner_stat}\nПроигравший: {loser_stat}\nВаш лучший результат: {best_online_game}", justify='left', font=('Arial', 10))
    widgets['stats'].pack(anchor='nw', side='top')

    widgets['back'] = ttk.Button(root, text='Назад', command=main_menu)
    widgets['back'].pack(anchor='sw', side='bottom')

def create_text():
    # Конфигурация текста
    widgets['title'] = ttk.Label(root, text="Онлайн змейка!", font=('Arial', 15))
    widgets['extras'] = ttk.Label(root, text="Создатель - Вадим Гутник, студент группы К0109-23")
    widgets['title'].pack()
    widgets['extras'].pack()

def start_game(mode, root):
    for key in widgets:
        try:
            widgets[key].destroy()
        except: pass
    choose_color = ttk.Label(text="Выберите цвет:", font=('Arial', 15))
    green_color = Button(background="#4DDE00", command=lambda: mode(root, "#4DDE00", "#329000")) # Цвет поля - зелёный
    black_color = Button(background="#161618", command=lambda: mode(root, "#161618", "#83868C")) # Цвет поля - чёрно-белый

    choose_color.pack()
    green_color.pack(side='left', ipadx=10, ipady=10, padx=30)
    black_color.pack(side='right', ipadx=10, ipady=10, padx=[0, 30])

def create_buttons():
    # Конфигурация кнопок
    widgets['start_solo'] = ttk.Button(root, text="Начать игру (одиночный режим)", command=lambda: start_game(Game.start_solo_game, root))
    widgets['start_online'] = ttk.Button(root, text="Начать игру (онлайн режим)", command=lambda: start_game(Game.start_online_game, root))
    widgets['stat'] = ttk.Button(root, text="Статистика", command=show_stat)

    widgets['start_solo'].pack(ipady=10, pady=40)
    widgets['start_online'].pack(ipady=10)
    widgets['stat'].pack(anchor='sw', side='bottom')

if __name__ == "__main__":
    # Конфигурация окна
    root = Tk()
    root.title("Online Snake")

    # Установка размеров и расположения окнаа относительно монитора игрока
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    x = (width-300)//2
    y = (height-300)//2
    root.geometry(f"300x300+{x}+{y}")
    
    root.resizable(False, False)

    # Глобальный словарь со всеми виджетами главного меню
    widgets = {
    'title': None,
    'extras': None,
    'start_solo': None,
    'start_online': None,
    'stat': None,
    'stats': None,
    'back': None
    }

    main_menu() # Отображает элементы главного окна игры

    root.mainloop()