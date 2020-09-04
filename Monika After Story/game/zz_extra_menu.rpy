default persistent.mas_window_color = "default"
default persistent.mas_mouse_color = "default"
default persistent.mas_sayori_name_abb = "Сайори"
default persistent.player_abbriviated_name = False

define numbers_three_list = [".99", ".98", ".97", ".96", ".95", ".94", ".93", ".92", ".91", ".90", ".89", ".88", ".87", ".86", ".85", ".84",
    ".83", ".82", ".81", ".80", ".79", ".78", ".76", ".76", ".75", ".74", ".73", ".72", ".71", ".70", ".69", ".68", ".67", ".66",
    ".65", ".64", ".63", ".62", ".61", ".60", ".59", ".58", ".57", ".56", ".55", ".54", ".53", ".52", ".51", ".50", ".49", ".48",
    ".47", ".46", ".45", ".44", ".43", ".42", ".41", ".40", ".39", ".38", ".37", ".36", ".35", ".34", ".33", ".32", ".31", ".30",
    ".29", ".28", ".27", ".26", ".25", ".24", ".23", ".22", ".21", ".20", ".19", ".18", ".17", ".16", ".15", ".14", ".13", ".12",
    ".11", ".10", ".09", ".08", ".07", ".06", ".05", ".04", ".03", ".02", ".01", ".00"]

define numbers_two_list = [".0", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9"]

transform up_poem_anim(yal=0.0):
    yoffset -300
    alpha 0.0
    easein 1.0 yoffset yal alpha 1.0
    on idle:
        zoom 1.0
    on hide:
        yoffset yal
        alpha 1.0
        easein 1.0 yoffset -250 alpha 0.0

define natsuki_name_list = ["natsuki", "нацуки", "натсуки", "натцуки"]
define yuri_name_list = ["yuri", "юри", "юрец"]
define sayori_name_list = ["sayori", "саёри", "сайори", "саери"]
define monika_name_list = ["monika", "моника", "moni", "мони", "моня", "монька", "монечка", "моничка"]

init -3 python:

    layout.MAS_SAYORI_NAME_ABB = (
        "Запускает меню выбора имени Сайори/Саери."
    )

    layout.MAS_NAME_ABB = (
        "Запускает меню активации улучшенного произношения имени."
    )

# TODO: Добавить индикатор привязанности

# Screen with name choice for Sayori
screen sayori_name_choice():
    modal True

    key "noshift_Э" action Return
    key "noshift_э" action Return
    key "noshift_'" action Return
    key "noshift_e" action Return
    key "noshift_E" action Return

    zorder 190

    style_prefix "extra_menu"

    frame:
        style ("extra_menu_outer_frame" if not mas_globals.dark_mode else "extra_menu_outer_frame_dark")

        hbox:

            frame:
                style "extra_menu_navigation_frame"

            frame:
                style "extra_menu_content_frame"

                transclude

        vbox:
            style_prefix "extra_menu"

            xpos gui.navigation_xpos
            spacing gui.navigation_spacing

            textbutton _("Сайори"):
                action SetField(persistent, "mas_sayori_name_abb", "Сайори")
            textbutton _("Саёри"):
                action SetField(persistent, "mas_sayori_name_abb", "Саёри")

    vbox:

        yalign 1.0

        textbutton _("Вернуться"):
            style "extra_menu_return_button"
            action Function(mas_extra_menu.sayori_name_choice_return)
    label "{size=-12}Произношение имени\n(Сейчас: [persistent.mas_sayori_name_abb]){/size}"

screen names_say_choice():
    modal True

    zorder 190

    style_prefix "extra_menu"

    frame:
        style ("extra_menu_outer_frame" if not mas_globals.dark_mode else "extra_menu_outer_frame_dark")

        hbox:

            frame:
                style "extra_menu_navigation_frame"

            frame:
                style "extra_menu_content_frame"

                transclude

        vbox:
            style_prefix "extra_menu"

            xpos gui.navigation_xpos
            spacing gui.navigation_spacing

            textbutton _("Обычный"):
                action SetField(persistent, "player_abbreviated_name", False)
            textbutton _("Улучшенный"):
                action SetField(persistent, "player_abbreviated_name", True)
    vbox:

        yalign 1.0

        textbutton _("Вернуться"):
            style "extra_menu_return_button"
            action Function(mas_extra_menu.names_say_choice_return)


    if persistent.player_abbreviated_name:
        label "{size=-12}Стиль произношения имён\n(Сейчас: улучшенный){/size}"
    else:
        label "{size=-12}Стиль произношения имён\n(Сейчас: обычный){/size}"
