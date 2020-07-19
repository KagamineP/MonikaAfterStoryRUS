init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_check_window",
            prompt="Тестирование проверки реакции на окно",
            category=['dev'],
            random=False,
            pool=True,
            unlocked=True
        )
    )

label monika_check_window:
    m 1hub "Ладно, [player]!"
    m 2dsc "Давай посмотрим...твое активное окно это.{w=0.5}.{w=0.5}."

    pause 2.0

    if mas_isFocused():
        m 1hub "Я, ура!"
    else:
        $ active_wind = mas_getActiveWindow(True)
        if active_wind:
            m 3eua "[active_wind]."
        else:
            m 1hksdlb "[player], у тебя нет активных окон!"
    return