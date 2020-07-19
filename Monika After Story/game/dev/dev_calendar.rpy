## calendar testing

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_calendar_testing",
            category=["dev"],
            prompt="Тестирование календаря",
            pool=True,
            unlocked=True
        )
    )

label dev_calendar_testing:
    $ import store.mas_calendar as mas_cal
    menu:
        m "Что бы ты хотел[mas_gender_none] сделать?"
        "Посмотреть календарь":
            call mas_start_calendar_read_only

        "Выбрать дату":
            call mas_start_calendar_select_date

            $ sel_date = _return

            if not sel_date:
                m 1tfp "Ты не выбрал[mas_gender_none] дату!"

            else:
                $ sel_date_formal = sel_date.strftime("%B %d, %Y")
                m "Ты выбрал[mas_gender_none] [sel_date_formal]."

    return
                    



