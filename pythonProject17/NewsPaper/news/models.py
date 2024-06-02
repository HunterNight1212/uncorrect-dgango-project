from django.db import models
from datetime import datetime, timezone


class Products(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    composition = models.TextField(default='состав не указан')

    products = models.ManyToManyField('Orders', through='ProductsOrders')


class Orders(models.Model):
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True)
    cost = models.FloatField(default=0.0)
    pickup = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)

    products = models.ManyToManyField(Products, through='ProductsOrders')

    def start_order(self):
        self.time_in = datetime.now()
        self.save()

    def finish_order(self):
        self.time_out = datetime.now()
        self.complete = True
        self.save()

    def get_duration(self):
        if self.complete:
            return (self.time_out - self.time_in).total_seconds() // 60
        else:
            return (datetime.now(timezone.utc) - self.time_in).total_seconds() // 60


director = 'DI'
admin = 'AD'
cook = 'CO'
cashier = 'CA'
cleaner = 'CL'

POSITIONS = [
    (director, 'директор'),
    (admin, 'адмнистратор'),
    (cashier, 'кассир'),
    (cleaner, 'уборщик')
]


class Staff(models.Model):
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=2, choices=POSITIONS, default=cashier)
    labor_contract = models.IntegerField()

    def last_name(self):
        return str(self.full_name).split()[0]


class ProductsOrders(models.Model):
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    _amount = models.IntegerField(default=1, db_column='amount')

    def sum(self):
        product_price = self.product_id.price
        return product_price * self._amount

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = int(value) if value >= 0 else 0
        self.save()