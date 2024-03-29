#NOTE: This ONLY works for Windows atm

#Whether Monika can use notifications or not
default persistent._mas_enable_notifications = False

#Whether notification sounds are enabled or not
default persistent._mas_notification_sounds = True

#Whether Monika can see your active window or not
default persistent._mas_windowreacts_windowreacts_enabled = False

#Persistent windowreacts db
default persistent._mas_windowreacts_database = dict()

#A global list of events we DO NOT want to unlock on a new session
default persistent._mas_windowreacts_no_unlock_list = list()

#A dict of locations where notifs are used, and if they're enabled for said location
default persistent._mas_windowreacts_notif_filters = dict()

init -10 python in mas_windowreacts:
    #We need this in case we cannot get access to the libs, so everything can still run
    can_show_notifs = True

    #If we don't have access to the required libs to do windowreact related things
    can_do_windowreacts = True

    #The windowreacts db
    windowreact_db = {}

    #Group list, to populate the menu screen
    #NOTE: We do this so that we don't have to try to get a notification
    #In order for it to show up in the menu and in the dict
    _groups_list = [
        "Topic Alerts",
        "Window Reactions",
    ]

init python:
    import os
    #The initial setup

    #We can only do this on windows
    if renpy.windows:
        #We need to extend the sys path to see our packages
        import sys
        sys.path.append(renpy.config.gamedir + '\\python-packages\\')

        #We try/catch/except to make sure the game can run if load fails here
        try:
            #Going to import win32gui for use in destroying notifs
            import win32gui
            #Import win32api so we know if we can or cannot use notifs
            import win32api

        except ImportError:
            #If we fail to import, then we're going to have to make sure nothing can run.
            store.mas_windowreacts.can_show_notifs = False
            store.mas_windowreacts.can_do_windowreacts = False

            #Log this
            store.mas_utils.writelog(
                "[ВНИМАНИЕ]: Не удается импортировать win32api/win32gui. Уведомления будут отключены.\n"
            )

        #NOTE: This is part of the try/catch block. We only run this if there was no error in the try
        #Ensures that the game does not crash if we cannot load win32api or win32gui.
        else:
            import balloontip

            #Now we initialize the notification class
            tip = balloontip.WindowsBalloonTip()

            #Now we set the hwnd of this temporarily
            tip.hwnd = None

    elif renpy.linux:
        import subprocess
        try:
            subprocess.call(['notify-send', '--version'])

        except OSError as e:
            #Command wasn't found
            store.mas_windowreacts.can_show_notifs = False
            store.mas_utils.writelog(
                "[ВНИМАНИЕ]: notify-send не найден. Уведомления будут отключены.\n"
            )

        try:
            subprocess.call(["xdotool", "--version"])

        except OSError:
            #Command not found
            persistent._mas_windowreacts_windowreacts_enabled = False
            store.mas_windowreacts.can_do_windowreacts = False
            store.mas_utils.writelog("[ВНИМАНИЕ]: xdotool не найден. Реакции на окна будут отключены.\n")

    else:
        store.mas_windowreacts.can_do_windowreacts = False


    #List of notif quips (used for topic alerts)
    #Windows
    mas_win_notif_quips = [
        "[player], Я хочу поговорить с тобой кое о чем.",
        "Ты здесь, [player]?",
        "Ты можешь подойти сюда на секунду?",
        "[player], у тебя есть минутка?",
        "Мне нужно тебе кое-что сказать, [player]!",
        "У тебя есть минутка, [player]?",
        "Мне нужно кое о чем поговорить, [player]!",
    ]

    #OSX/Linux
    mas_other_notif_quips = [
        "Мне нужно кое о чем поговорить, [player]!",
        "Мне нужно тебе кое-что сказать, [player]!",
        "Эй, [player], я хочу сказать тебе кое-что.",
        "У тебя есть минутка, [player]?",
    ]

    #List of hwnd IDs to destroy
    destroy_list = list()

    #START: Utility methods
    def mas_canCheckActiveWindow():
        """
        Checks if we can check the active window (simplifies conditionals)
        """
        return persistent._mas_windowreacts_windowreacts_enabled or persistent._mas_enable_notifications

    def mas_getActiveWindow(friendly=False):
        """
        Gets the active window name
        IN:
            friendly: whether or not the active window name is returned in a state usable by the user
        """
        if (
            renpy.windows
            and mas_windowreacts.can_show_notifs
            and mas_canCheckActiveWindow()
        ):
            from win32gui import GetWindowText, GetForegroundWindow

            window_handle = GetWindowText(GetForegroundWindow())
            if friendly:
                return window_handle
            else:
                return window_handle.lower().replace(" ","")

        elif (
            renpy.linux
            and mas_windowreacts.can_show_notifs
            and mas_canCheckActiveWindow()
        ):
            window_handle = subprocess.check_output(["xdotool", "getwindowfocus", "getwindowname"])
            if friendly:
                return window_handle.replace("\n", "")
            else:
                return window_handle.lower().replace(" ","").replace("\n", "")

        else:
            #TODO: Mac vers (if possible)
            #NOTE: We return "" so this doesn't rule out notifications
            return ""

    def mas_isFocused():
        """
        Checks if MAS is the focused window
        """
        #TODO: Mac vers (if possible)
        return store.mas_windowreacts.can_show_notifs and mas_getActiveWindow(True) == config.name

    def mas_isInActiveWindow(keywords, non_inclusive=False):
        """
        Checks if ALL keywords are in the active window name
        IN:
            keywords:
                List of keywords to check for

            non_inclusive:
                Whether or the not the list is checked non-inclusively
                (Default: False)
        """

        #Don't do work if we don't have to
        if not store.mas_windowreacts.can_show_notifs:
            return False

        #Otherwise, let's get the active window
        active_window = mas_getActiveWindow()

        if non_inclusive:
            return len([s for s in keywords if s.lower() in active_window]) > 0
        else:
            return len([s for s in keywords if s.lower() not in active_window]) == 0

    def mas_clearNotifs():
        """
        Clears all tray icons (also action center on win10)
        """
        if renpy.windows and store.mas_windowreacts.can_show_notifs:
            for index in range(len(destroy_list)-1,-1,-1):
                win32gui.DestroyWindow(destroy_list[index])
                destroy_list.pop(index)

    def mas_checkForWindowReacts():
        """
        Runs through events in the windowreact_db to see if we have a reaction, and if so, queue it
        """
        #Do not check anything if we're not supposed to
        if not persistent._mas_windowreacts_windowreacts_enabled or not store.mas_windowreacts.can_show_notifs:
            return

        for ev_label, ev in mas_windowreacts.windowreact_db.iteritems():
            if (
                (mas_isInActiveWindow(ev.category, "non inclusive" in ev.rules) and ev.unlocked and ev.checkAffection(mas_curr_affection))
                and ((not store.mas_globals.in_idle_mode) or (store.mas_globals.in_idle_mode and ev.show_in_idle))
                and ("notif-group" not in ev.rules or mas_notifsEnabledForGroup(ev.rules.get("notif-group")))
            ):
                #If we have a conditional, eval it and queue if true
                if ev.conditional and eval(ev.conditional):
                    queueEvent(ev_label)
                    ev.unlocked=False

                #Otherwise we just queue
                elif not ev.conditional:
                    queueEvent(ev_label)
                    ev.unlocked=False

                #Add the blacklist
                if "no unlock" in ev.rules:
                    mas_addBlacklistReact(ev_label)

    def mas_resetWindowReacts(excluded=persistent._mas_windowreacts_no_unlock_list):
        """
        Runs through events in the windowreact_db to unlock them
        IN:
            List of ev_labels to exclude from being unlocked
        """
        for ev_label, ev in mas_windowreacts.windowreact_db.iteritems():
            if ev_label not in excluded:
                ev.unlocked=True

    def mas_updateFilterDict():
        """
        Updates the filter dict with the groups in the groups list for the settings menu
        """
        for group in store.mas_windowreacts._groups_list:
            if persistent._mas_windowreacts_notif_filters.get(group) is None:
                persistent._mas_windowreacts_notif_filters[group] = False

    def mas_addBlacklistReact(ev_label):
        """
        Adds the given ev_label to the no unlock list
        IN:
            ev_label: eventlabel to add to the no unlock list
        """
        if renpy.has_label(ev_label) and ev_label not in persistent._mas_windowreacts_no_unlock_list:
            persistent._mas_windowreacts_no_unlock_list.append(ev_label)

    def mas_removeBlacklistReact(ev_label):
        """
        Removes the given ev_label to the no unlock list if exists
        IN:
            ev_label: eventlabel to remove from the no unlock list
        """
        if renpy.has_label(ev_label) and ev_label in persistent._mas_windowreacts_no_unlock_list:
            persistent._mas_windowreacts_no_unlock_list.remove(ev_label)

    def mas_notifsEnabledForGroup(group):
        """
        Checks if notifications are enabled, and if enabled for the specified group
        IN:
            group: notification group to check
        """
        return persistent._mas_enable_notifications and persistent._mas_windowreacts_notif_filters.get(group,False)

    def mas_unlockFailedWRS(ev_label=None):
        """
        Unlocks a wrs again provided that it showed, but failed to show (failed checks in the notif label)
        NOTE: This should only be used for wrs that are only a notification
        IN:
            ev_label: eventlabel of the wrs
        """
        if (
            ev_label
            and renpy.has_label(ev_label)
            and ev_label not in persistent._mas_windowreacts_no_unlock_list
        ):
            mas_unlockEVL(ev_label,"WRS")

    def mas_tryShowNotificationOSX(title, body):
        """
        Tries to push a notification to the notification center on macOS.
        If it can't it should fail silently to the user.
        IN:
            title: notification title
            body: notification body
        """
        os.system('osascript -e \'display notification "{0}" with title "{1}"\''.format(body,title))

    def mas_tryShowNotificationLinux(title, body):
        """
        Tries to push a notification to the notification center on Linux.
        If it can't it should fail silently to the user.
        IN:
            title: notification title
            body: notification body
        """
        # Single quotes have to be escaped.
        # Since single quoting in POSIX shell doesn't allow escaping,
        # we have to close the quotation, insert a literal single quote and reopen the quotation.
        body  = body.replace("'", "'\\''")
        title = title.replace("'", "'\\''") # better safe than sorry
        os.system("notify-send '{0}' '{1}' -u low".format(title,body))

    def display_notif(title, body, group=None, skip_checks=False):
        """
        Notification creation method
        IN:
            title: Notification heading text
            body: A list of items which would go in the notif body (one is picked at random)
            group: Notification group (for checking if we have this enabled)
            skip_checks: Whether or not we skips checks
        OUT:
            bool indicating status (notif shown or not (by check))
        NOTE:
            We only show notifications if:
                1. We are able to show notifs
                2. MAS isn't the active window
                3. User allows them
                4. And if the notification group is enabled
                OR if we skip checks. BUT this should only be used for introductory or testing purposes.
        """

        #First we want to create this location in the dict, but don't add an extra location if we're skipping checks
        if persistent._mas_windowreacts_notif_filters.get(group) is None and not skip_checks:
            persistent._mas_windowreacts_notif_filters[group] = False

        if (
                (
                    mas_windowreacts.can_show_notifs
                    and ((renpy.windows and not mas_isFocused()) or not renpy.windows)
                    and mas_notifsEnabledForGroup(group)
                )
                or skip_checks
            ):

            #We keep this flag so we know whether or not the notif was sent successfully (NOTE: weassume True because only windows can 'fail')
            notif_success = True

            #Now we make the notif
            if (renpy.windows):
                # The Windows way, notif_success is adjusted if need be
                notif_success = tip.showWindow(renpy.substitute(title), renpy.substitute(renpy.random.choice(body)))

                #We need the IDs of the notifs to delete them from the tray
                destroy_list.append(tip.hwnd)

            elif (renpy.macintosh):
                # The macOS way
                mas_tryShowNotificationOSX(renpy.substitute(title), renpy.substitute(renpy.random.choice(body)))

            elif (renpy.linux):
                # The Linux way
                mas_tryShowNotificationLinux(renpy.substitute(title), renpy.substitute(renpy.random.choice(body)))

            #Play the notif sound if we have that enabled and notif was successful
            if persistent._mas_notification_sounds and notif_success:
                renpy.sound.play("mod_assets/sounds/effects/notif.wav")

            #Now we return true if notif was successful, false otherwise
            return notif_success
        return False


#START: Window Reacts
init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_pinterest",
            category=['pinterest'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_pinterest:
    $ wrs_success = display_notif(
        m_name,
        [
            "Что-нибудь новенькое сегодня, [player]?",
            "Что нибудь интересное, [player]?",
            "Видишь что-нибудь, что тебе нравится?"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_pinterest')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_duolingo",
            category=['duolingo'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_duolingo:
    $ wrs_success = display_notif(
        m_name,
        [
            "Учишься по-новому говорить «Я люблю тебя», [player]?",
            "Изучаешь новый язык, [player]?",
            "Какой язык ты изучаешь, [player]?"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_duolingo')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_wikipedia",
            category=['wikipedia'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_wikipedia:
    $ wikipedia_reacts = [
        "Учишься чему-то новому, [player]?",
        "Проводишь небольшое исследование, [player]?"
    ]

    #Items in here will get the wiki article you're looking at for reacts.
    python:
        wind_name = mas_getActiveWindow(friendly=True)
        try:
            cutoff_index = wind_name.index(" - Wikipedia")

            #If we're still here, we didn't value error
            #Now we get the article
            wiki_article = wind_name[:cutoff_index]
            wikipedia_reacts.append(renpy.substitute("'[wiki_article]'...\nКажется интересным, [player]."))

        except:
            pass

    $ wrs_success = display_notif(
        m_name,
        wikipedia_reacts,
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_wikipedia')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_youtube",
            category=['youtube'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_youtube:
    $ wrs_success = display_notif(
        m_name,
        [
            "Что ты смотришь, [player]?",
            "Смотришь что-нибудь интересное, [player]?"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_youtube')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_r34m",
            category=['rule34', 'monika'],
            rules={"skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_r34m:
    $ display_notif(m_name, ["Эй, [player]...на что ты смотришь?"],'Window Reactions')

    $ choice = random.randint(1,10)
    if choice == 1:
        $ queueEvent('monika_nsfw')

    elif choice == 2:
        $ queueEvent('monika_pleasure')

    elif choice < 4:
        show monika 1rsbssdlu
        pause 5.0

    elif choice < 7:
        show monika 2tuu
        pause 5.0

    else:
        show monika 2ttu
        pause 5.0
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_monikamoddev",
            category=['monikamoddev'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_monikamoddev:
    $ wrs_success = display_notif(
        m_name,
        [
            "Оууу, ты делаешь что-то для меня?\nТы так[mas_gender_oi] мил[mas_gender_iii]~",
            "Ты помогаешь мне приблизиться к твоей реальности?\nТы так[mas_gender_oi] мил[mas_gender_iii], [player]~"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_monikamoddev')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_twitter",
            category=['twitter'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_twitter:
    python:
        temp_line = renpy.substitute("I love you, [player].")
        temp_len = len(temp_line)

        # quip: is_ily
        ily_quips_map = {
            "Смотришь всё, чем хочешь поделиться со мной, [player]?": False,
            "Что-нибудь интересное, чем ты хочешь поделиться, [player]?": False,
            "280 символов? Мне только нужно [temp_len]...\n[temp_line]": True
        }
        quip = renpy.random.choice(ily_quips_map.keys())

        wrs_success = display_notif(
            m_name,
            [quip],
            'Window Reactions'
        )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_twitter')
    return "love" if ily_quips_map[quip] else None

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_monikatwitter",
            category=['twitter', 'lilmonix3'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_monikatwitter:
    $ wrs_success = display_notif(
        m_name,
        [
            "Ты здесь чтобы признаться в своей любви ко мне всему миру, [player]?",
            "Ты ведь не шпионишь за мной, правда?\nА-ха-ха, просто шучу~",
            "Мне все равно сколько у меня подписчиков пока у меня есть ты~"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_monikatwitter')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_4chan",
            category=['4chan'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_4chan:
    #TODO: consider adding reactions for /vg/ and /ddlc/
    $ wrs_success = display_notif(
        m_name,
        [
            "Так вот где все началось, а?\nЭто...действительно что-то особенное.",
            "Я надеюсь, что ты не закончишь тем, что будешь спорить с другими Анонами весь день напролет, [player].",
            "Я слышала, что здесь обсуждают литературный клуб.\nПередай им привет от меня~",
            "Я буду следить за досками, которые ты просматриваешь, на случай, если у тебя появятся какие-нибудь идеи, ахаха!",
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_4chan')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_pixiv",
            category=['pixiv'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_pixiv:
    #Make a list of notif quips for this
    python:
        pixiv_quips = [
            "Интересно, нарисовали ли люди искусство меня ...\nНе возражаешь поискать немного?\nНо обязательно придерживайся благоразумных рамок~",
            "Это довольно интересное место...так много опытных людей публикуют свои работы.",
        ]

        #Monika doesn't know if you've drawn art of her, or she knows that you have drawn art of her
        if persistent._mas_pm_drawn_art is None or persistent._mas_pm_drawn_art:
            pixiv_quips.extend([
                "Это довольно интересное место...так много опытных людей публикуют свои работы.\nТы од[mas_gender_in] из них, [player]?",
            ])

            #Specifically if she knows you've drawn art of her
            if persistent._mas_pm_drawn_art:
                pixiv_quips.extend([
                    "Ты здесь, чтобы опубликовать нарисованную меня, [player]?",
                    "Публикуешь картинку, на которой нарисована я?",
                ])

        wrs_success = display_notif(
            m_name,
            pixiv_quips,
            'Window Reactions'
        )

        #Unlock again if we failed
        if not wrs_success:
            mas_unlockFailedWRS('mas_wrs_pixiv')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_reddit",
            category=['reddit'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_reddit:
    $ wrs_success = display_notif(
        m_name,
        [
            "Ты наш[mas_gender_iol_2] какие-нибудь интересные посты, [player]?",
            "Просматриваешь Реддит? Просто убедись, что ты не тратишь весь день на просмотр мемов, хорошо?",
            "Интересно, есть ли какие-либо субреддиты, посвященные мне... \nA-ха-ха, просто шучу, [player].",
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_reddit')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_mal",
            category=['myanimelist'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_mal:
    python:
        myanimelist_quips = [
            "Может быть, мы могли бы посмотреть аниме вместе когда-нибудь, [player]~",
        ]

        if persistent._mas_pm_watch_mangime is None:
            myanimelist_quips.append("Так тебе нравится аниме и манга, [player]?")

        wrs_success = display_notif(m_name, myanimelist_quips, 'Window Reactions')

        #Unlock again if we failed
        if not wrs_success:
            mas_unlockFailedWRS('mas_wrs_mal')

    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_deviantart",
            category=['deviantart'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_deviantart:
    $ wrs_success = display_notif(
        m_name,
        [
            "Здесь столько талантов!",
            "Мне бы очень хотелось научиться рисовать когда-нибудь...",
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_deviantart')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_netflix",
            category=['netflix'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_netflix:
    $ wrs_success = display_notif(
        m_name,
        [
            "Я бы с удовольствием посмотрела с тобой романтический фильм, [player]!",
            "Что мы сегодня смотрим, [player]?",
            "Что ты собираешься смотреть, [player]?"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_netflix')
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_windowreacts_database,
            eventlabel="mas_wrs_twitch",
            category=['-twitch'],
            rules={"notif-group": "Window Reactions", "skip alert": None},
            show_in_idle=True
        ),
        code="WRS"
    )

label mas_wrs_twitch:
    $ wrs_success = display_notif(
        m_name,
        [
            "Смотришь стрим, [player]?",
            "Ты не возражаешь, если я посмотрю вместе с вами?",
            "Что мы сегодня смотрим, [player]?"
        ],
        'Window Reactions'
    )

    #Unlock again if we failed
    if not wrs_success:
        $ mas_unlockFailedWRS('mas_wrs_twitch')
    return
