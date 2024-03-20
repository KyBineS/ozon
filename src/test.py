from faker import Faker

f = Faker('ru_RU')

surname, name, _ = f.name().split(' ')
print(name, surname)