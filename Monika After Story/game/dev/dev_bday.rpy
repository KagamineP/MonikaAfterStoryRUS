# test bday art

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_bday_visuals",
            category=["dev"],
            prompt="Визуальные эффекты дня рождения",
            pool=True,
            unlocked=True
        )
    )

label dev_bday_visuals:
    m 1eua "Привет, сейчас я проверю визуальные эффекты дня рождения."

    m "Начнем с баннера."
    show mas_bday_banners zorder 7

    m "Теперь воздушные шары."
    show mas_bday_balloons zorder 8

    m "Теперь торт."
    show mas_bday_cake zorder 11

    m "Теперь торт со свечами."
    $ mas_bday_cake_lit = True

    m "Как это выглядит?"

    m "Хорошо, теперь пора это убрать."
    hide mas_bday_banners
    hide mas_bday_balloons
    hide mas_bday_cake
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_bday_visual_files",
            category=["dev"],
            prompt="BDAY VISUALS (Files)",
            pool=True,
            unlocked=True
        )
    )

label dev_bday_visual_files:
    m 1eua "Okay, lets try looking for the files we need"
    $ store.mas_dockstat.surpriseBdayShowVisuals()

    m "candle light?"
    $ mas_bday_cake_lit = True

    m "off"
    $ mas_bday_cake_lit = False

    m "remove visuals"
    $ store.mas_dockstat.surpriseBdayHideVisuals()
    m "done"
    return
