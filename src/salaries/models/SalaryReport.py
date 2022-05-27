import json
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from .Employee import Employee
import json
from json import JSONEncoder
from django.utils.crypto import get_random_string
from django.db.models.signals import pre_save


class DefaultClassEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class BaseJsonSerializable:

    JSON_ENCODER = DefaultClassEncoder

    @classmethod
    def from_dict(cls, dict_o):
        metrica = cls(**dict_o)
        metrica.__dict__.update(dict_o)
        return metrica

    @classmethod
    def from_json(cls, json_str):
        dict_o = json.loads(json_str)
        return cls.from_dict(dict_o)

    def to_json(self):
        return json.dumps(self, cls=self.JSON_ENCODER)

    def to_dict(self):
        return self.__dict__


class Metrica(BaseJsonSerializable):
    def __init__(self, name, value,
                 group=None, description=None, label=None, meta_params={}, class_name=''):
        self.name = name
        self.value = value
        self.group = group
        self.description = description
        self.label = label
        self.meta_params = meta_params
        self.class_name = class_name

    def get_meta_param(self, meta_param_name, default=None):
        return self.meta_params.get(meta_param_name, default)

    def set_class(self, class_name):
        self.class_name = class_name

    def get_class(self):
        return self.class_name

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class MetricsCollection:

    ITEM_MODEL = Metrica

    def __init__(self):
        self._items = []

    def add(self, item):
        if not isinstance(item, self.ITEM_MODEL):
            raise TypeError
        self._items.append(item)

    def extend(self, items):
        for item in items:
            self.add(item)

    def to_list(self):
        return [item.to_dict() for item in self._items]

    def to_json(self):
        return json.dumps(self.to_list())

    def len(self):
        return len(self._items)

    def get_by(self, key, value):
        for item in self._items:
            if getattr(item, key) == value:
                return item
        return None

    @classmethod
    def from_list(cls, list):
        collection = cls()
        for item in list:
            collection.add(cls.ITEM_MODEL.from_dict(item))
        return collection

    @classmethod
    def from_json(cls, json_str):
        list = json.loads(json_str)
        return cls.from_list(list)

    def __iter__(self):
        self.__iterator_counter = 0
        return self

    def __next__(self):
        if self.__iterator_counter == len(self._items):
            raise StopIteration
        res = self._items[self.__iterator_counter]
        self.__iterator_counter += 1
        return res


def get_random_slug():
    return get_random_string(length=8)


class SalaryReport(models.Model):

    NOT_CONFIRMED = 'NOT_CONFIRMED'
    CONFIRMED_FOR_PAYMENT = 'CONFIRMED_FOR_PAYMENT'
    PAID = 'PAID'
    DECLINED = 'DECLINED'

    REPORT_STATUSES = [
        (NOT_CONFIRMED, 'Не подтвержден'),
        (CONFIRMED_FOR_PAYMENT, 'Подтвержден для оплаты'),
        (PAID, 'Оплачен'),
        (DECLINED, 'Отклонен')
    ]

    REPORT_STATUSES_CSS_CLASSES = {
        NOT_CONFIRMED: "secondary",
        CONFIRMED_FOR_PAYMENT: 'warning',
        PAID: 'success',
        DECLINED: 'danger'
    }

    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField('Время создания', null=False, auto_now_add=True)
    date_from = models.DateTimeField('Время начала', null=False)
    date_to = models.DateTimeField("Время окончания", null=False)
    slug_id = models.SlugField(unique=True, blank=False, null=False, max_length=8)
    status = models.CharField('Статус', choices=REPORT_STATUSES,
                              default=NOT_CONFIRMED, max_length=50)
    metrics = models.JSONField('Метрики', blank=True, null=False, default='')

    def get_report_status_css_class(self):
        return self.REPORT_STATUSES_CSS_CLASSES[self.status]

    def __get_metrics_as_collection(self):
        if self.metrics:
            return MetricsCollection.from_json(self.metrics)
        return MetricsCollection()

    def add_metrica(self, metrica):
        if metrica:
            metrics = self.__get_metrics_as_collection()
            metrics.add(metrica)
            self.metrics = metrics.to_json()

    def add_metrics(self, metrics):
        metrics_collection = self.__get_metrics_as_collection()
        metrics_collection.extend(metrics)
        self.metrics = metrics_collection.to_json()

    def get_grouped_metrics(self):
        groups = {}
        metrics_collection = self.__get_metrics_as_collection()
        for metrica in metrics_collection:
            if metrica.group not in groups:
                groups[metrica.group] = []
            groups[metrica.group].append(metrica)
        return groups

    def get_metrics_by_meta_param(self, param_name, param_value):
        res = []
        metrics_collection = self.__get_metrics_as_collection()
        for metrica in metrics_collection:
            if metrica.get_meta_param(param_name) == param_value:
                res.append(metrica)
        return res

    def count_metrics(self):
        return self.__get_metrics_as_collection().len()

    def get_metrica_by(self, key, value):
        metrics = self.__get_metrics_as_collection()
        metrica = metrics.get_by(key, value)
        if metrica:
            return metrica
        return None

    def get_absolute_url(self):
        return reverse("salaries:salary_report_view", kwargs={
            "report_slug": self.slug_id
        })

    def get_total_money(self):
        metrica = self.get_metrica_by('label', 'total_money')
        if metrica:
            return f"{metrica.value:,}"
        return None

    def __str__(self):
        formatted_date = self.created_at.strftime('%d.%m.%Y (%H:%M)')
        return f"{self.id}. {self.employee.name}, {formatted_date}"

    class Meta:
        verbose_name = 'Зарплатный отчет'
        verbose_name_plural = 'Зарплатные отчеты'


@receiver(pre_save, sender=SalaryReport)
def set_random_slug_id(sender, instance, **kwargs):
    if instance.id is None and not instance.slug_id:
        instance.slug_id = get_random_slug()
