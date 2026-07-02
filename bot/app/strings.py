from dataclasses import dataclass


@dataclass
class Language:
    QUERY_NOT_FOUND: str
    QUERY_FOUND: str
    START_GREETINGS: str
    TOO_LONG_QUERY: str
    KB_ADD_TO_WISHLIST: str
    KB_REMOVE_FROM_WISHLIST: str
    KB_ADD_TO_COLLECTION: str
    KB_REMOVE_FROM_COLLECTION: str
    THIS_IS_WISHLIST: str
    WISHLIST_IS_EMPTY: str
    THIS_IS_COLLECTION: str
    COLLECTION_IS_EMPTY: str
    CACHE_CLEARED: str
    BACKUP_IN_PROGRESS: str
    BACKUP_FAILED: str
    RESTORE_SEND_FILE: str
    RESTORE_INVALID_FILE: str
    RESTORE_FILE_TOO_LARGE: str
    RESTORE_CONFIRM: str
    RESTORE_IN_PROGRESS: str
    RESTORE_SUCCESS: str
    RESTORE_FAILED: str
    RESTORE_CANCELLED: str
    RESTORE_WAITING_HINT: str
    RESTORE_CONFIRM_HINT: str
    KB_CANCEL: str
    KB_CONFIRM_RESTORE: str


CHOOSE_LANGUAGE = "Choose your language\nPasirinkite kalbą\nВыберите язык"

multilanguage = {
    "ru": Language(
        QUERY_NOT_FOUND="По вашему запросу ничего не найдено, попробуйте изменить запрос.",
        QUERY_FOUND="Federico Mahora - <b>{number}</b> очень напоминает:\nБренд: <b>{brand}</b>\nНазвание: <b>{name}</b>\n{description}\n{url}",
        START_GREETINGS="""

Привет, я бот, который поможет тебе понять каким ароматом был вдохновлен аромат Federico Mahora.
Напиши номер аромата и я пришлю тебе информацию о нем.
Например: 972

Вообще ты можешь задавать разные вопросы. Например:

Dior - покажет тебе все ароматы так или иначе связанные с этим брендом
для мужчин - покажет все ароматы для мужчин
для женщин - все ароматы для женщин
Tom Ford для женщин и мужчин - покажет все как женские так и мужские ароматы связанные с Tom Ford

Любой из этих запросов выдаст тебе список ароматов, с их номерами.

Если ты хочешь подробнее узнать о каком-то аромате, напиши мне его номер
""",
        TOO_LONG_QUERY="Слишком длинный запрос, попробуйте снова.\nНапример: Armani для женщин",
        KB_ADD_TO_WISHLIST="Добавить в желаемые",
        KB_REMOVE_FROM_WISHLIST="Удалить из желаемых",
        KB_ADD_TO_COLLECTION="Добавить в коллекцию",
        KB_REMOVE_FROM_COLLECTION="Удалить из коллекции",
        THIS_IS_WISHLIST="Мой список желаемых",
        WISHLIST_IS_EMPTY="Мой список желаемых пуст. Вы можете добавить ароматы в список.",
        THIS_IS_COLLECTION="Есть в моей коллекции",
        COLLECTION_IS_EMPTY="Моя коллекция пуста. Вы можете добавить ароматы в коллекцию.",
        CACHE_CLEARED="Кэш очищен",
        BACKUP_IN_PROGRESS="Создаю бэкап…",
        BACKUP_FAILED="Не удалось создать бэкап:\n<code>{error}</code>",
        RESTORE_SEND_FILE=(
            "Пришлите <b>.sql</b> файл бэкапа.\n"
            "⚠️ Существующие данные будут перезаписаны."
        ),
        RESTORE_INVALID_FILE="Ожидается файл с расширением <b>.sql</b>.",
        RESTORE_FILE_TOO_LARGE=(
            "Файл больше 20 МБ — стандартный Telegram Bot API не даст его скачать."
        ),
        RESTORE_CONFIRM=(
            "Файл получен: <b>{name}</b> ({size_kb} КБ).\n"
            "Перезаписать базу?"
        ),
        RESTORE_IN_PROGRESS="Восстанавливаю базу…",
        RESTORE_SUCCESS="База восстановлена.",
        RESTORE_FAILED="Не удалось восстановить базу:\n<code>{error}</code>",
        RESTORE_CANCELLED="Отменено.",
        RESTORE_WAITING_HINT=(
            "Пришлите <b>.sql</b> файл или нажмите «Отмена»."
        ),
        RESTORE_CONFIRM_HINT=(
            "Нажмите «Да, перезаписать» или «Отмена»."
        ),
        KB_CANCEL="Отмена",
        KB_CONFIRM_RESTORE="Да, перезаписать",
    ),
    "en": Language(
        QUERY_NOT_FOUND="Nothing was found, try changing your query.",
        QUERY_FOUND="Federico Mahora - <b>{number}</b> reminds me of:\nBrand: <b>{brand}</b>\nName: <b>{name}</b>\n{description}\n{url}",
        START_GREETINGS="""
Hi, I'm a bot that will help you figure out which fragrance was inspired by the Federico Mahora fragrance.

Write Federico Mahora fragrance number and I will send you information about it.
For example: 972

Actually you can ask different questions. For example:

Dior - will show you all the fragrances related to this brand in one way or another.
For men - it will show you all fragrances for men.
For women, all fragrances for women.
Tom Ford for women and men - will show you all both women's and men's fragrances related to Tom Ford.

Any of these queries will give you a list of fragrances, with their numbers.

If you want to know more about a particular fragrance, text me the fragrance number.
""",
        TOO_LONG_QUERY="Too long query, try again.\nFor example: Armani for women",
        KB_ADD_TO_WISHLIST="Add to wishlist",
        KB_REMOVE_FROM_WISHLIST="Remove from wishlist",
        KB_ADD_TO_COLLECTION="Add to collection",
        KB_REMOVE_FROM_COLLECTION="Remove from collection",
        THIS_IS_WISHLIST="My wishlist",
        WISHLIST_IS_EMPTY="My wishlist is empty. You can add fragrances to wishlist.",
        THIS_IS_COLLECTION="My collection",
        COLLECTION_IS_EMPTY="My collection is empty. You can add fragrances to collection.",
        CACHE_CLEARED="Cache cleared",
        BACKUP_IN_PROGRESS="Creating backup…",
        BACKUP_FAILED="Backup failed:\n<code>{error}</code>",
        RESTORE_SEND_FILE=(
            "Send the <b>.sql</b> backup file.\n"
            "⚠️ Existing data will be overwritten."
        ),
        RESTORE_INVALID_FILE="Expected a file with <b>.sql</b> extension.",
        RESTORE_FILE_TOO_LARGE=(
            "File is larger than 20 MB — the standard Telegram Bot API "
            "will refuse to download it."
        ),
        RESTORE_CONFIRM=(
            "File received: <b>{name}</b> ({size_kb} KB).\n"
            "Overwrite the database?"
        ),
        RESTORE_IN_PROGRESS="Restoring the database…",
        RESTORE_SUCCESS="Database restored.",
        RESTORE_FAILED="Restore failed:\n<code>{error}</code>",
        RESTORE_CANCELLED="Cancelled.",
        RESTORE_WAITING_HINT=(
            "Send the <b>.sql</b> file or press “Cancel”."
        ),
        RESTORE_CONFIRM_HINT=(
            "Press “Yes, overwrite” or “Cancel”."
        ),
        KB_CANCEL="Cancel",
        KB_CONFIRM_RESTORE="Yes, overwrite",
    ),
    "lt": Language(
        QUERY_NOT_FOUND="Nerasta, bandykite pakeisti užklausą.",
        QUERY_FOUND="Federico Mahora - <b>{number}</b> remekam:\nBrand: <b>{brand}</b>\nName: <b>{name}</b>\n{description}\n{url}",
        START_GREETINGS="""
Sveiki, esu botas, kuris padės jums suprasti, kuriuos kvepalus įkvėpė Federico Mahora kvepalai.

Parašykite Federico Mahora kvepalų numerį ir aš atsiųsiu jums informaciją apie jį.
Pavyzdžiui: 972

Apskritai galite užduoti įvairių klausimų. Pavyzdžiui:

Dior - parodysiu visus vienaip ar kitaip su šiuo prekės ženklu susijusius kvepalus.
Vyrams - parodys visus vyrams skirtus kvepalus.
Moterims - visus moterims skirtus kvepalus.
Tom Ford moterims ir vyrams - parodys visus tiek moteriškus, tiek vyriškus kvepalus, susijusius su Tom Ford.

Bet kuri iš šių užklausų pateiks kvepalų sąrašą su jų numeriais.
Jei norite sužinoti daugiau apie konkretų kvepalą, parašykite man kvepalų numerį.
""",
        TOO_LONG_QUERY="Per ilga užklausa, bandykite dar kartą.\nPavyzdžiui: Armani moterims",
        KB_ADD_TO_WISHLIST="Įdėti į norimus",
        KB_REMOVE_FROM_WISHLIST="Pašalinti iš norimų",
        KB_ADD_TO_COLLECTION="Įdėti į kolekciją",
        KB_REMOVE_FROM_COLLECTION="Pašalinti iš kolekcijos",
        THIS_IS_WISHLIST="Aš noriu",
        WISHLIST_IS_EMPTY="Mano pageidavimų sąrašas tuščias. Galite pridėti kvapus į pageidavimų sąrašą.",
        THIS_IS_COLLECTION="Mano kolekcija",
        COLLECTION_IS_EMPTY="Mano kolekcija tuščias. Galite pridėti kvapus į kolekciją.",
        CACHE_CLEARED="įrašomas pašalintas",
        BACKUP_IN_PROGRESS="Kuriama atsarginė kopija…",
        BACKUP_FAILED="Nepavyko sukurti atsarginės kopijos:\n<code>{error}</code>",
        RESTORE_SEND_FILE=(
            "Atsiųskite <b>.sql</b> atsarginės kopijos failą.\n"
            "⚠️ Esami duomenys bus perrašyti."
        ),
        RESTORE_INVALID_FILE="Tikimasi failo su plėtiniu <b>.sql</b>.",
        RESTORE_FILE_TOO_LARGE=(
            "Failas didesnis nei 20 MB — standartinis Telegram Bot API "
            "jo nesisiųs."
        ),
        RESTORE_CONFIRM=(
            "Failas gautas: <b>{name}</b> ({size_kb} KB).\n"
            "Perrašyti duomenų bazę?"
        ),
        RESTORE_IN_PROGRESS="Atkuriama duomenų bazė…",
        RESTORE_SUCCESS="Duomenų bazė atkurta.",
        RESTORE_FAILED="Nepavyko atkurti duomenų bazės:\n<code>{error}</code>",
        RESTORE_CANCELLED="Atšaukta.",
        RESTORE_WAITING_HINT=(
            "Atsiųskite <b>.sql</b> failą arba spauskite „Atšaukti“."
        ),
        RESTORE_CONFIRM_HINT=(
            "Spauskite „Taip, perrašyti“ arba „Atšaukti“."
        ),
        KB_CANCEL="Atšaukti",
        KB_CONFIRM_RESTORE="Taip, perrašyti",
    ),
}
