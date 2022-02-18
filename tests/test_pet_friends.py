from api import PetFriends
from settings import valid_email, valid_password, invalid_email
import os
import re

pf = PetFriends()

allowed_small = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z']
ALLOWED_BIG = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
               'V', 'W', 'X', 'Y', 'Z']
allowed_rus_small = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
                     'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ' 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
ALLOWED_RUS_BIG = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
                   'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Frank', animal_type='двортерьер',
                                     age='восемь', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

# Positive tests x2
#1
def test_add_new_pet_with_valid_data_but_absent_photo(name='Faruk', animal_type='песокот',age='8'):
    """Проверяем что можно добавить питомца с корректными данными, но без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_pic(auth_key, name, animal_type, age )

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    try:
        assert result['pet_photo'] == pet_photo
    except NameError as Exception:
        print('Фото отсутствует')
#2
def test_add_photo_of_pet(pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить фото питомца в созданного питомца без фото"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #если последний добавленный мною питомец не имеет фото
    if pet_photo in my_pets['pets'][0]['id']:
        # Добавляем нового питомца без фото
        _, my_pets = pf.add_new_pet_without_pic(auth_key,'собака', 'новая', '9')
        # Запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берем последнего добавленного питомца и меняем его фото
    status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)
    # Проверяем что статус ответа = 200 и есть фото питомца
    assert status == 200
    assert result['pet_photo'] != ''


# Negative tests x8
#1
def test_add_new_pet_with_too_big_age(name='Нурсултан', animal_type='двортерьер',
                                     age='30', pet_photo='images/cat1.jpg'):
    """Проверяем поведение системы при введении слишком большого значения возраста питомца"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    if int(age) <= 25:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("Питомцы столько не живут")
#2
def test_not_giving_api_key_for_invalid_user   (email=invalid_email, password=valid_password):
    """ Проверяем что запрос api ключа с некорректными данными невозможен"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями
    if 'key' in result:
        assert 'key' in result
    else:
        raise Exception ('Отсутсвие доступа к матиралам страницы.Пользователь не был найден в базе данных')

#3
def test_add_new_pet_with_missing_name (name='', animal_type='двортерьер',
                                     age='30', pet_photo='images/cat1.jpg'):
    """Проверяем поведение системы при введении пустого значения имени питомца"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    if len(name) != 0:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("Имя питомца не может быть пустым")

#4
def test_add_new_pet_with_invalid_age_data_type(name='Стив', animal_type='котопес',
                                     age='восемь', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с некорректным типом данных"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    if type(age) == int:
        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("Возраст выражен не цифровым значением")

#5

def test_updating_pet_info_with_unacceptable_symbols(name='$0Б@kа', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце с недопустимыми символами в имени"""

    allowed = allowed_small + allowed_rus_small + ALLOWED_BIG + ALLOWED_RUS_BIG
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    for i in name:
        if i in allowed:
            # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
            if len(my_pets['pets']) > 0:
                status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

                # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
                assert status == 200
                assert result['name'] == name
            else:
                # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
                raise Exception("There is no my pets")
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("Недопустимы значения в имени")

#6
def test_impossible_to_add_new_pet_with_negative_age_number(name='Стив', animal_type='котопес',
                                     age='-12', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с отрицательным значением в возрасте"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    if int(age) > 0:
        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("Возраст выражен отрицательным числом")

#7
def test_unsuccessful_delete_pet_with_invalid_id():
    """Проверяем возможность удаления питомца с неверным ID"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id заведомо несуществующего индекса питомца и отправляем запрос на удаление
    pet_id = "212baddd-2944-43c4-b257-3d1e3a5539ca"
    if pet_id in my_pets.values():
        status, _ = pf.delete_pet(auth_key, pet_id)
        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id in my_pets.values()
    else:
        raise Exception('ID не существует')

#8
def test_adding_pet_with_unacceptable_symbols_in_animal_type(name='Набоков', animal_type='$aLvaD0r^', age='5', pet_photo='images/cat1.jpg'):
    """Проверяем возможность обновления информации о питомце с недопустимыми символами в типе животного"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    allowed = allowed_small + allowed_rus_small + ALLOWED_BIG + ALLOWED_RUS_BIG
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    for i in animal_type:
        if i in allowed:

                status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
                # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
                assert status == 200
                assert result['animal_type'] == animal_type

        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("Недопустимы значения в типе животного")




