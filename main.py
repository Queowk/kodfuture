# weather_diary.py

import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import List, Optional

class WeatherEntry:
    """Модель данных о погоде"""
   
    def __init__(self, date: datetime, temperature: float, description: str, precipitation: float):
        self.date = date
        self.temperature = temperature
        self.description = description
        self.precipitation = precipitation
   
    def to_dict(self) -> dict:
        """Конвертация в словарь для JSON"""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'temperature': self.temperature,
            'description': self.description,
            'precipitation': self.precipitation
        }
   
    @classmethod
    def from_dict(cls, data: dict):
        """Создание объекта из словаря"""
        return cls(
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            temperature=data['temperature'],
            description=data['description'],
            precipitation=data['precipitation']
        )
   
    def __str__(self) -> str:
        return (f"📅 {self.date.strftime('%Y-%m-%d')} | 🌡️ {self.temperature}°C | "
                f"{self.description} | 💧 {self.precipitation} мм")

class WeatherType(ABC):
    """Абстрактный класс для различных типов погоды"""
   
    @abstractmethod
    def get_advice(self) -> str:
        pass

class SunnyWeather(WeatherType):
    def get_advice(self) -> str:
        return "☀️ Не забудьте солнцезащитный крем и головной убор!"

class RainyWeather(WeatherType):
    def get_advice(self) -> str:
        return "☔ Возьмите зонт и оденьтесь теплее!"

class SnowyWeather(WeatherType):
    def get_advice(self) -> str:
        return "❄️ Осторожно на дорогах! Одевайтесь очень тепло."

class WindyWeather(WeatherType):
    def get_advice(self) -> str:
        return "💨 Сильный ветер! Закрепите вещи на балконе."

class WeatherDiary:
    """Основной класс дневника погоды"""
   
    def __init__(self, filename: str = 'weather_data.json'):
        self.filename = filename
        self.entries: List[WeatherEntry] = []
        self.load_data()
   
    def add_entry(self, date_str: str, temperature: float, description: str, precipitation: float) -> bool:
        """Добавление новой записи"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
           
            # Проверка на существующую запись за эту дату
            if self.get_entry_by_date(date):
                print("❌ Запись за эту дату уже существует!")
                return False
           
            entry = WeatherEntry(date, temperature, description, precipitation)
            self.entries.append(entry)
            self.save_data()
            print("✅ Запись успешно добавлена!")
           
            # Показываем совет на основе погоды
            weather_type = self._get_weather_type(description, precipitation)
            if weather_type:
                print(f"💡 Совет: {weather_type.get_advice()}")
           
            return True
        except ValueError:
            print("❌ Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return False
   
    def _get_weather_type(self, description: str, precipitation: float) -> Optional[WeatherType]:
        """Определение типа погоды для советов"""
        desc_lower = description.lower()
        if precipitation > 5 or 'дождь' in desc_lower:
            return RainyWeather()
        elif precipitation > 0:
            return SnowyWeather() if 'снег' in desc_lower else RainyWeather()
        elif 'солн' in desc_lower or 'ясно' in desc_lower:
            return SunnyWeather()
        elif 'ветр' in desc_lower:
            return WindyWeather()
        return None
   
    def get_entry_by_date(self, date: datetime) -> Optional[WeatherEntry]:
        """Получение записи по дате"""
        for entry in self.entries:
            if entry.date.date() == date.date():
                return entry
        return None
   
    def view_entries(self, filtered_entries: List[WeatherEntry] = None) -> None:
        """Просмотр всех или отфильтрованных записей"""
        entries_to_show = filtered_entries if filtered_entries else self.entries
       
        if not entries_to_show:
            print("📭 Нет записей для отображения")
            return
       
        print("\n" + "="*60)
        print("📊 ДНЕВНИК ПОГОДЫ")
        print("="*60)
        for entry in sorted(entries_to_show, key=lambda x: x.date):
            print(entry)
        print("="*60 + "\n")
   
    def delete_entry(self, date_str: str) -> bool:
        """Удаление записи по дате"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            entry = self.get_entry_by_date(date)
           
            if entry:
                self.entries.remove(entry)
                self.save_data()
                print("✅ Запись успешно удалена!")
                return True
            else:
                print("❌ Запись за указанную дату не найдена")
                return False
        except ValueError:
            print("❌ Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return False
   
    def filter_by_date_range(self, start_date_str: str, end_date_str: str) -> List[WeatherEntry]:
        """Фильтрация записей по диапазону дат"""
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
           
            filtered = [
                entry for entry in self.entries
                if start_date <= entry.date <= end_date
            ]
           
            if not filtered:
                print("❌ Нет записей в указанном диапазоне дат")
           
            return filtered
        except ValueError:
            print("❌ Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return []
   
    def filter_by_temperature(self, min_temp: float, max_temp: float) -> List[WeatherEntry]:
        """Фильтрация записей по температуре"""
        filtered = [
            entry for entry in self.entries
            if min_temp <= entry.temperature <= max_temp
        ]
       
        if not filtered:
            print(f"❌ Нет записей с температурой в диапазоне {min_temp}-{max_temp}°C")
       
        return filtered
   
    def plot_temperature_graph(self, entries: List[WeatherEntry] = None) -> None:
        """Построение графика температуры"""
        plot_entries = entries if entries else self.entries
       
        if len(plot_entries) < 2:
            print("❌ Недостаточно данных для построения графика (нужно минимум 2 записи)")
            return
       
        # Сортировка по дате
        sorted_entries = sorted(plot_entries, key=lambda x: x.date)
       
        dates = [entry.date.strftime('%Y-%m-%d') for entry in sorted_entries]
        temperatures = [entry.temperature for entry in sorted_entries]
        precipitations = [entry.precipitation for entry in sorted_entries]
       
        # Создание графика
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
       
        # График температуры
        ax1.plot(dates, temperatures, marker='o', linewidth=2, markersize=8, color='red')
        ax1.set_title('График температуры', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Температура (°C)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
       
        # Добавление значений на график
        for i, temp in enumerate(temperatures):
            ax1.annotate(f'{temp}°C', (dates[i], temp),
                        textcoords="offset points", xytext=(0,10), ha='center')
       
        # График осадков
        ax2.bar(dates, precipitations, color='blue', alpha=0.6)
        ax2.set_title('Количество осадков', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Дата')
        ax2.set_ylabel('Осадки (мм)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
       
        plt.tight_layout()
        plt.show()
   
    def save_data(self) -> None:
        """Сохранение данных в JSON файл"""
        data = [entry.to_dict() for entry in self.entries]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
   
    def load_data(self) -> None:
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [WeatherEntry.from_dict(item) for item in data]
                print(f"📂 Загружено {len(self.entries)} записей из {self.filename}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️ Ошибка загрузки файла: {e}")
                self.entries = []
   
    def get_statistics(self) -> None:
        """Показ статистики"""
        if not self.entries:
            print("📭 Нет данных для статистики")
            return
       
        temps = [entry.temperature for entry in self.entries]
        precip = [entry.precipitation for entry in self.entries]
       
        print("\n" + "="*50)
        print("📈 СТАТИСТИКА ПОГОДЫ")
        print("="*50)
        print(f"📊 Всего записей: {len(self.entries)}")
        print(f"🌡️ Средняя температура: {sum(temps)/len(temps):.1f}°C")
        print(f"🔥 Максимальная температура: {max(temps)}°C")
        print(f"❄️ Минимальная температура: {min(temps)}°C")
        print(f"💧 Среднее количество осадков: {sum(precip)/len(precip):.1f} мм")
        print("="*50 + "\n")

def main():
    """Главная функция приложения"""
    diary = WeatherDiary()
   
    while True:
        print("\n" + "="*50)
        print("🌤️  WEATHER DIARY - Дневник погоды")
        print("="*50)
        print("1. ➕ Добавить запись")
        print("2. 📋 Просмотреть все записи")
        print("3. 🗑️ Удалить запись")
        print("4. 🔍 Фильтрация по дате")
        print("5. 🔍 Фильтрация по температуре")
        print("6. 📈 Построить график температуры")
        print("7. 📊 Показать статистику")
        print("8. 💾 Сохранить данные")
        print("9. 📂 Загрузить данные")
        print("0. 🚪 Выход")
        print("="*50)
       
        choice = input("Выберите действие (0-9): ").strip()
       
        if choice == '1':
            print("\n--- Добавление новой записи ---")
            try:
                date = input("Дата (ГГГГ-ММ-ДД): ").strip()
                temp = float(input("Температура (°C): ").strip())
                desc = input("Описание (солнечно, дождь, снег, облачно и т.д.): ").strip()
                precip = float(input("Осадки (мм): ").strip())
               
                if precip < 0:
                    print("❌ Осадки не могут быть отрицательными!")
                else:
                    diary.add_entry(date, temp, desc, precip)
            except ValueError:
                print("❌ Ошибка: Неверный формат температуры или осадков!")
       
        elif choice == '2':
            diary.view_entries()
       
        elif choice == '3':
            print("\n--- Удаление записи ---")
            date = input("Дата записи для удаления (ГГГГ-ММ-ДД): ").strip()
            diary.delete_entry(date)
       
        elif choice == '4':
            print("\n--- Фильтрация по диапазону дат ---")
            start = input("Начальная дата (ГГГГ-ММ-ДД): ").strip()
            end = input("Конечная дата (ГГГГ-ММ-ДД): ").strip()
            filtered = diary.filter_by_date_range(start, end)
            if filtered:
                diary.view_entries(filtered)
                if input("\nПостроить график для отфильтрованных данных? (y/n): ").lower() == 'y':
                    diary.plot_temperature_graph(filtered)
       
        elif choice == '5':
            print("\n--- Фильтрация по температуре ---")
            try:
                min_temp = float(input("Минимальная температура (°C): ").strip())
                max_temp = float(input("Максимальная температура (°C): ").strip())
                filtered = diary.filter_by_temperature(min_temp, max_temp)
                if filtered:
                    diary.view_entries(filtered)
                    if input("\nПостроить график для отфильтрованных данных? (y/n): ").lower() == 'y':
                        diary.plot_temperature_graph(filtered)
            except ValueError:
                print("❌ Ошибка: Неверный формат температуры!")
       
        elif choice == '6':
            diary.plot_temperature_graph()
       
        elif choice == '7':
            diary.get_statistics()
       
        elif choice == '8':
            diary.save_data()
            print("✅ Данные сохранены!")
       
        elif choice == '9':
            diary.load_data()
       
        elif choice == '0':
            print("👋 До свидания!")
            break
       
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
