class TopicsMask:
    def __init__(self):
        self.mask = 0
        self.total_topics = 36

    def set_topic(self, topic_index, value):
        """Устанавливает флаг для конкретной темы"""
        if 1 <= topic_index <= self.total_topics:
            if value:
                self.mask |= (1 << (topic_index - 1))  # Устанавливаем бит
            else:
                self.mask &= ~(1 << (topic_index - 1))  # Сбрасываем бит

    def get_topic(self, topic_index):
        """Получает значение флага для конкретной темы"""
        if 1 <= topic_index <= self.total_topics:
            return bool(self.mask & (1 << (topic_index - 1)))
        return False

    def get_all_topics(self):
        """Возвращает список всех выбранных тем"""
        selected = []
        for i in range(1, self.total_topics + 1):
            if self.get_topic(i):
                selected.append(i)
        return selected

    def set_from_list(self, topics_list):
        """Устанавливает флаги из списка выбранных тем"""
        self.mask = 0
        for topic_index in topics_list:
            self.set_topic(topic_index, True)

    def to_int(self):
        """Возвращает integer представление маски"""
        return self.mask

    def from_int(self, mask_int):
        """Восстанавливает маску из integer"""
        self.mask = mask_int
        return self